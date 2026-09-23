import os
import re
import json
import time

import networkx as nx
from networkx.readwrite import json_graph

from services.llm_service import groq_model


# =========================================================
# Graph Storage
# =========================================================
# In-process Graph RAG: relationships between entities
# (people, roles, services, pillars, categories, documents)
# are modeled as a small NetworkX graph built at ingestion
# time and persisted to a local JSON file. No external graph
# database is required.

GRAPH_STORE_PATH = os.path.join(
    "rag",
    "graph_store.json"
)

_STOP_WORDS = {

    "who", "what", "which", "show", "tell", "about", "of",
    "the", "is", "are", "does", "do", "and", "for", "with",
    "accion", "labs"
}


class _DailyQuotaExhausted(Exception):
    """Groq's per-day token quota (not the per-minute one) is
    exhausted - won't clear for minutes to hours, so callers
    should stop the whole extraction batch rather than retry."""
    pass


# =========================================================
# Person Extraction (LLM-based)
# =========================================================
# A regex heuristic ("a short line starting with a capital
# letter") was tried first, but on this dataset's unstructured
# PDF/JSON marketing text it mostly picked up sentence
# fragments and category labels as "people" (e.g. "Category:
# Capabilities", "We implement centralized..."). Real named-
# entity extraction needs actual language understanding, so
# this uses the LLM instead - but only on chunks that look
# like they might mention a person/role at all, via a cheap
# keyword pre-filter, to avoid an LLM call per chunk (most of
# which are service/product descriptions with no people in
# them at all).

_LEADERSHIP_KEYWORDS = [
    "ceo", "chief executive", "chief technology", "chief financial",
    "chief operating", "cto", "cfo", "coo", "founder", "co-founder",
    "president", "vice president", "vp ", "director", "chairman",
    "chairwoman", "chairperson", "managing director",
    "board of directors", "board member", "head of", "svp", "evp"
]


def _looks_like_leadership_content(text):

    lower = (text or "").lower()

    return any(keyword in lower for keyword in _LEADERSHIP_KEYWORDS)


def _extract_people_from_text(text, source):

    prompt = f"""
You are extracting named people and their job titles from a
company's website/document text, for a knowledge graph.

Only extract REAL individual people's full names that are
explicitly associated with a role, title, or position (e.g.
CEO, Founder, Managing Director, Board Member, VP, Chairman,
Head of X).

Do NOT extract:
- Category labels, section headings, or generic phrases
- Company, product, or service names
- Sentence fragments that are not real personal names
- Anything you are not confident is an actual person's name

Return ONLY a valid JSON array (no other text, no markdown
fences). Each item: {{"name": "...", "role": "..."}}.
If no real people with roles are found, return: []

Text:
{text[:2000]}

JSON:
"""

    # Groq's free tier has a tokens-per-minute cap, which a long
    # run of back-to-back extraction calls can hit. One retry
    # after a short pause clears a transient 429 without having
    # to slow every single call down with a fixed delay.
    for attempt in range(2):

        try:

            response = groq_model.invoke(prompt)

            raw = response.content.strip()

            # Strip markdown code fences some models wrap JSON in.
            raw = re.sub(r"^```(json)?", "", raw, flags=re.IGNORECASE).strip()

            raw = re.sub(r"```$", "", raw).strip()

            people = json.loads(raw)

            if not isinstance(people, list):

                return []

            results = []

            for item in people:

                name = str(item.get("name", "")).strip()

                role = str(item.get("role", "")).strip()

                if name and 2 <= len(name.split()) <= 5:

                    results.append({

                        "name": name,

                        "role": role,

                        "source": source
                    })

            return results

        except Exception as e:

            error_text = str(e).lower()

            # A per-minute rate limit clears itself in seconds, so
            # one short retry is worth it. A per-*day* quota won't
            # clear for minutes to hours - retrying that is just
            # wasted time, and raising here lets the batch loop
            # below stop entirely instead of failing the same way
            # against every remaining candidate.
            if "tokens per day" in error_text or "tpd" in error_text:

                raise _DailyQuotaExhausted(str(e))

            is_rate_limited = "rate_limit" in error_text or "429" in error_text

            if is_rate_limited and attempt == 0:

                time.sleep(3)

                continue

            print(f"Graph RAG: person extraction failed for {source}: {e}")

            return []


def _candidate_priority(doc):

    """
    Lower number = processed first. Dedicated bio/leadership
    pages and PDFs are far more likely to yield a real person
    than a blog or news article that just happens to mention a
    title in passing - and the LLM extraction budget (Groq's
    daily token quota) is limited, so the highest-value content
    should be spent on first, in case the quota runs out before
    reaching the rest.
    """

    source = ((doc.metadata or {}).get("source") or "").lower()

    if source.endswith(".pdf"):

        return 0

    if "/blogs/" in source or "/news/" in source:

        return 2

    return 1


def extract_people_llm(documents):

    candidates = [

        doc for doc in documents

        if _looks_like_leadership_content(doc.page_content)
    ]

    candidates.sort(key=_candidate_priority)

    print(

        f"Graph RAG: {len(candidates)} of {len(documents)} chunks "
        f"look like leadership content, running LLM extraction..."
    )

    people = []

    for i, doc in enumerate(candidates):

        source = (doc.metadata or {}).get("source", "")

        try:

            people.extend(
                _extract_people_from_text(doc.page_content, source)
            )

        except _DailyQuotaExhausted as e:

            print(

                f"Graph RAG: Groq's daily token quota is "
                f"exhausted after {i}/{len(candidates)} candidates "
                f"- stopping extraction early with what was found "
                f"so far ({len(people)} people). {e}"
            )

            break

    return people


# =========================================================
# Build Graph From Documents
# =========================================================
def build_graph(documents):

    """
    Build a directed graph of entity relationships from the
    knowledge base documents' metadata:

        source --BELONGS_TO--> category
        category --HAS_PILLAR--> pillar
        pillar --INCLUDES_SERVICE--> service
        person --HAS_ROLE--> role
        person --MENTIONED_IN--> source
    """

    graph = nx.DiGraph()

    for doc in documents:

        metadata = doc.metadata or {}

        source = metadata.get("source")

        category = metadata.get("category")

        pillar = metadata.get("pillar")

        service = metadata.get("service")

        if source:

            graph.add_node(source, kind="document")

            if category:

                graph.add_node(category, kind="category")

                graph.add_edge(
                    source,
                    category,
                    relation="BELONGS_TO"
                )

        if category and pillar:

            graph.add_node(pillar, kind="pillar")

            graph.add_edge(
                category,
                pillar,
                relation="HAS_PILLAR"
            )

        if pillar and service:

            graph.add_node(service, kind="service")

            graph.add_edge(
                pillar,
                service,
                relation="INCLUDES_SERVICE"
            )

    # =====================================================
    # People / Leadership Relationships (LLM-extracted)
    # =====================================================
    for person in extract_people_llm(documents):

        name = person["name"]

        role = person["role"]

        source = person["source"]

        graph.add_node(name, kind="person")

        if role:

            graph.add_node(role, kind="role")

            graph.add_edge(
                name,
                role,
                relation="HAS_ROLE"
            )

        if source:

            graph.add_edge(
                name,
                source,
                relation="MENTIONED_IN"
            )

    return graph


# =========================================================
# Persistence
# =========================================================
def save_graph(graph, path=GRAPH_STORE_PATH):

    data = json_graph.node_link_data(graph, edges="edges")

    os.makedirs(
        os.path.dirname(path) or ".",
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as f:

        json.dump(data, f)


def load_graph(path=GRAPH_STORE_PATH):

    if not os.path.exists(path):

        return None

    try:

        with open(path, "r", encoding="utf-8") as f:

            data = json.load(f)

        return json_graph.node_link_graph(
            data,
            directed=True,
            edges="edges"
        )

    except Exception as e:

        print(f"Graph RAG: failed to load graph store: {e}")

        return None


def build_and_save_graph(documents, path=GRAPH_STORE_PATH):

    graph = build_graph(documents)

    save_graph(graph, path)

    print(
        f"Graph RAG: built graph with {graph.number_of_nodes()} "
        f"nodes and {graph.number_of_edges()} edges"
    )

    return graph


# =========================================================
# Lazy-loaded singleton graph used at query time
# =========================================================
_graph_cache = None

_graph_loaded = False


def _get_graph():

    global _graph_cache, _graph_loaded

    if not _graph_loaded:

        _graph_cache = load_graph()

        _graph_loaded = True

    return _graph_cache


_RELATION_TEXT = {

    "BELONGS_TO": "belongs to",
    "HAS_PILLAR": "has the pillar",
    "INCLUDES_SERVICE": "includes the service",
    "HAS_ROLE": "holds the role of",
    "MENTIONED_IN": "is mentioned in"
}


def _query_words(query):

    return [

        w for w in re.findall(r"\w+", query.lower())

        if len(w) > 2 and w not in _STOP_WORDS
    ]


# =========================================================
# Relationship Context For RAG Prompt
# =========================================================
def get_relationship_context(query, max_related=8):

    """
    Find graph nodes related to the query and describe their
    relationships in natural language, for use as extra
    context in the RAG prompt. Returns "" if no graph has been
    built yet, or nothing relevant is found.
    """

    graph = _get_graph()

    if graph is None or graph.number_of_nodes() == 0:

        return ""

    words = _query_words(query)

    if not words:

        return ""

    matched_nodes = []

    for node in graph.nodes:

        node_lower = str(node).lower()

        if any(word in node_lower for word in words):

            matched_nodes.append(node)

    if not matched_nodes:

        return ""

    lines = []

    seen = set()

    for node in matched_nodes:

        for _, target, data in graph.out_edges(node, data=True):

            relation = data.get("relation", "RELATED_TO")

            phrase = (
                f"{node} "
                f"{_RELATION_TEXT.get(relation, relation)} "
                f"{target}."
            )

            if phrase not in seen:

                seen.add(phrase)

                lines.append(phrase)

        for source, _, data in graph.in_edges(node, data=True):

            relation = data.get("relation", "RELATED_TO")

            phrase = (
                f"{source} "
                f"{_RELATION_TEXT.get(relation, relation)} "
                f"{node}."
            )

            if phrase not in seen:

                seen.add(phrase)

                lines.append(phrase)

        if len(lines) >= max_related:

            break

    if not lines:

        return ""

    return (
        "Known Relationships:\n"
        + "\n".join(lines[:max_related])
    )

from services.llm_service import generate_llm_response
from services.media_service import extract_media_assets

from vector_db.pinecone_client import vector_store

import re


# =========================================================
# Main RAG Response Function
# =========================================================
async def get_rag_response(query: str):

    try:

        # =====================================================
        # Detect Board/Leadership Queries
        # =====================================================

        board_keywords=[

            "board",
            "directors",
            "leadership",
            "leader",
            "director",
            "members",
            "team",
            "ceo",
            "founder",
            "executive"

        ]

        is_board_query=any(

            word in query.lower()

            for word in board_keywords
        )


        # =====================================================
        # Dynamic Retrieval
        # =====================================================

        retrieval_k=15

        if is_board_query:

            retrieval_k=100


        docs=vector_store.similarity_search(

            query,

            k=retrieval_k
        )


        # =====================================================
        # Force leadership retrieval
        # =====================================================

        if is_board_query:

            leadership_queries=[

                "Board of Directors",
                "Board Members",
                "Leadership Team",
                "Executive Leadership",
                "Leadership Accion Labs",
                "Directors",
                "Managing Director",
                "Chairman",
                "CEO"

            ]

            additional_docs=[]

            for q in leadership_queries:

                try:

                    temp=vector_store.similarity_search(
                        q,
                        k=20
                    )

                    additional_docs.extend(
                        temp
                    )

                except Exception as e:

                    print(
                        f"leadership search failed:{e}"
                    )


            docs.extend(
                additional_docs
            )


            # remove duplicates

            unique=[]

            seen=set()


            for d in docs:

                key=(

                    d.page_content[:400]

                    if d.page_content

                    else ""

                )

                if key not in seen:

                    seen.add(key)

                    unique.append(d)

            docs=unique




        # =====================================================
        # Extra Retrieval
        # =====================================================

        if is_board_query:

            extra_docs=[]

            board_queries=[

                "Board of Directors",
                "leadership team",
                "executive leadership",
                "CEO",
                "Founder",
                "Managing Director",
                "leadership Accion Labs",
                "board members"

            ]


            for q in board_queries:

                try:

                    additional=vector_store.similarity_search(
                        q,
                        k=10
                    )

                    extra_docs.extend(
                        additional
                    )

                except Exception as e:

                    print(
                        f"Extra retrieval failed:{e}"
                    )


            docs.extend(
                extra_docs
            )


            # =================================================
            # Remove duplicates
            # =================================================

            unique_docs=[]

            seen=set()

            for d in docs:

                key=(

                    d.page_content[:250]

                    if d.page_content

                    else ""

                )

                if key not in seen:

                    seen.add(key)

                    unique_docs.append(d)

            docs=unique_docs


        # =====================================================
        # No docs
        # =====================================================

        if not docs:

            return {

                "answer":"No relevant information found.",

                "images":[],

                "videos":[],

                "pdfs":[],

                "links":[],

                "cards":[],

                "sources":[],

                "metadata":{}
            }


        # =====================================================
        # Build Context
        # =====================================================

        context_chunks=[]

        director_cards=[]

        seen_people=set()


        for doc in docs:

            metadata=doc.metadata or {}

            text=doc.page_content or ""


            if text:

                context_chunks.append(
                    text
                )


            # =================================================
            # Dynamic Person Extraction
            # =================================================

            if is_board_query:

                name=metadata.get(
                    "title",
                    ""
                )

                image=metadata.get(
                    "image",
                    ""
                )

                linkedin=metadata.get(
                    "link",
                    ""
                )

                designation=metadata.get(
                    "designation",
                    ""
                )


                if not name:

                    lines=[

                        x.strip()

                        for x in text.split("\n")

                        if x.strip()

                    ]


                    for line in lines:

                        words=line.split()

                        if (

                            len(words)>=2

                            and

                            len(words)<=5

                            and

                            words[0][0].isupper()

                        ):

                            name=line

                            break


                lower=text.lower()


                if not designation:

                    if "chief executive officer" in lower:

                        designation="CEO"

                    elif "founder" in lower:

                        designation="Founder"

                    elif "vice president" in lower:

                        designation="Vice President"

                    elif "chairman" in lower:

                        designation="Chairman"

                    elif "managing director" in lower:

                        designation="Managing Director"

                    elif "board" in lower:

                        designation="Board Member"

                    else:

                        designation="Leadership"


                if (

                    name

                    and

                    len(name.split())<=5

                    and

                    name not in seen_people

                ):

                    seen_people.add(
                        name
                    )

                    # ==============================================
                    # Clean Interactive Description
                    # ==============================================

                    clean_text=text[:600]

                    clean_text=clean_text.replace(
                        "Not specified.",
                        ""
                    )

                    clean_text=clean_text.replace(
                        "Role:",
                        ""
                    )

                    clean_text=clean_text.replace(
                        "Summary:",
                        ""
                    )

                    clean_text=clean_text.replace(
                        "Experience:",
                        ""
                    )

                    clean_text=" ".join(
                        clean_text.split()
                    )


                    # ==============================================
                    # Dynamic image fallback
                    # ==============================================

                    if not image:

                        media=extract_media_assets(
                            docs
                        )

                        possible=media.get(
                            "images",
                            []
                        )

                        cleaned_name=name.lower()

                        cleaned_name=cleaned_name.replace(
                            " ",
                            "_"
                        )


                        for img in possible:

                            lower=img.lower()

                            if (

                                cleaned_name in lower

                                or

                                cleaned_name.replace(
                                    "_",
                                    "-"
                                ) in lower

                                or

                                name.split()[0].lower()
                                in lower

                            ):

                                image=img

                                break


                    director_cards.append({

                        "title":name,

                        "subtitle":designation,

                        "description":clean_text,

                        "image":image,

                        "link":linkedin

                    })


        # =====================================================
        # Final Context
        # =====================================================

        context="\n\n".join(
            context_chunks
        )


        # =====================================================
        # Prompt
        # =====================================================

        prompt=f"""
You are InsightHost.

Answer ONLY from context.

Rules:

- Never hallucinate
- Never show image URLs
- Never say "Not specified"
- Never repeat Role Summary Experience labels
- Make responses natural and conversational
- For leadership use concise human descriptions
Name
Role
Summary
Experience

Context:

{context}

Question:

{query}

"""


        # =====================================================
        # LLM
        # =====================================================

        llm_response=await generate_llm_response(
            prompt
        )


        answer=llm_response.get(

            "answer",

            "No response"
        )


        model_used=llm_response.get(

            "model",

            "unknown"
        )


        # =====================================================
        # Media extraction
        # =====================================================

        media_assets=extract_media_assets(
            docs
        )


        filtered_images=[]

        filtered_videos=[]

        filtered_links=[]


        query_lower=query.lower()


        for img in media_assets.get(
            "images",
            []
        ):

            filename=img.split("/")[-1]

            cleaned=filename.lower()

            cleaned=cleaned.replace(
                "_",
                " "
            )


            if any(

                word in cleaned

                for word in query_lower.split()

            ):

                filtered_images.append(
                    img
                )


        for vid in media_assets.get(
            "videos",
            []
        ):

            filename=vid.split("/")[-1]

            cleaned=filename.lower()

            if any(

                word in cleaned

                for word in query_lower.split()

            ):

                filtered_videos.append(
                    vid
                )


        for link in media_assets.get(
            "links",
            []
        ):

            if any(

                word in link.lower()

                for word in query_lower.split()

            ):

                filtered_links.append(
                    link
                )


        # =====================================================
        # NO INFO => NO MEDIA
        # =====================================================

        if (

            "couldn't find" in answer.lower()

            or

            "no information" in answer.lower()

        ):

            filtered_images=[]

            filtered_videos=[]

            filtered_links=[]


        elif not filtered_images:

            filtered_images=media_assets.get(
                "images",
                []
            )

            filtered_videos=media_assets.get(
                "videos",
                []
            )

            filtered_links=media_assets.get(
                "links",
                []
            )


        # =====================================================
        # Final Response
        # =====================================================

        return {

            "answer":answer,

            "images":filtered_images,

            "videos":filtered_videos,

            "pdfs":
            media_assets.get(
                "pdfs",
                []
            ),

            "links":filtered_links,

            "cards":

            director_cards

            if is_board_query

            else

            media_assets.get(
                "cards",
                []
            ),

            "sources":
            media_assets.get(
                "sources",
                []
            ),

            "metadata":{

                "model":model_used,

                "retrieved_docs":len(docs),

                "query":query,

                "leadership":is_board_query

            }

        }


    except Exception as e:

        print(
            f"RAG Chain Error:{e}"
        )

        return {

            "answer":
            "Sorry, I encountered an error.",

            "images":[],

            "videos":[],

            "pdfs":[],

            "links":[],

            "cards":[],

            "sources":[],

            "metadata":{}
        }
import os
import json
import pandas as pd

from pypdf import PdfReader
from docx import Document as DocxDocument

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.web_scraper import load_web_documents


# =========================================================
# Base Knowledge Path
# =========================================================
DATA_PATH = "knowledge_base"

DOCUMENTS_PATH = os.path.join(DATA_PATH, "documents")
JSON_PATH = os.path.join(DATA_PATH, "json")
CSV_PATH = os.path.join(DATA_PATH, "csv")
PDF_PATH = os.path.join(DATA_PATH, "pdfs")

IMAGES_PATH = os.path.join(DATA_PATH, "images")
VIDEOS_PATH = os.path.join(DATA_PATH, "videos")

CAPTIONS_CACHE_PATH = os.path.join(
    DATA_PATH,
    "media_captions_cache.json"
)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

VIDEO_EXTENSIONS = (".mp4", ".mov", ".webm")


# =========================================================
# Captions/Summaries Cache
# =========================================================
# Captioning images and summarizing videos calls the Gemini
# API, so results are cached to disk to avoid re-calling it
# (and re-incurring cost/latency) every time ingestion runs.

def _load_captions_cache():

    if not os.path.exists(CAPTIONS_CACHE_PATH):

        return {}

    try:

        with open(CAPTIONS_CACHE_PATH, "r", encoding="utf-8") as f:

            return json.load(f)

    except Exception as e:

        print(f"Error loading media captions cache: {e}")

        return {}


def _save_captions_cache(cache):

    try:

        with open(CAPTIONS_CACHE_PATH, "w", encoding="utf-8") as f:

            json.dump(cache, f)

    except Exception as e:

        print(f"Error saving media captions cache: {e}")


def _caption_image(image_path):

    from PIL import Image

    from services.llm_service import gemini_model

    image = Image.open(image_path)

    response = gemini_model.generate_content([

        image,

        (
            "Describe this image in one concise sentence for a "
            "company knowledge base. Focus on who or what is "
            "shown."
        )
    ])

    return response.text.strip()


# =========================================================
# Helper Functions
# =========================================================
def find_related_image(file_stem):

    if os.path.exists(IMAGES_PATH):

        for image_file in os.listdir(IMAGES_PATH):

            if image_file.startswith(file_stem):

                return f"/media/images/{image_file}"

    return ""


def find_related_video(file_stem):

    if os.path.exists(VIDEOS_PATH):

        for video_file in os.listdir(VIDEOS_PATH):

            if video_file.startswith(file_stem):

                return f"/media/videos/{video_file}"

    return ""


# =========================================================
# Multimodal RAG: Image Captions + Video Summaries
# =========================================================
# Images and videos are otherwise only discoverable by
# filename substring matching (see media_service.py). To make
# them semantically searchable through the vector store too,
# each image is captioned and each video summarized once
# (Gemini), and the result is embedded as its own retrievable
# document.

def load_media_documents():

    media_documents = []

    captions_cache = _load_captions_cache()

    cache_dirty = False

    # =====================================================
    # Images
    # =====================================================
    if os.path.exists(IMAGES_PATH):

        for image_file in os.listdir(IMAGES_PATH):

            if not image_file.lower().endswith(IMAGE_EXTENSIONS):

                continue

            cache_key = f"image:{image_file}"

            caption = captions_cache.get(cache_key)

            if not caption:

                try:

                    caption = _caption_image(
                        os.path.join(IMAGES_PATH, image_file)
                    )

                    captions_cache[cache_key] = caption

                    cache_dirty = True

                except Exception as e:

                    print(
                        f"Error captioning image {image_file}: {e}"
                    )

                    continue

            if caption:

                media_documents.append(
                    Document(
                        page_content=f"Image: {caption}",

                        metadata={

                            "source": image_file,

                            "type": "image",

                            "image": f"/media/images/{image_file}",

                            "video": "",

                            "pdf": "",

                            "link": ""
                        }
                    )
                )

    # =====================================================
    # Videos
    # =====================================================
    if os.path.exists(VIDEOS_PATH):

        from services.video_service import summarize_video_sync

        for video_file in os.listdir(VIDEOS_PATH):

            if not video_file.lower().endswith(VIDEO_EXTENSIONS):

                continue

            cache_key = f"video:{video_file}"

            summary = captions_cache.get(cache_key)

            if not summary:

                try:

                    summary = summarize_video_sync(
                        os.path.join(VIDEOS_PATH, video_file)
                    )

                    captions_cache[cache_key] = summary

                    cache_dirty = True

                except Exception as e:

                    print(
                        f"Error summarizing video {video_file}: {e}"
                    )

                    continue

            if summary:

                media_documents.append(
                    Document(
                        page_content=f"Video: {summary}",

                        metadata={

                            "source": video_file,

                            "type": "video",

                            "image": "",

                            "video": f"/media/videos/{video_file}",

                            "pdf": "",

                            "link": ""
                        }
                    )
                )

    if cache_dirty:

        _save_captions_cache(captions_cache)

    print(
        f"Captioned/summarized {len(media_documents)} media files"
    )

    return media_documents


# =========================================================
# Load Documents
# =========================================================
def load_documents(include_web=True, max_web_pages=None, include_media=True):

    documents = []

    # =====================================================
    # TEXT FILES
    # =====================================================
    if os.path.exists(DOCUMENTS_PATH):

        for file_name in os.listdir(DOCUMENTS_PATH):

            file_path = os.path.join(
                DOCUMENTS_PATH,
                file_name
            )

            try:

                if file_name.lower().endswith(".txt"):

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        text = f.read().strip()

                        if text:

                            file_stem = os.path.splitext(
                                file_name
                            )[0]

                            image = find_related_image(
                                file_stem
                            )

                            video = find_related_video(
                                file_stem
                            )

                            documents.append(
                                Document(
                                    page_content=text,

                                    metadata={

                                        "source": file_name,

                                        "title": file_stem,

                                        "type": "text",

                                        "image": image or "",

                                        "video": video or "",

                                        "pdf": "",

                                        "link": ""
                                    }
                                )
                            )

            except Exception as e:

                print(f"Error loading TXT {file_name}: {e}")

    # =====================================================
    # JSON FILES
    # =====================================================
    if os.path.exists(JSON_PATH):

        for file_name in os.listdir(JSON_PATH):

            file_path = os.path.join(
                JSON_PATH,
                file_name
            )

            try:

                if file_name.lower().endswith(".json"):

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                        if isinstance(data, list):

                            for item in data:

                                category = item.get(
                                    "category", ""
                                )

                                pillar = item.get(
                                    "pillar", ""
                                )

                                service = item.get(
                                    "service", ""
                                )

                                content = item.get(
                                    "content", ""
                                )

                                source = item.get(
                                    "source",
                                    file_name
                                )

                                image = item.get(
                                    "image",
                                    ""
                                )

                                video = item.get(
                                    "video",
                                    ""
                                )

                                pdf = item.get(
                                    "pdf",
                                    ""
                                )

                                link = item.get(
                                    "link",
                                    ""
                                )

                                text = f"""
Category: {category}
Pillar: {pillar}
Service: {service}

{content}
""".strip()

                                if text:

                                    documents.append(
                                        Document(
                                            page_content=text,

                                            metadata={
                                                "category": category,

                                                "pillar": pillar,

                                                "service": service,

                                                "source": source,

                                                "type": "json",

                                                "image": image or "",

                                                "video": video or "",

                                                "pdf": pdf or "",

                                                "link": link or ""
                                            }
                                        )
                                    )

            except Exception as e:

                print(f"Error loading JSON {file_name}: {e}")

    # =====================================================
    # PDF FILES
    # =====================================================
    if os.path.exists(PDF_PATH):

        for file_name in os.listdir(PDF_PATH):

            file_path = os.path.join(
                PDF_PATH,
                file_name
            )

            try:

                if file_name.lower().endswith(".pdf"):

                    reader = PdfReader(file_path)

                    for page in reader.pages:

                        text = page.extract_text()

                        if text:

                            documents.append(
                                Document(
                                    page_content=text.strip(),

                                    metadata={

                                        "source": file_name,

                                        "type": "pdf",

                                        "image": "",

                                        "video": "",

                                        "pdf":
                                        f"/media/pdfs/{file_name}",

                                        "link": ""
                                    }
                                )
                            )

            except Exception as e:

                print(f"Error loading PDF {file_name}: {e}")

    # =====================================================
    # CSV FILES
    # =====================================================
    if os.path.exists(CSV_PATH):

        for file_name in os.listdir(CSV_PATH):

            file_path = os.path.join(
                CSV_PATH,
                file_name
            )

            try:

                if file_name.lower().endswith(".csv"):

                    df = pd.read_csv(
                        file_path,
                        on_bad_lines="skip"
                    )

                    for _, row in df.iterrows():

                        text = " ".join(
                            map(str, row.values)
                        ).strip()

                        if text:

                            documents.append(
                                Document(
                                    page_content=text,

                                    metadata={

                                        "source": file_name,

                                        "type": "csv",

                                        "image":"",

                                        "video":"",

                                        "pdf":"",

                                        "link":""
                                    }
                                )
                            )

            except Exception as e:

                print(f"Error loading CSV {file_name}: {e}")

    # =====================================================
    # WEB PAGES (accionlabs.com, via sitemap)
    # =====================================================
    if include_web:

        try:

            documents.extend(
                load_web_documents(max_pages=max_web_pages)
            )

        except Exception as e:

            print(f"Error loading web pages: {e}")

    # =====================================================
    # Chunking
    # =====================================================
    print(f"Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_documents = splitter.split_documents(
        documents
    )

    print(f"Created {len(split_documents)} chunks")

    # =====================================================
    # Multimodal RAG: append image/video documents as-is
    # (already short, so they are not re-chunked)
    # =====================================================
    if include_media:

        media_documents = load_media_documents()

        split_documents.extend(media_documents)

    return split_documents
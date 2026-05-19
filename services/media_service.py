import re
import os


# =========================================================
# Media Folders
# =========================================================

IMAGE_FOLDER = "knowledge_base/images"
VIDEO_FOLDER = "knowledge_base/videos"


# =========================================================
# Normalize Text
# =========================================================

def normalize_text(text):

    return (
        text.lower()
        .replace("_"," ")
        .replace("-"," ")
        .replace("/"," ")
        .replace("("," ")
        .replace(")"," ")
        .replace(","," ")
        .strip()
    )


# =========================================================
# Convert YouTube URL to EMBED
# =========================================================

def convert_youtube_embed(url):

    try:

        if "youtu.be/" in url:

            video_id=(
                url.split("youtu.be/")[1]
                .split("?")[0]
            )

            return(
                f"https://www.youtube.com/embed/"
                f"{video_id}"
                f"?autoplay=1&mute=1"
            )


        elif "youtube.com/watch?v=" in url:

            video_id=(
                url.split("watch?v=")[1]
                .split("&")[0]
            )

            return(
                f"https://www.youtube.com/embed/"
                f"{video_id}"
                f"?autoplay=1&mute=1"
            )

    except:

        pass

    return url


# =========================================================
# Match Local Media By Text
# =========================================================

def find_local_media(

    text,

    intent=None,

    entities=None

):
    entities = entities or []

    text=normalize_text(text)

    image_scores=[]

    video_scores=[]


    # ==========================================
    # Images
    # ==========================================

    if os.path.exists(
        IMAGE_FOLDER
    ):

        for file in os.listdir(
            IMAGE_FOLDER
        ):

            clean_name=(

                file.lower()
                .replace("_"," ")
                .replace("-"," ")
                .rsplit(".",1)[0]

            )

            clean_name=normalize_text(
                clean_name
            )

            words=clean_name.split()

            score=sum(

                1 for w in words

                if w in text

            )

            if score>0:

                image_scores.append({

                    "score":score,

                    "path":
                    f"/media/images/{file}"

                })


    # ==========================================
    # Videos
    # ==========================================

    if os.path.exists(
        VIDEO_FOLDER
    ):

        for file in os.listdir(
            VIDEO_FOLDER
        ):

            clean_name=(

                file.lower()
                .replace("_"," ")
                .replace("-"," ")
                .rsplit(".",1)[0]

            )

            clean_name=normalize_text(
                clean_name
            )

            words=clean_name.split()

            score=sum(

                1 for w in words

                if w in text

            )

            if score>0:

                video_scores.append({

                    "score":score,

                    "path":
                    f"/media/videos/{file}"

                })


    # ==========================================
    # Sort relevance
    # ==========================================

    image_scores=sorted(

        image_scores,

        key=lambda x:x["score"],

        reverse=True

    )


    video_scores=sorted(

        video_scores,

        key=lambda x:x["score"],

        reverse=True

    )


    matched_images=[

        x["path"]

        for x in image_scores[:20]

    ]


    matched_videos=[

        x["path"]

        for x in video_scores[:1]

    ]


    return(

        list(dict.fromkeys(
            matched_images
        )),

        list(dict.fromkeys(
            matched_videos
        ))
    )



# =====================================================
# Main Extraction
# =====================================================

def extract_media_assets(
    docs,
    query="",
    intent=None,
    people=None
):

    images=[]
    videos=[]
    pdfs=[]
    links=[]
    cards=[]
    sources=[]

    seen_titles=set()


    image_pattern=(
        r'https?://[^\s"\']+\.(?:jpg|jpeg|png|gif|webp)'
    )

    video_pattern=(
        r'https?://[^\s"\']+\.(?:mp4|mov|webm)'
    )

    youtube_pattern=(

        r'https?:\/\/(?:www\.)?'

        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)'

        r'[^\s"\']+'
    )


    link_pattern=(
        r'https?://[^\s"\']+'
    )


    for doc in docs:

        metadata=doc.metadata or {}

        text=doc.page_content or ""


        detected_images=re.findall(

            image_pattern,

            text,

            flags=re.IGNORECASE
        )


        detected_videos=re.findall(

            video_pattern,

            text,

            flags=re.IGNORECASE
        )


        youtube_links=re.findall(

            youtube_pattern,

            text,

            flags=re.IGNORECASE
        )


        for yt in youtube_links:

            embed=convert_youtube_embed(
                yt
            )

            detected_videos.append(
                embed
            )


        detected_links=re.findall(

            link_pattern,

            text,

            flags=re.IGNORECASE
        )
        # ==========================================
        # Auto classify PDF URLs
        # ==========================================

        for url in detected_links:

            lower=url.lower()


            if any(

                x in lower

                for x in [

                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".webp"

                ]

            ):

                detected_images.append(
                    url
                )


            elif any(

                x in lower

                for x in [

                    ".mp4",
                    ".mov",
                    ".webm"

                ]

            ):

                detected_videos.append(
                    url
                )


        search_text=(

            query

            + " "

            + " ".join(
                people or []
            )

        )


        local_images,local_videos=(

            find_local_media(

                search_text,

                intent=intent,

                entities=people

            )

        )


        detected_images.extend(
            local_images
        )

        detected_videos.extend(
            local_videos
        )


        image=metadata.get(
            "image"
        )

        if image:

            detected_images.append(
                image
            )


        video=metadata.get(
            "video"
        )

        if video:

            detected_videos.append(
                video
            )


        source=metadata.get(
            "source"
        )

        if source:

            sources.append(
                source
            )


        clean_links=[]

        for l in detected_links:

            lower=l.lower()

            if any(

                ext in lower

                for ext in [

                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".webp",
                    ".mp4",
                    ".mov",
                    ".webm"

                ]

            ):

                continue


            if (

                "youtube"

                in lower

                or

                "youtu.be"

                in lower

            ):

                continue


            clean_links.append(
                l
            )


        images.extend(
            detected_images
        )

        videos.extend(
            detected_videos
        )

        links.extend(
            clean_links
        )


        title=metadata.get(
            "title"
        )

        if not title:

            lines=text.split("\n")

            if len(lines):

                title=lines[0][:80]


        if not title:

            continue


        if title in seen_titles:

            continue


        seen_titles.add(
            title
        )


        cards.append({

            "title":title,

            "subtitle":
            metadata.get(
                "designation",
                "Leadership"
            ),

            "description":
            text[:200],

            "image":
            detected_images[0]
            if detected_images
            else "",

            "video":
            detected_videos[0]
            if detected_videos
            else "",

            "source":
            source

        })


    return{

        "images":
        list(dict.fromkeys(
            images
        ))[:20],

        "videos":
        list(dict.fromkeys(
            videos
        ))[:1],

        "pdfs":
        list(dict.fromkeys(
            pdfs
        )),

        "links":
        list(dict.fromkeys(
            links
        )),

        "cards":
        cards,

        "sources":
        list(dict.fromkeys(
            sources
        ))
    }
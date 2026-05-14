# =========================================================
# Extract Media Assets
# =========================================================
def extract_media_assets(docs):

    images = []

    videos = []

    pdfs = []

    links = []

    cards = []

    sources = []

    for doc in docs:

        metadata = doc.metadata or {}

        # =====================================================
        # Images
        # =====================================================
        image = metadata.get("image")

        if image:

            images.append(image)

        # =====================================================
        # Videos
        # =====================================================
        video = metadata.get("video")

        if video:

            videos.append(video)

        # =====================================================
        # PDFs
        # =====================================================
        pdf = metadata.get("pdf")

        if pdf:

            pdfs.append(pdf)

        # =====================================================
        # Links
        # =====================================================
        link = metadata.get("link")

        if link:

            links.append(link)

        # =====================================================
        # Sources
        # =====================================================
        source = metadata.get("source")

        if source:

            sources.append(source)

        # =====================================================
        # Cards
        # =====================================================
        title = metadata.get("title")

        if title:

            cards.append({

                "title": title,

                "description": doc.page_content[:200],

                "image": image,

                "video": video,

                "source": source
            })

    return {

        "images": list(set(images)),

        "videos": list(set(videos)),

        "pdfs": list(set(pdfs)),

        "links": list(set(links)),

        "cards": cards,

        "sources": list(set(sources))
    }
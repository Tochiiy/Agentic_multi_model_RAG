from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from tools.img_tool import read_image_tool
from bs4 import BeautifulSoup
from typing import List
from utils.any_doc_loader import load_document
from urllib.parse import urljoin
import requests
import os
import bs4
import dotenv

dotenv.load_dotenv()


# ── 1. Format Documents as String ────────────────────────────────
def format_documents_as_string(documents: List[Document]) -> str:
    """
    Joins all document chunks into one string separated by blank lines.
    Used to inject retrieved context into the RAG prompt.
    """
    return "\n\n".join([doc.page_content for doc in documents if doc.page_content])


# ── 2. Generate Image Docs ────────────────────────────────────────
def generate_image_docs(images: List[str] = []) -> List[Document]:
    docs = []
    
    # filter valid image formats only
    
    valid_images = [
        img for img in images 
        if not img.split("?")[0].lower().endswith(".svg")
    ]
    
    print(f"  🖼️ Valid images (non-SVG): {len(valid_images)}/{len(images)}")
    
    for img_url in valid_images:
        try:
            result = read_image_tool.invoke({"image_url": img_url})
            if result.get("success") and result.get("summary"):
                doc = Document(
                    page_content=result["summary"],
                    metadata={
                        "image_url": img_url,
                        "doc_type": "imageSummary"
                    }
                )
                docs.append(doc)
            else:
                print(f"  ⚠️ Skipping image: {img_url[:50]}")
        except Exception as e:
            print(f"  ⚠️ Skipping image — {e}")

    return docs


# ── 3. Extract Image URLs from HTML ──────────────────────────────
def extract_image_urls(html: str, base_url: str) -> List[str]:
    """
    Parses raw HTML and extracts all image URLs from <img> tags.
    Handles src, data-src, data-lazy-src, and srcset attributes.
    Converts relative URLs to absolute using the base_url.
    """
    soup = BeautifulSoup(html, "lxml")
    image_urls = []

    for img in soup.find_all("img"):
        src = (
            img.get("src") or
            img.get("data-src") or
            img.get("data-lazy-src")
        )

        if not src and img.get("srcset"):
            src = img["srcset"].split(",")[0].split(" ")[0]

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src

        try:
            if src.startswith("http"):
                image_urls.append(src)
            else:
                image_urls.append(urljoin(base_url, src))
        except Exception:
            continue

    return image_urls


# ── 4. Web Base Loader ────────────────────────────────────────────
def web_base_loader(url: str) -> List[Document]:
    """
    Loads text content from a URL using WebBaseLoader.
    Targets article content only — ignores nav, sidebar, footer.
    """
    try:
        loader = WebBaseLoader(
            web_paths=[url],
            bs_kwargs={
                "parse_only": bs4.SoupStrainer(
                    class_=("post-content", "post", "post-header",
                            "content", "article", "main")
                )
            }
        )
        docs = loader.load()
        return docs
    except Exception as e:
        print(f"  ❌ Failed to load URL: {e}")
        return []


# ── 5. Main Pipeline: Load Docs + Images ─────────────────────────
def load_raw_docs_with_images(urls: List[str] = []) -> dict:
    """
    Full pipeline that:
    1. Loads text content from each URL
    2. Fetches raw HTML to extract image URLs
    3. Runs each image through the vision model
    4. Returns both text docs and image summary docs
    """
    all_documents = []
    all_image_summaries = []

    for url in urls:
        print(f"🔗 Loading: {url}")

        # Step 1 — load text content
        try:
            docs = web_base_loader(url)
            all_documents.extend(docs)
            print(f"  ✅ Loaded {len(docs)} text document(s)")
        except Exception as e:
            print(f"  ❌ Failed to load text: {e}")

        # Step 2 — fetch raw HTML
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                proxies={"http": None, "https": None},
                timeout=10
            )
            html = response.text
        except Exception as e:
            print(f"  ❌ Failed to fetch HTML: {e}")
            continue

        # Step 3 — extract image URLs
        image_urls = extract_image_urls(html, url)
        print(f"  📸 Found {len(image_urls)} image(s)")

        # Step 4 — generate image summaries
        image_docs = generate_image_docs(image_urls)
        all_image_summaries.extend(image_docs)
        print(f"  ✅ Generated {len(image_docs)} image summary docs")

    return {
        "documents": all_documents,
        "image_summaries": all_image_summaries
    }


# ── 6. Universal Loader ───────────────────────────────────────────
def load_any(source: str) -> List[Document]:
    """
    Universal entry point for all source types.

    Usage:
        load_any("https://example.com")   → web scrape
        load_any("paper.pdf")             → PDF
        load_any("notes.docx")            → Word
        load_any("data.csv")              → CSV
        load_any("slides.pptx")           → PowerPoint
        load_any("recording.mp3")         → audio transcription
    """
    if source.startswith("http"):
        return web_base_loader(source)

    ext = os.path.splitext(source)[1].lower()

    audio_formats = [".mp3", ".mp4", ".wav", ".m4a", ".flac", ".ogg", ".webm"]
    if ext in audio_formats:
        from utils.audio_loader import transcribe_audio
        return transcribe_audio(source)

    
    return load_document(source)


# ── Test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = load_raw_docs_with_images([
        "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"
    ])

    print(f"\n── Text Documents: {len(result['documents'])}")
    print(f"── Image Summaries: {len(result['image_summaries'])}")

    if result["image_summaries"]:
        print("\nFirst image summary:")
        print(result["image_summaries"][0].page_content[:300])

    print("\nFirst text document:")
    print(result["documents"][0].page_content[:300])    
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from utils.utils import load_raw_docs_with_images
from utils.utils import load_any
from embedding_model.embedding_model import embeddings
import uuid
import dotenv
import os


dotenv.load_dotenv()


# ── 1. Create Parent Docs ─────────────────────────────────────────
def create_parent_docs(raw_docs: list[Document]) -> list[Document]:
    """
    Large chunks (2000 chars) — used for context when answering.
    Each parent gets a unique UUID so children can reference it.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    parent_splits = splitter.split_documents(raw_docs)

    for split in parent_splits:
        chunk_id = str(uuid.uuid4())
        split.metadata["doc_type"] = "parent"
        split.metadata["chunk_id"] = chunk_id
        split.metadata["parent_id"] = chunk_id  # self-reference
        split.metadata["source"] = chunk_id

    return parent_splits


# ── 2. Create Child Docs ──────────────────────────────────────────
def create_child_docs(parent_docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    all_children = []

    for parent in parent_docs:
        children = splitter.split_documents([parent])  # split one parent at a time

        for i, child in enumerate(children):           # i resets per parent ✅
            parent_id = parent.metadata["chunk_id"]    # always correct ✅

            child.metadata["doc_type"] = "child"
            child.metadata["parent_id"] = parent_id
            child.metadata["chunk_id"] = f"child-{parent_id}-{i}"  # truly unique ✅
            child.metadata["source"] = child.metadata["chunk_id"]

            all_children.append(child)

    return all_children


# ── 3. Main Embedding Pipeline ────────────────────────────────────
def doc_embedding_multi_vector(sources: list[str]):
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    print("🔄 Extraction Phase...")
    raw_docs = []
    image_summaries = []

    for source in sources:
        print(f"🔗 Loading: {source}")

        if source.startswith("http"):
            # URL — load text + images
            result = load_raw_docs_with_images([source])
            raw_docs.extend(result["documents"])
            image_summaries.extend(result["image_summaries"])

        else:
            # local file — use universal loader
            
            docs = load_any(source)
            raw_docs.extend(docs)
            print(f"  ✅ Loaded {len(docs)} doc(s)")

    print(f"  ✅ {len(raw_docs)} text docs, {len(image_summaries)} image summaries")

    # chunk + store — same as before
    print("🔄 Chunking Phase...")
    parent_docs = create_parent_docs(raw_docs)
    child_docs = create_child_docs(parent_docs)
    print(f"  ✅ {len(parent_docs)} parent chunks")
    print(f"  ✅ {len(child_docs)} child chunks")

    print("💾 Storing in Pinecone...")
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    all_docs = [*parent_docs, *child_docs, *image_summaries]
    vector_store.add_documents(all_docs)

    print(f"✅ Finished embedding {len(all_docs)} total documents")
    return vector_store


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    doc_embedding_multi_vector([
        "https://lilianweng.github.io/posts/2023-06-23-agent/"
    ])
from langchain_pinecone  import PineconeVectorStore
from langchain_core.documents import Document
from embedding_model.embedding_model import embeddings
from utils.utils import format_documents_as_string
from pinecone import Pinecone
from typing import List
import dotenv
import os

dotenv.load_dotenv()


def query_multi_vector(query: str) -> dict:
    """
    Multi-vector retrieval pipeline:
    1. Search child docs (small, precise semantic match)
    2. Search image summaries
    3. Extract parent IDs from matched children
    4. Fetch full parent docs using those IDs (rich context)

    

    Why this works:
    - Children are small → better semantic similarity scores
    - Parents are large → better context for LLM to answer from
    - Images are tagged separately → multimodal retrieval
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    # ── Step 1: Search child docs ─────────────────────────────────
    child_docs = vector_store.similarity_search(
        query, k=6,
        filter={"doc_type": "child"}
    )
    print(f"  📚 Found {len(child_docs)} child docs")

    # ── Step 2: Search image summaries ───────────────────────────
    image_summaries = vector_store.similarity_search(
        query, k=2,
        filter={"doc_type": "imageSummary"}
    )
    print(f"  📸 Found {len(image_summaries)} image summaries")

    # ── Step 3: Extract unique parent IDs from children ───────────
    parent_ids = list(set([
        c.metadata.get("parent_id")
        for c in child_docs
        if c.metadata.get("parent_id") is not None
    ]))
    print(f"  🔗 Unique parent IDs: {len(parent_ids)}")

    # ── Step 4: Fetch full parent docs ────────────────────────────
    retrieved_parent_docs = []
    if parent_ids:
        retrieved_parent_docs = vector_store.similarity_search(
            query, k=3,
            filter={
                "doc_type": "parent",
                "source": {"$in": parent_ids}
            }
        )
    print(f"  📚 Found {len(retrieved_parent_docs)} parent docs")

    return {
        "query": query,
        "image_summaries": image_summaries,
        "retrieved_parent_docs": retrieved_parent_docs,
        "context": format_documents_as_string(retrieved_parent_docs),
        "image_context": format_documents_as_string(image_summaries),
        "full_context": format_documents_as_string(
            retrieved_parent_docs + image_summaries
        )
    }


# ── Test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    queries = [
        "Different types of memory architectures in AI agents",
        "Categories of memory systems for autonomous agents",
    ]

    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("=" * 50)
        result = query_multi_vector(query)

        print("\n── Parent Docs ─────────────────────────────")
        for doc in result["retrieved_parent_docs"]:
            print(doc.page_content[:300])
            print("---")

        print("\n── Image Summaries ─────────────────────────")
        for doc in result["image_summaries"]:
            print(doc.page_content[:200])
            print("---")
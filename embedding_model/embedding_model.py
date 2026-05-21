"""
Document embedding pipeline for RAG system.

Handles web scraping, document chunking, and storing embeddings in Pinecone
vector database using HuggingFace embeddings model.
"""

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_community.document_loaders import WebBaseLoader
from langchain_cohere import CohereEmbeddings
import bs4
from typing import List
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dotenv
import os

dotenv.load_dotenv()



embeddings = CohereEmbeddings(
    model="embed-english-v3.0",  
    cohere_api_key=os.getenv("COHERE_API_KEY")
)

def web_base_loader(url: str) -> List[Document]:
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
        print(f"Failed to load web page retrying in 20 seconds: {e}")
        time.sleep(20)
        return []


def parse_docs(docs: List[Document]) -> List[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
    )
    return splitter.split_documents(docs)


def embedded_data(chunks: List[Document]) -> PineconeVectorStore:
    """Embed chunks and store in Pinecone vector database."""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    vector_store.add_documents(chunks)
    return vector_store


def embed_url(url: str) -> PineconeVectorStore:
    """End-to-end pipeline: load → chunk → embed → store."""
    docs = web_base_loader(url)
    chunks = parse_docs(docs)
    return embedded_data(chunks)


if __name__ == "__main__":
    vector_store = embed_url("https://lilianweng.github.io/posts/2023-06-23-agent/")
    print(vector_store)
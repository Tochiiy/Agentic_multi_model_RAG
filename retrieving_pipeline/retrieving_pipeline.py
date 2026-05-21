"""
Multi-query Retrieval-Augmented Generation (RAG) pipeline.

Transforms queries, retrieves relevant documents from Pinecone, deduplicates,
and generates answers using LLM context.
"""

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from embedding_model.embedding_model import embeddings
from Agent import llm
from pydantic import BaseModel, Field
from typing import List
import dotenv
import os

dotenv.load_dotenv()


class QueriesOutput(BaseModel):
    """Structured output for query transformation results."""
    questions: List[str] = Field(
        description="array of questions for semantic search retrieval",
        max_length=3
    )


QUERY_TRANSFORMATION_PROMPT = PromptTemplate.from_template("""
You are an expert at query rewriting for semantic search and retrieval-augmented generation (RAG).

Step back and think about the user's underlying intent before rewriting the query.

Instructions:
1. Analyze the original question.
2. Identify the core goal, concepts, and implied context.
3. Generate at least 3 alternative rewritten queries that better express the same intent.
4. Each rewritten query should be clear, specific, and optimized for semantic retrieval.
5. Do NOT add explanations or reasoning.

Original question:
-------
{question}
-------
""")


GENERATE_RESPONSE_PROMPT = PromptTemplate.from_template("""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.

Question: {question}
Context: {context}
Answer:
""")


def query_vectorDB(query: str) -> List[Document]:
    """Query Pinecone vector database for similar documents."""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    return vector_store.similarity_search(query, k=5)


def format_docs_as_string(docs: List[Document]) -> str:
    """Format list of documents into a single context string."""
    return "\n\n".join([doc.page_content for doc in docs])


structured_llm = llm.with_structured_output(QueriesOutput)
query_transformation_chain = QUERY_TRANSFORMATION_PROMPT | structured_llm


def rag_chain(question: str) -> str:
    """
    Multi-query RAG pipeline: transform → retrieve → deduplicate → answer.
    
    Args:
        question: User query
        
    Returns:
        Generated answer based on retrieved context
    """
    generated: QueriesOutput = query_transformation_chain.invoke({"question": question})
    print("Generated queries:", generated.questions)

    all_docs = []
    for q in generated.questions:
        result = query_vectorDB(q)
        all_docs.extend(result)

    seen = set()
    unique_docs = []
    for doc in all_docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_docs.append(doc)

    context = format_docs_as_string(unique_docs)

    response = (GENERATE_RESPONSE_PROMPT | llm).invoke({
        "question": question,
        "context": context
    })
    return response.content


if __name__ == "__main__":
    answer = rag_chain("Types of Agent Memory")
    print("\n── Answer ──────────────────────────────")
    print(answer)
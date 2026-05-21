from retrieving_pipeline.multi_vector_retrieval import query_multi_vector
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from Agent import llm
from typing import List
import dotenv
import os
dotenv.load_dotenv()


# ── Pydantic Schemas ──────────────────────────────────────────────
class RetrieverInput(BaseModel):
    queries: List[str] = Field(
        description="array of input to retrieve data in vector db"
    )

class QueryTransformerInput(BaseModel):
    query: str = Field(description="user input to transform")

class QueriesOutput(BaseModel):
    questions: List[str] = Field(
        description="array of questions for semantic search retrieval",
        max_length=3
    )


# ── Tool 1: Retriever Tool ────────────────────────────────────────
async def retriever_tool(queries: List[str]) -> dict:
    """
    Retrieves documents and image summaries from Pinecone
    for each query, deduplicates, and returns formatted context.
    """
    retrieved_documents = []
    retrieved_image_documents = []
    seen_chunk_ids = set()

    for question in queries:
        result = query_multi_vector(question)

        parent_docs = result.get("retrieved_parent_docs", [])
        image_summaries = result.get("image_summaries", [])

        # ── deduplicate text docs ─────────────────────────────────
        for doc in parent_docs:
            chunk_id = doc.metadata.get("chunk_id")
            if not chunk_id:
                retrieved_documents.append(doc)
                continue
            if chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                retrieved_documents.append(doc)

        # ── deduplicate image summaries ───────────────────────────
        for doc in image_summaries:
            img_chunk_id = doc.id if hasattr(doc, "id") else doc.metadata.get("image_url")
            if not img_chunk_id:
                retrieved_image_documents.append(doc)
                continue
            if img_chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(img_chunk_id)
                retrieved_image_documents.append(doc)

    # ── format output ─────────────────────────────────────────────
    top_documents = "\n\n".join([
        doc.page_content for doc in retrieved_documents if doc.page_content
    ])

    image_urls = ",".join([
        doc.metadata.get("image_url", "")
        for doc in retrieved_image_documents
        if doc.metadata.get("image_url")
    ])

    final_response = f"""
        <retrieved_document>
        {top_documents}
        </retrieved_document>
        <retrieved_images>
        {image_urls}
        </retrieved_images>
    """

    print(final_response)

    return {
        "content": [
            {
                "type": "text",
                "text": final_response
            }
        ]
    }


# ── Tool 2: Query Transformer Tool ───────────────────────────────
async def query_transformer_tool(query: str) -> dict:
    """
    Rewrites the user query into 3 better versions
    optimized for semantic search retrieval.
    """
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

    
    structured_llm = llm.with_structured_output(QueriesOutput)
    chain = QUERY_TRANSFORMATION_PROMPT | structured_llm

    generated = chain.invoke({"question": query})
    questions = generated.questions

    return {
        "content": [
            {
                "type": "text",
                "text": f"here's a List of queries : {','.join(questions)}"
            }
        ]
    }



from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

async def web_search_tool(query: str) -> dict:
    """Search the web for current information."""
    try:
        result = search_tool.run(query)
        return {
            "content": [{"type": "text", "text": result}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Search failed: {str(e)}"}]
        }
    



from datetime import datetime
import pytz

async def get_current_datetime_tool(timezone: str = "UTC") -> dict:
    """
    Returns the current date, time, and day of the week.
    Useful for time-sensitive queries, scheduling, or current event tracking.
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        time_string = (
            f"Current Date and Time ({timezone}):\n"
            f"- ISO Timestamp: {now.isoformat()}\n"
            f"- Human Readable: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": time_string
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error fetching date/time for timezone '{timezone}': {str(e)}"
                }
            ]
        }
    

import numexpr as ne

class CalculatorInput(BaseModel):
    expression: str = Field(
        description="The mathematical expression to evaluate (e.g., '2 * (3 + 4)' or '1500 * (1 + 0.05)**5')"
    )

async def calculate_tool(expression: str) -> dict:
    """
    Safely evaluates a mathematical expression string. 
    Supports standard operators (+, -, *, /, **), math functions (sin, cos, log, exp), and nested parentheses.
    """
    # Clean standard human notations to machine syntax
    sanitized = expression.replace("^", "**").replace("x", "*").strip()
    
    try:
        # numexpr safely parses math without exposing system built-ins like eval() does
        result = ne.evaluate(sanitized).item()
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Expression: {expression}\nResult: {result}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Failed to evaluate expression. Ensure it only contains numbers and basic operators. Error: {str(e)}"
                }
            ]
        }


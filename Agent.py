"""
Main LLM agent configuration using OpenRouter.

This module initializes a ChatOpenAI instance configured to use OpenRouter
as the API provider, enabling access to multiple LLM models.
"""

from langchain_openai import ChatOpenAI
import dotenv
import os

dotenv.load_dotenv()

llm = ChatOpenAI(
    model="openrouter/auto",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "Agentic-RAG-MCP-Agent",
    },
    temperature=0.7,
    max_tokens=500
)

if __name__ == "__main__":
    response = llm.invoke("Hello!")
    print(response.content)
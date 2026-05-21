from langchain_openai import ChatOpenAI
import os
import dotenv

dotenv.load_dotenv()

vision_model = ChatOpenAI(
    model="openrouter/free",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "Agentic-RAG-MCP-Agent",
    },
    temperature=0.7,
)
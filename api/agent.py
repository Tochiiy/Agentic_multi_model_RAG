import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from retrieving_pipeline.multi_vector_retrieval import query_multi_vector
from Agent import llm
import httpx
import shutil
import json
import dotenv
import re
dotenv.load_dotenv()

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://agentic-multi-model-rag-78vm.vercel.app",
    "https://maxai-agent.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory chat history ────────────────────────────────────────
chat_history = []


# ── Manager Prompt ────────────────────────────────────────────────
MANAGER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant called Agentic RAG.

For greetings — respond warmly in ONE short sentence only. Example: "Hello! How can I assist you today?"
For questions — use the retrieved context, tool outputs, and calculations to answer accurately.
If context is empty or doesn't contain the answer, use your own knowledge.
Always respond in plain conversational English.
if user ask for tools, respond with a list of tools available
Never output JSON, structured formats, thoughts, or internal reasoning.
Never mention "context", "web search results", or any internal variables in your response.

{context}

{web_context}

{tool_context}
"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])
# ── Call MCP Tool ─────────────────────────────────────────────────
async def call_mcp_tool(tool_name: str, args: dict) -> str:
    """
    Calls a tool on the MCP server.
    All tools live in MCP — agent.py just orchestrates.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Step 1 — initialize MCP session
            init = await client.post(
                "http://localhost:3001/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "agent-backend", "version": "1.0.0"}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "x-api-key": os.getenv("MCP_API_KEY", "")
                },
                timeout=30
            )
            session_id = init.headers.get("mcp-session-id")

            # Step 2 — call the tool
            res = await client.post(
                "http://localhost:3001/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": args}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "x-api-key": os.getenv("MCP_API_KEY", ""),
                    "mcp-session-id": session_id or ""
                },
                timeout=60
            )

            # Step 3 — parse SSE response
            text = res.text
            data_line = next(
                (l.replace("data:", "").strip()
                 for l in text.split("\n") if l.startswith("data:")),
                "{}"
            )
            result = json.loads(data_line)
            content = result.get("result", {}).get("content", [{}])
            return content[0].get("text", "") if content else ""

    except Exception as e:
        print(f"❌ MCP tool call failed: {e}")
        return ""

@app.get("/")
async def root():
    return {"status": "healthy", "agent": "MAX-AI Running"}


# ── GET /api/agent/chat-history ───────────────────────────────────
@app.get("/api/agent/chat-history")
async def get_chat_history():
    formatted = []
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            formatted.append({
                "role": "human",
                "content": msg.content,
                "thinking": ""
            })
        elif isinstance(msg, AIMessage):
            formatted.append({
                "role": "ai",
                "content": msg.content,
                "thinking": getattr(msg, "thinking", "")
            })
    return {"messages": formatted}


# ── DELETE /api/agent/chat-history ───────────────────────────────
@app.delete("/api/agent/chat-history")
async def clear_chat_history():
    global chat_history
    chat_history = []
    return {"message": "Chat history cleared"}


# ── POST /api/agent/upload ────────────────────────────────────────
@app.post("/api/agent/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        from embedding_model.multi_vector_embedding import doc_embedding_multi_vector
        doc_embedding_multi_vector([temp_path])
        os.remove(temp_path)
        return {"success": True, "message": f"✅ {file.filename} embedded!"}
    except Exception as e:
        return {"success": False, "message": f"❌ {str(e)}"}


# ── POST /api/agent/embed-url ─────────────────────────────────────
@app.post("/api/agent/embed-url")
async def embed_url(url: str = Form(...)):
    try:
        from embedding_model.multi_vector_embedding import doc_embedding_multi_vector
        doc_embedding_multi_vector([url])
        return {"success": True, "message": f"✅ URL embedded!"}
    except Exception as e:
        return {"success": False, "message": f"❌ {str(e)}"}



# ── POST /api/agent/upload-image ─────────────────────────────────
@app.post("/api/agent/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        import base64
        from tools.img_tool import read_image_tool
        from langchain_core.documents import Document
        from langchain_pinecone import PineconeVectorStore
        from embedding_model.embedding_model import embeddings
        from pinecone import Pinecone

        # Step 1 — read image file as base64
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        ext = file.filename.split(".")[-1].lower()
        data_url = f"data:image/{ext};base64,{base64_image}"

        # Step 2 — analyze with vision model
        print(f"🖼️ Analyzing uploaded image: {file.filename}")
        result = read_image_tool.invoke({"image_url": data_url})

        if not result.get("success"):
            return {"success": False, "message": "❌ Failed to analyze image"}

        # Step 3 — embed summary into Pinecone
        doc = Document(
            page_content=result["summary"],
            metadata={
                "image_url": file.filename,
                "doc_type": "imageSummary",
                "source": file.filename
            }
        )

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        vector_store.add_documents([doc])

        return {"success": True, "message": f"✅ {file.filename} analyzed and embedded!"}
    except Exception as e:
        return {"success": False, "message": f"❌ {str(e)}"}



# ── Greeting detection ────────────────────────────────────────────
GREETINGS = {"hi", "hello", "hey", "howdy", "hiya", "sup", "what's up", "good morning", "good afternoon", "good evening"}

def is_greeting(message: str) -> bool:
    return message.lower().strip().rstrip("!?.") in GREETINGS


# ── GET /api/agent/stream ─────────────────────────────────────────

@app.get("/api/agent/stream")
async def stream_response(message: str):
    async def generate():
        try:
            context = ""
            web_context = ""
            tool_context = ""

            # Skip tool routing entirely for basic greetings
            if is_greeting(message):
                print("👋 Greeting detected — skipping retrieval")
            else:
                # ── A. Intelligently Trigger Date & Time Tool ──────
                time_keywords = {"date", "time", "clock", "today", "year", "now", "day"}
                if any(word in message.lower() for word in time_keywords):
                    print("🕒 Detected time-sensitive intent. Calling MCP get_current_datetime...")
                    # Pass the tool parameters matching your MCP specification
                    tool_context += await call_mcp_tool("get_current_datetime", {"timezone": "UTC"}) + "\n"

                # ── B. Intelligently Trigger Calculator Tool ──────
                # Regular expression targeting numbers paired with common mathematical operations
                if re.search(r'\d+\s*[\+\-\*/\^]\s*\d+', message):
                    print("🔢 Detected mathematical calculation intent. Calling MCP calculate...")
                    tool_context += await call_mcp_tool("calculate", {"expression": message}) + "\n"

                # ── C. Core RAG Retrieval ─────────────────────────
                print("📚 Calling MCP retriever tool...")
                rag_context = await call_mcp_tool("retriever", {"queries": [message]})
                context = rag_context

                # ── D. Web Search Fallback ────────────────────────
                if not context or len(context) < 200:
                    print("🌐 Calling MCP web_search tool...")
                    web_context = await call_mcp_tool("web_search", {"query": message})

            # ── E. Execute LLM Text Completion Chain ──────────────
            chain = MANAGER_PROMPT | llm
            full_response = ""

            async for chunk in chain.astream({
                "question": message,
                "context": context,
                "web_context": web_context,
                "tool_context": tool_context,  # Injects math/date responses dynamically
                "chat_history": chat_history[-6:],
            }):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content
                    yield f"event: message\ndata: {json.dumps({'message': content})}\n\n"

            chat_history.append(HumanMessage(content=message))
            chat_history.append(AIMessage(content=full_response))
            yield f"event: end\ndata: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"❌ Stream error: {e}")
            import traceback
            traceback.print_exc()
            yield f"event: message\ndata: {json.dumps({'message': f'Error: {str(e)}'})}\n\n"
            yield f"event: end\ndata: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "http://localhost:3000",
        }
    )

# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"✅ Agent API running at http://0.0.0.0:{port}")
    # Pass as a string reference so uvicorn workers resolve the module path correctly
    uvicorn.run("api.agent:app", host="0.0.0.0", port=port, reload=False)
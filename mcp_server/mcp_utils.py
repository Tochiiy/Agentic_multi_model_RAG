from fastapi import Request, HTTPException
import os
import dotenv

dotenv.load_dotenv()


# ── API Key Validation ────────────────────────────────────────────

async def validate_api_key(request: Request):
    """
    Validates the x-api-key header against MCP_API_KEY in .env
    Raises 401 if missing or invalid.
    """
    api_key = request.headers.get("x-api-key", "").strip()
    expected_key = os.getenv("MCP_API_KEY", "")

    if not api_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Format Documents as String ────────────────────────────────────
def format_documents_as_string(documents: list) -> str:
    """
    JS equivalent:
    const formatDocumentsAsString = (documents) =>
        documents.map((doc) => doc?.pageContent).join("\n\n")
    """
    return "\n\n".join([
        doc.page_content for doc in documents if doc.page_content
    ])
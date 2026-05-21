from tools.vision_model import vision_model  
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import requests
import base64
import os
import dotenv

dotenv.load_dotenv()

def encode_image_from_url(image_url: str) -> str:
    
    clean_url = image_url.split("?")[0]  # remove query params first
    if clean_url.endswith(".svg"):
        raise ValueError(f"SVG not supported: {image_url}")

    response = requests.get(
        image_url,
        proxies={"http": None, "https": None},
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    if not response.ok:
        raise ValueError(f"Invalid image URL: {image_url}")
    return base64.b64encode(response.content).decode("utf-8")

class ReadImageInput(BaseModel):
    image_url: str = Field(description="image url provided by the user")

@tool(args_schema=ReadImageInput)
def read_image_tool(image_url: str) -> dict:
    """Read and analyze an image from a URL and return a text summary."""
    try:
        base64_image = encode_image_from_url(image_url)

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Summarize the key elements in this image clearly and concisely."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        )

        response = vision_model.invoke([message])
        return {"success": True, "summary": response.content}

    except Exception as e:
        print(f"❌ Image read error: {e}")
        return {"success": False, "summary": ""}


# ── Test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = read_image_tool.invoke({
        "image_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
    })
    print("Success:", result["success"])
    print("Summary:", result["summary"])
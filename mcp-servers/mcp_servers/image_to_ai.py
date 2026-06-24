#!/usr/bin/env python3
"""
MCP Server for image-to-ai — exposes image conversion as MCP tools.

Tools:
  - image_to_base64: Convert local image to Base64 data URI
  - image_to_tensor: Convert local image to NumPy/PyTorch tensor
  - image_to_text: Extract text from image via OCR

Run: python -m mcp_servers.image_to_ai
"""
import base64
import mimetypes
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.lowlevel import NotificationOptions
import mcp.types as types

# Import our converter
skill_path = Path(__file__).parent.parent.parent / ".agents" / "skills" / "image-to-ai"
sys.path.insert(0, str(skill_path))
from image_to_ai import ImageToAI

converter = ImageToAI()

server = Server("image-to-ai")


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="image_to_base64",
            description="Convert a local image file to Base64 data URI for multimodal LLMs (GPT-4V, Claude, Gemini)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to local image file"},
                    "mime_type": {"type": "string", "description": "Optional MIME type override", "default": None},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="image_to_tensor",
            description="Convert a local image to numerical tensor (NumPy array or PyTorch tensor) for ML pipelines",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to local image file"},
                    "framework": {"type": "string", "enum": ["numpy", "pytorch", "torch"], "default": "numpy"},
                    "normalize": {"type": "boolean", "default": False},
                    "dtype": {"type": "string", "enum": ["float32", "float16", "uint8"], "default": None},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="image_to_text",
            description="Extract text from image using Tesseract OCR",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to local image file"},
                    "lang": {"type": "string", "default": "eng"},
                    "config": {"type": "string", "default": ""},
                },
                "required": ["image_path"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    image_path = arguments.get("image_path")
    if not image_path:
        return [TextContent(type="text", text="Error: image_path required")]

    try:
        if name == "image_to_base64":
            mime_type = arguments.get("mime_type")
            result = converter.to_base64(image_path, mime_type)
            return [TextContent(type="text", text=result)]

        elif name == "image_to_tensor":
            framework = arguments.get("framework", "numpy")
            normalize = arguments.get("normalize", False)
            dtype = arguments.get("dtype")
            result = converter.to_tensor(image_path, framework, normalize, dtype)
            
            if hasattr(result, "shape"):
                info = f"Shape: {result.shape}, Dtype: {result.dtype}"
                if hasattr(result, "device"):
                    info += f", Device: {result.device}"
                return [
                    TextContent(type="text", text=info),
                    TextContent(type="text", text=str(result.tolist() if hasattr(result, "tolist") else result)),
                ]
            return [TextContent(type="text", text=str(result))]

        elif name == "image_to_text":
            lang = arguments.get("lang", "eng")
            config = arguments.get("config", "")
            result = converter.to_text(image_path, lang, config)
            return [TextContent(type="text", text=result)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="image-to-ai",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
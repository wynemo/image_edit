import base64
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from config import settings

app = FastAPI(
    title="图片处理 API",
    description="上传图片并使用 AI 处理",
    version="1.0.0"
)

# 添加 CORS 中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageProcessRequest(BaseModel):
    prompt: str = "把这个弄成北条司漫画风格的"


class ImageProcessResponse(BaseModel):
    status: str
    text_response: Optional[str] = None
    images: Optional[list] = None
    processed_at: str
    error: Optional[str] = None


def encode_image_from_bytes(image_bytes: bytes, content_type: str) -> str:
    """将图片字节数据编码为base64格式的data URL"""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{content_type};base64,{base64_image}"


async def process_image_with_ai(image_bytes: bytes, content_type: str, prompt: str) -> Dict[str, Any]:
    """调用 OpenAI API 处理图片"""
    try:
        # 初始化 OpenAI 客户端
        client = OpenAI(
            base_url=settings.OPENAI_API_URL,
            api_key=settings.OPENAI_API_KEY,
        )
        
        # 编码图片
        image_data_url = encode_image_from_bytes(image_bytes, content_type)
        
        # 调用 API
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        }
                    ]
                }
            ]
        )
        
        # 处理响应
        response_message = completion.choices[0].message
        result = {
            "text_response": response_message.content if response_message.content else None,
            "images": []
        }
        
        # 检查是否有返回的图片
        if hasattr(response_message, 'images') and response_message.images:
            for image_data in response_message.images:
                if isinstance(image_data, str):
                    result["images"].append(image_data)
                elif isinstance(image_data, dict):
                    # 处理不同格式的图片数据
                    if 'b64_json' in image_data:
                        result["images"].append(image_data['b64_json'])
                    elif 'image_url' in image_data and 'url' in image_data['image_url']:
                        result["images"].append(image_data['image_url']['url'])
                    elif 'data' in image_data:
                        result["images"].append(image_data['data'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 调用失败: {str(e)}")


@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse("index.html")


@app.get("/api")
async def api_info():
    """API 信息"""
    return {
        "service": "图片处理 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process-image/": "上传图片并处理",
            "GET /docs": "API 文档"
        }
    }


@app.post("/process-image/", response_model=ImageProcessResponse)
async def process_image(
    file: UploadFile = File(..., description="要处理的图片文件"),
    prompt: str = Form(default="把这个弄成北条司漫画风格的", description="处理提示词")
):
    """
    上传图片并使用 AI 进行处理
    
    参数:
    - file: 图片文件 (支持 JPEG, PNG, GIF, WEBP 格式)
    - prompt: 处理提示词 (默认: "把这个弄成北条司漫画风格的")
    
    返回:
    - 处理结果，包含文字响应和生成的图片（如果有）
    """
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    content_type = file.content_type or "image/jpeg"  # 默认类型
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型: {content_type}. 支持的类型: {', '.join(allowed_types)}"
        )
    
    # 验证文件大小（限制为 20MB）
    max_size = 20 * 1024 * 1024  # 20MB
    contents = await file.read()
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400, 
            detail=f"文件太大. 最大允许大小: {max_size / 1024 / 1024}MB"
        )
    
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="文件为空")
    
    try:
        # 处理图片
        print("prompt is", prompt)
        result = await process_image_with_ai(contents, content_type, prompt)
        
        # 构造响应
        response = ImageProcessResponse(
            status="success",
            text_response=result.get("text_response"),
            images=result.get("images", []),
            processed_at=datetime.now().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        return ImageProcessResponse(
            status="error",
            error=str(e),
            processed_at=datetime.now().isoformat()
        )


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
import base64
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from config import settings


def encode_image(image_path):
    """将本地图片文件编码为base64格式的data URL"""
    with open(image_path, "rb") as image_file:
        import mimetypes
        mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{base64_image}"

client = OpenAI(
  base_url=settings.OPENAI_API_URL,
  api_key=settings.OPENAI_API_KEY,
)

completion = client.chat.completions.create(
  model=settings.OPENAI_MODEL,
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "把这个弄成北条司漫画风格的"
        },
        {
          "type": "image_url",
          "image_url": {
            # 方法1: 直接使用URL
            # "url": "http://xxx.com"
            
            # 方法2: 本地文件转base64
            # "url": f"data:image/png;base64,{base64.b64encode(open('path/to/image.png', 'rb').read()).decode()}"
            
            # 方法3: 使用辅助函数
            "url": encode_image("/Users/tommygreen/Downloads/photo_2024-12-11_13-47-13.jpg")  # 需要定义 encode_image 函数
          }
        }
      ]
    }
  ]
)

# 创建保存图片的目录
output_dir = Path("generated_images")
output_dir.mkdir(exist_ok=True)

# 获取响应内容
response_message = completion.choices[0].message

# 打印文字内容
if response_message.content:
    print("文字回复:", response_message.content)

# 保存base64图片的函数
def save_base64_image(base64_string, output_dir, index=0):
    """将base64编码的图片保存到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 移除base64前缀（如果有）
    if ',' in base64_string:
        # 格式如: data:image/png;base64,xxxxx
        header, base64_data = base64_string.split(',', 1)
        # 从header中提取图片格式
        if '/' in header and ';' in header:
            img_format = header.split('/')[1].split(';')[0]
        else:
            img_format = 'png'
    else:
        base64_data = base64_string
        img_format = 'png'
    
    file_path = output_dir / f"image_{timestamp}_{index}.{img_format}"
    
    try:
        # 解码base64数据
        image_data = base64.b64decode(base64_data)
        
        # 写入文件
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        print(f"图片已保存: {file_path}")
        return file_path
    except Exception as e:
        print(f"保存图片失败: {e}")
        return None

# 检查是否有图片返回
if hasattr(response_message, 'images') and response_message.images:
    print("\n返回的图片:")
    for i, image_data in enumerate(response_message.images):
        print(f"正在保存图片 {i+1}...")
        # 如果是base64数据
        if isinstance(image_data, str):
            save_base64_image(image_data, output_dir, i)
        # 如果是字典，可能包含base64数据
        elif isinstance(image_data, dict):
            if 'b64_json' in image_data:
                save_base64_image(image_data['b64_json'], output_dir, i)
            elif 'image_url' in image_data:
                # 如果是URL，打印出来（需要另外下载）
                #print(f"  图片URL: {image_data['image_url']['url']}")
                save_base64_image(image_data['image_url']['url'], output_dir, i)
            elif 'data' in image_data:
                save_base64_image(image_data['data'], output_dir, i)
使用 gemini-2.5-flash-image-preview 编辑图片的网站，调用openrouter 的 api


## 运行

编辑一下config.py里的 OPENAI_API_KEY, 可以使用openrouter的

`uv run main.py`

然后访问 http://127.0.0.1:8000

## 效果

![](2025-08-27-17-42-49.png)


## docker 部署

编写配置文件，参考 `settings.env.example`

`docker run --env-file settings.env --rm -it -p 8000:8000 wynemo/image-edit`
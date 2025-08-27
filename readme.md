使用 gemini-2.5-flash-image-preview 编辑图片的网站，调用openrouter 的 api


## 运行

`uv run main.py`

编辑一下config.py里的 OPENAI_API_KEY, 可以使用openrouter


## docker 部署

编写配置文件，参考 `settings.env.example`

`docker run --env-file settings.env --rm -it -p 8000:8000 wynemo/image-edit`
生成图片的网站，调用api

编辑一下 test_api.py 图片url 以及config.py里的 OPENAI_API_KEY

然后 `uv sync`

测试代码生成 `uv run test_api.py`

docker 部署

docker run --env-file settings.env --rm -it -p 8000:8000 wynemo/image-edit
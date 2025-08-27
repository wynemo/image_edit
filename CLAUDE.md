# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言

使用中文

## Project Overview

This is an image generation web application that calls APIs to generate images. It uses Python 3.12 with FastAPI and OpenAI dependencies.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies using uv (package manager)
uv sync

```

### Running the Application
```bash
# Run the main application
uv run main.py
```

## Architecture

The project is currently in early development with:
- `main.py` as the entry point
- FastAPI framework for building the web API
- OpenAI library for image generation capabilities
- Python 3.12 as the runtime environment
- uv as the package manager (with uv.lock for dependency locking)
# 🚀 Praveen Coding Asst & RAG Chatbot

An AI-powered Full-Stack Coding Assistant and Document RAG (Retrieval-Augmented Generation) application powered by **Qwen 2.5 Coder 7B (4-bit NF4)** and **SentenceTransformers**.

## ✨ Features
- **Local LLM Inference**: Runs `Qwen/Qwen2.5-Coder-7B-Instruct` quantized with 4-bit NormalFloat (NF4).
- **Real-Time Token Streaming**: Streams answers token-by-token using `TextIteratorStreamer`.
- **Dynamic PDF RAG**: Upload any PDF to extract text, chunk, embed with `all-MiniLM-L6-v2`, and retrieve top relevant context with page citations.
- **Modern Responsive Dark UI**: Built with responsive CSS and Markdown rendering.

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **LLM**: Qwen 2.5 Coder 7B (Hugging Face Transformers + BitsAndBytes)
- **Embeddings & Vector Search**: Sentence-Transformers + Cosine Similarity
- **Backend**: Flask + Flask-CORS
- **Frontend**: HTML5, CSS3, Vanilla JS, Marked.js

## 💻 Hardware Requirements
- **GPU**: NVIDIA GPU with >= 8 GB VRAM (or Google Colab T4 GPU).

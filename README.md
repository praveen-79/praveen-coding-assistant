# 🚀 Praveen Coding Asst & RAG Chatbot

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-yellow)](https://huggingface.co/spaces/praveenkumarpidamarthi/praveen-coding-assistant)
[![GitHub stars](https://img.shields.io/github/stars/praveen-79/praveen-coding-assistant?style=social)](https://github.com/praveen-79/praveen-coding-assistant)

> 🌐 **Try the Live App:** [https://huggingface.co/spaces/praveenkumarpidamarthi/praveen-coding-assistant](https://huggingface.co/spaces/praveenkumarpidamarthi/praveen-coding-assistant)

An AI-powered Full-Stack Coding Assistant and Document RAG (Retrieval-Augmented Generation) application powered by **Qwen 2.5 Coder 7B** and **SentenceTransformers**.

---

## ✨ Key Features
- **Intelligent Coding Assistant**: Explains programming concepts, algorithms (DSA), Python, SQL, and AI/ML code.
- **Dynamic PDF RAG**: Upload any PDF to extract text, create vector embeddings, and retrieve answers with cited source pages.
- **Real-Time Token Streaming**: Streams responses live word-by-word like ChatGPT.
- **Responsive Dark UI**: Clean, modern dark-themed web interface with built-in Markdown rendering.

---

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **LLM**: Qwen 2.5 Coder 7B
- **Embeddings & Vector Search**: Sentence-Transformers (`all-MiniLM-L6-v2`) + Cosine Similarity
- **Backend**: Flask, Flask-CORS, PyPDF
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Marked.js
- **Deployment**: Hugging Face Spaces

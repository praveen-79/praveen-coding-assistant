import os
import threading
import torch
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------------------------
# MODEL INITIALIZATION
# ---------------------------------------------------------------------------
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

print("Loading Qwen Tokenizer and Model...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    device_map="auto"
)

print("Loading SentenceTransformer...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

page_chunks = []
embeddings = None
SYSTEM_PROMPT = (
    "You are Praveen Coding Asst, a helpful AI coding and document assistant. "
    "Provide clear explanations and correct code."
)
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def retrieve_chunks(query, top_k=3):
    global embeddings, page_chunks
    if embeddings is None or len(page_chunks) == 0:
        return []
    query_emb = embedding_model.encode([query])
    sims = cosine_similarity(query_emb, embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    return [{"page": page_chunks[i]["page"], "score": float(sims[i]), "text": page_chunks[i]["text"]} for i in top_indices]

def generate_response_stream(messages, max_tokens=350):
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True
    ).to(model.device)

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    for new_text in streamer:
        yield new_text

# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    global page_chunks, embeddings, chat_history
    if "file" not in request.files:
        return jsonify({"error": "No file received"}), 400
    file = request.files["file"]
    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please provide a valid PDF file"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    reader = PdfReader(pdf_path)
    page_documents = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text and text.strip():
            page_documents.append({"page": page_number, "text": text.strip()})

    chunk_size, overlap = 800, 150
    page_chunks = []
    for page in page_documents:
        p_num, text = page["page"], page["text"]
        start = 0
        while start < len(text):
            chunk = text[start:start + chunk_size].strip()
            if chunk:
                page_chunks.append({"page": p_num, "text": chunk})
            start += chunk_size - overlap

    if page_chunks:
        embeddings = embedding_model.encode([item["text"] for item in page_chunks], show_progress_bar=False)
    else:
        embeddings = None

    chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"message": "File processed", "filename": filename, "pages": len(page_documents), "chunks": len(page_chunks)})

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message is empty"}), 400

    context, sources = "", []
    if embeddings is not None and len(page_chunks) > 0:
        retrieved_results = retrieve_chunks(user_message, top_k=3)
        if retrieved_results:
            context = "\n\n".join([f"[Page {r['page']}]\n{r['text']}" for r in retrieved_results])
            sources = [f"Page {r['page']}" for r in retrieved_results]

    if context:
        prompt = f"PDF Context:\n{context}\n\nUser Question: {user_message}\n\nAnswer using the PDF context when relevant."
        chat_history.append({"role": "user", "content": prompt})
    else:
        chat_history.append({"role": "user", "content": user_message})

    if len(chat_history) > 7:
        messages_to_generate = [chat_history[0]] + chat_history[1:][-6:]
    else:
        messages_to_generate = list(chat_history)

    def token_stream():
        full_response = []
        try:
            for token in generate_response_stream(messages_to_generate):
                full_response.append(token)
                yield token
            if sources:
                unique_sources = sorted(list(set(sources)))
                source_text = f"\n\n*(Sources: {', '.join(unique_sources)})*"
                full_response.append(source_text)
                yield source_text
            chat_history.append({"role": "assistant", "content": "".join(full_response)})
        except Exception as e:
            yield f"\n[AI Error: {str(e)}]"

    return Response(stream_with_context(token_stream()), mimetype="text/plain")

@app.route("/clear", methods=["POST"])
def clear_chat():
    global chat_history
    chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"message": "Chat cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

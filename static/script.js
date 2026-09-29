const chatArea = document.getElementById("chatArea");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const newChatBtn = document.getElementById("newChatBtn");
const clearButton = document.getElementById("clearButton");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const welcome = document.getElementById("welcome");

function addStaticMessage(text, type) {
    if (welcome) welcome.style.display = "none";
    const message = document.createElement("div");
    message.className = `message ${type}`;
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = type === "user" ? "You" : "AI";
    const content = document.createElement("div");
    content.className = "message-content";
    content.innerHTML = type === "ai" ? marked.parse(text) : document.createTextNode(text).textContent;
    message.appendChild(avatar);
    message.appendChild(content);
    chatArea.appendChild(message);
    chatArea.scrollTop = chatArea.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addStaticMessage(text, "user");
    input.value = "";

    if (welcome) welcome.style.display = "none";
    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai";
    aiMessage.innerHTML = `<div class="message-avatar">AI</div><div class="message-content"><em>Thinking...</em></div>`;
    chatArea.appendChild(aiMessage);
    chatArea.scrollTop = chatArea.scrollHeight;

    const contentDiv = aiMessage.querySelector(".message-content");
    let accumulatedText = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        if (!response.ok) throw new Error("Server error");
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            accumulatedText += decoder.decode(value, { stream: true });
            contentDiv.innerHTML = marked.parse(accumulatedText) + '<span style="color:#4CAF50;">▊</span>';
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        contentDiv.innerHTML = marked.parse(accumulatedText);
    } catch (error) {
        contentDiv.innerHTML = "⚠️ Error communicating with server.";
    }
}

sendButton.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

async function resetChat() {
    await fetch("/clear", { method: "POST" });
    chatArea.innerHTML = "";
    if (welcome) { chatArea.appendChild(welcome); welcome.style.display = "block"; }
}
if (newChatBtn) newChatBtn.addEventListener("click", resetChat);
if (clearButton) clearButton.addEventListener("click", resetChat);

fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    fileName.textContent = file.name;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
        addStaticMessage("Please select a PDF file.", "ai");
        return;
    }
    addStaticMessage(`Uploading **${file.name}** and creating embeddings...`, "ai");
    const formData = new FormData();
    formData.append("file", file);
    try {
        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();
        if (res.ok) {
            addStaticMessage(`✅ **${data.filename}** loaded (${data.pages} pages, ${data.chunks} chunks). Ask questions now!`, "ai");
        } else {
            addStaticMessage(`Upload failed: ${data.error}`, "ai");
        }
    } catch (e) {
        addStaticMessage("Unable to upload PDF.", "ai");
    }
});

document.querySelectorAll(".suggestion").forEach(card => {
    card.addEventListener("click", () => {
        input.value = card.dataset.question;
        input.focus();
    });
});
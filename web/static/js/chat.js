const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const conversationList = document.getElementById("conversationList");
const newChatBtn = document.getElementById("newChatBtn");
const suggestionsBar = document.getElementById("suggestionsBar");

if (!chatForm || !chatInput || !chatMessages) {
  // This script is loaded globally from layout.html; no-op outside chat screen.
} else {
const chatBtn = chatForm.querySelector("button[type='submit']");
const chatBtnText = document.getElementById("chatBtnText");
const chatSpinner = document.getElementById("chatSpinner");
const stopBtn = document.getElementById("stopBtn");

let currentChatId = null;
let isStreaming = false;
let streamController = null;

function createMessageBubble(text, sender = "user") {
  const wrapper = document.createElement("div");
  wrapper.className = sender === "user" ? "flex justify-end" : "flex justify-start";

  const bubble = document.createElement("div");
  bubble.className =
    sender === "user"
      ? "bg-green-600 text-white p-3 rounded-2xl max-w-2xl whitespace-pre-wrap"
      : "bg-gray-700 text-white p-3 rounded-2xl max-w-2xl prose prose-invert";

  if (sender === "bot") {
    bubble.innerHTML = marked.parse(text || "");
  } else {
    bubble.innerText = text || "";
  }

  wrapper.appendChild(bubble);
  return { wrapper, bubble };
}

function setSendingState(sending) {
  isStreaming = sending;
  chatSpinner.classList.toggle("hidden", !sending);
  chatBtnText.textContent = sending ? "Generating..." : "Send";
  chatBtn.disabled = sending;
  if (stopBtn) {
    stopBtn.classList.toggle("hidden", !sending);
  }
}

function adjustInputHeight() {
  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 180)}px`;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createSuggestionChip(text) {
  const button = document.createElement("button");
  button.type = "button";
  button.className =
    "px-3 py-1.5 rounded-full text-xs bg-gray-700 hover:bg-gray-600 transition border border-gray-600";
  button.innerText = text;
  button.addEventListener("click", () => {
    chatInput.value = text;
    adjustInputHeight();
    chatInput.focus();
  });
  return button;
}

function renderSuggestions(suggestions) {
  if (!suggestionsBar) return;
  suggestionsBar.innerHTML = "";
  if (!Array.isArray(suggestions) || suggestions.length === 0) return;
  suggestions.forEach((suggestion) => suggestionsBar.appendChild(createSuggestionChip(suggestion)));
}

async function loadPromptSuggestions(chatId = null) {
  const query = chatId ? `?chat_id=${chatId}` : "";
  const response = await fetch(`/prompt-suggestions${query}`, {
    credentials: "include",
  });
  const data = await response.json();
  if (!response.ok) return;
  renderSuggestions(data.suggestions || []);
}

function buildConversationItem(conv) {
  const item = document.createElement("button");
  item.type = "button";
  item.className = [
    "w-full text-left p-2 rounded-lg cursor-pointer text-sm border-b border-gray-800",
    "hover:bg-gray-700 transition",
    conv.id === currentChatId ? "bg-gray-700" : "",
  ].join(" ");

  item.innerText = conv.title || "New Chat";
  item.onclick = () => loadConversation(conv.id);
  return item;
}

async function loadConversations() {
  const response = await fetch("/conversations", { credentials: "include" });
  const data = await response.json();

  if (!conversationList) return;
  conversationList.innerHTML = "";

  if (!Array.isArray(data) || data.length === 0) {
    const empty = document.createElement("div");
    empty.className = "p-3 text-sm text-gray-400";
    empty.innerText = "No chats yet";
    conversationList.appendChild(empty);
    return;
  }

  data.forEach((conv) => conversationList.appendChild(buildConversationItem(conv)));
}

async function loadConversation(id) {
  const response = await fetch(`/conversations/${id}`, {
    credentials: "include",
  });
  const messages = await response.json();
  if (!response.ok) return;

  currentChatId = id;
  chatMessages.innerHTML = "";

  messages.forEach((msg) => {
    const sender = msg.role === "assistant" ? "bot" : "user";
    const bubble = createMessageBubble(msg.content, sender);
    chatMessages.appendChild(bubble.wrapper);
  });

  await loadConversations();
  await loadPromptSuggestions(id);
  scrollToBottom();
}

async function streamAIResponse(userMessage, assistantBubble, signal) {
  const response = await fetch("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message: userMessage, chat_id: currentChatId }),
    signal,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Streaming failed");
  }

  const returnedChatId = Number(response.headers.get("X-Chat-Id"));
  if (returnedChatId) {
    currentChatId = returnedChatId;
    await loadConversations();
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let fullText = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const token = decoder.decode(value, { stream: true });
    fullText += token;
    assistantBubble.innerHTML = marked.parse(fullText);
    scrollToBottom();
  }

  return fullText;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isStreaming) return;

  const message = chatInput.value.trim();
  if (!message) return;

  const user = createMessageBubble(message, "user");
  chatMessages.appendChild(user.wrapper);
  scrollToBottom();

  chatInput.value = "";
  adjustInputHeight();
  setSendingState(true);

  const assistant = createMessageBubble("", "bot");
  chatMessages.appendChild(assistant.wrapper);
  scrollToBottom();

  try {
    streamController = new AbortController();
    await streamAIResponse(message, assistant.bubble, streamController.signal);
    await loadPromptSuggestions(currentChatId);
  } catch (error) {
    if (error.name === "AbortError") {
      // User intentionally stopped generation; keep partial streamed text as-is.
    } else {
      assistant.bubble.innerText = "Error: " + error.message;
    }
  } finally {
    streamController = null;
    setSendingState(false);
  }
});

chatInput.addEventListener("input", adjustInputHeight);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

if (newChatBtn) {
  newChatBtn.addEventListener("click", async () => {
    if (isStreaming) return;
    currentChatId = null;
    chatMessages.innerHTML = "";
    await loadConversations();
    await loadPromptSuggestions();
    chatInput.focus();
  });
}

if (stopBtn) {
  stopBtn.addEventListener("click", () => {
    if (streamController && isStreaming) {
      streamController.abort();
    }
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  adjustInputHeight();
  await loadConversations();
  await loadPromptSuggestions();
});
}

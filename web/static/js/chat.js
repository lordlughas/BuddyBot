// Chat UI script for BuddyBot

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

// Button + spinner references
const chatBtn = chatForm.querySelector("button");
const chatBtnText = document.getElementById("chatBtnText");
const chatSpinner = document.getElementById("chatSpinner");

// Utility: create a chat bubble
// function createMessageBubble(text, sender = "user") {
//   const bubble = document.createElement("div");
//   bubble.className =
//     sender === "user"
//       ? "flex justify-end"
//       : "flex justify-start";

//   const inner = document.createElement("div");
//   inner.className =
//     sender === "user"
//       ? "bg-green-600 text-white p-3 rounded-lg max-w-xs animate-fadeIn"
//       : "bg-gray-700 text-white p-3 rounded-lg max-w-xs animate-fadeIn";

//   inner.textContent = text;
//   bubble.appendChild(inner);
//   return bubble;
// }
function createMessageBubble(text, sender = "user") {
  const wrapper = document.createElement("div");
  wrapper.className =
    sender === "user"
      ? "flex justify-end"
      : "flex justify-start";

  const bubble = document.createElement("div");
  bubble.className =
    sender === "user"
      ? "bg-green-600 text-white p-3 rounded-2xl max-w-2xl whitespace-pre-wrap"
      : "bg-gray-700 text-white p-3 rounded-2xl max-w-2xl prose prose-invert";

  if (sender === "bot") {
    // 🔥 Render Markdown properly
    bubble.innerHTML = marked.parse(text);
  } else {
    bubble.innerText = text;
  }

  wrapper.appendChild(bubble);
  return wrapper;
}



// Typing indicator
function showTypingIndicator() {
  const typing = document.createElement("div");
  typing.id = "typingIndicator";
  typing.className = "flex justify-start";
  typing.innerHTML = `
    <div class="bg-gray-700 text-white p-3 rounded-lg max-w-xs animate-pulse">
      ...
    </div>
  `;
  chatMessages.appendChild(typing);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
  const typing = document.getElementById("typingIndicator");
  if (typing) typing.remove();
}

// // Fake AI response (replace with API call later)
// async function getAIResponse(userMessage) {
//   // Simulate delay
//   return new Promise((resolve) => {
//     setTimeout(() => {
//       resolve(`You said: "${userMessage}". Let's talk finance! 💹`);
//     }, 1500);
//   });
// }
// 🔥 REAL AI CALL
async function getAIResponse(userMessage) {
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ message: userMessage, chat_id: currentChatId }),
    });

    const data = await response.json();

    currentChatId = data.chat_id;
    loadConversation();
    if (!response.ok) {
      throw new Error(data.error || "Something went wrong");
    }

    return data.reply;

  } catch (error) {
    return "⚠️ Error: " + error.message;
  }
}

// Handle form submit
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  // Add user bubble
  chatMessages.appendChild(createMessageBubble(message, "user"));
  chatMessages.scrollTop = chatMessages.scrollHeight;
  chatInput.value = "";

  // Show loading state on button
  chatSpinner.classList.remove("hidden");
  chatBtnText.textContent = "Sending...";
  chatBtn.disabled = true;

  // Show typing indicator
  showTypingIndicator();

  // Get AI response
  const response = await getAIResponse(message);

  // Remove typing indicator
  removeTypingIndicator();

  // Add AI bubble
  chatMessages.appendChild(createMessageBubble(response, "bot"));
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Reset loading state
  chatSpinner.classList.add("hidden");
  chatBtnText.textContent = "Send";
  chatBtn.disabled = false;
});



//let currentConversationId = null;
let currentChatId = null;

async function loadConversations() {
  const response = await fetch("/conversations", {
    credentials: "include",
  });
  
  const data = await response.json();

  const sidebar = document.querySelector("#conversationList");
  sidebar.innerHTML = "";

  data.forEach(conv => {
    const item = document.createElement("div");
    item.className = "p-2 hover:bg-gray-700 cursor-pointer text-sm border-b border-gray-800";
    item.innerText = conv.title;

    item.onclick = () => loadConversation(conv.id);

    sidebar.appendChild(item);
  });
}

async function loadConversation(id) {
  const response = await fetch(`/conversations/${id}`, {
    credentials: "include",
  });
  const messages = await response.json();

  //currentConversationId = id;
  currentChatId = id;
  chatMessages.innerHTML = "";

  messages.forEach(msg => {
    chatMessages.appendChild(createMessageBubble(msg.content, msg.role === "assistant" ? "bot" : "user"));
  });
}

window.onload = loadConversations;
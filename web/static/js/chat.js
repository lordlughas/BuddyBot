const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, "user");
    userInput.value = "";

    // // Temporary bot reply (Phase 4 logic later)
    // setTimeout(() => {
    //     addMessage("🤖 I'm thinking... (backend coming soon)", "bot");
    // }, 600);

    // Typing indicator
    const typing = addMessage("BuddyBot is typing...", "bot");
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });
        const data = await response.json();

        typing.remove();
        addMessage(data.reply, "bot");

    } catch (error) {
        typing.remove();
        addMessage(" Error connecting to server", "bot");
    }
});

function addMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    const p = document.createElement("p");
    p.textContent = text;

    msgDiv.appendChild(p);
    chatBox.appendChild(msgDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    return msgDiv;
}

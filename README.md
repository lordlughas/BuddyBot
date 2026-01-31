# 🤖 BuddyBot — A Friendly Rule-Based Chatbot

BuddyBot is a web-based chatbot built with **Python and Flask**.  
It uses **rule-based logic** to detect user mood, provide encouragement, study tips, jokes, and friendly conversation through a clean chat-style interface inspired by ChatGPT.

This project is designed for **learning**, **demonstration**, **portfolio use**, and **class project**.

---

## 🚀 Features

- 💬 ChatGPT-style web interface  
- 😊 Mood detection (happy, sad, stressed, tired)  
- 📚 Study tips for students  
- 😂 Random jokes  
- 💙 Encouraging responses  
- 🧠 Session-based chat memory  
- 🧩 Clean modular architecture  
- 🌐 Ready for hosting & deployment  

---

## 🛠 Tech Stack

- **Backend:** Python 3.10, Flask  
- **Frontend:** HTML, CSS, JavaScript (Fetch API)  
- **Logic:** Rule-based chatbot engine  
- **Session Management:** Flask Sessions  
- **Version Control:** Git & GitHub  

---

## 📁 Project Structure

BuddyBot/
│
├── app/
│ ├── init.py
│ ├── config.py # Bot personality, keywords, responses
│ ├── responses.py # Rule-based chatbot logic
│ └── chatter.py # (Future AI integration)
│
├── web/
│ ├── init.py
│ ├── app.py # Flask routes & session handling
│ └── templates/
│ └── index.html # Chat UI
│
├── tests/
│ ├── appTest.py
│ └── chatterTest.py
│
├── run.py # Application entry point
├── requirements.txt # Dependencies
└── README.md


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/lordlughas/BuddyBot.git
cd BuddyBot

### 2️⃣ Create & activate virtual environment
```bash
py -3.10 -m venv venv
venv\Scripts\activate

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Run the application
python run.py

Open your browser and visit:
http://127.0.0.1:5000


🧪 Example Interactions

User: "I am sad"
BuddyBot: "I'm sorry you're feeling this way 💙 You’re doing better than you think 😊"


📌 Learning Objectives

Understand chatbot architecture

Learn Flask routing & sessions

Practice clean project structuring

Apply rule-based AI logic

Gain real-world debugging experience

Use Git for version control


🔮 Future Enhancements

AI-powered responses (OpenAI / local LLM)

Database-backed chat history

User authentication

Dark/light theme toggle

Cloud deployment

🧑‍💻 Author

Built by Charles Lughas
Guided step-by-step for learning and mastery.
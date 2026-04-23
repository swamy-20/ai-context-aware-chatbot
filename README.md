# 🤖 ArchiText – Context-Aware AI Chatbot

An AI-powered chatbot built with a multi-service architecture, designed for **context-aware conversations** using advanced Natural Language Processing (NLP) techniques like TF-IDF, Word2Vec, and multi-turn dialogue handling.







---

## 🖥️ Chatbot Interface

<img width="865" height="711" alt="Screenshot 2026-04-01 140637" src="https://github.com/user-attachments/assets/e08a3dc6-0264-471c-b439-9a1261459328" />


## 💡 Why This Project?

This project demonstrates **real-world AI system design** by combining:

* Multi-service architecture (Frontend + Backend + NLP microservice)
* Hybrid NLP techniques (TF-IDF + Word2Vec)
* Context-aware multi-turn conversations
* Scalable API-based backend design

👉 Built as a **production-style project**, not just a basic ML demo.

---

## 🏗️ Architecture

```
Client (React + Vite)
        ↓
Backend (Node.js + Express)
        ↓
NLP Service (FastAPI)
        ↓
ML Models (TF-IDF + Word2Vec)
```


---

## 🔥 Key Features

* 🧠 **Context-Aware Chatbot** (multi-turn memory)
* ⚡ **Hybrid NLP Engine** (TF-IDF + Word2Vec)
* 🏷️ **Intent Detection System**
* 💬 **Human-like Response Generation**
* 🎯 **~90% Intent Accuracy**
* 🌐 **Modern UI (React + Tailwind)**
* 🔌 **API-based modular architecture**

---

## 🛠️ Tech Stack

| Layer      | Technology                  |
| ---------- | --------------------------- |
| Frontend   | React + Vite + Tailwind CSS |
| Backend    | Node.js + Express           |
| NLP Engine | Python + FastAPI            |
| ML Models  | TF-IDF + Word2Vec (Gensim)  |
| Database   | Prisma ORM                  |

---

## 🚀 Quick Start (Standalone Chatbot)

```bash
cd chatbot
python app.py
```

👉 Open: `http://localhost:8001`

---

## ⚙️ Full Project Setup

### 1️⃣ NLP Service

```bash
cd nlp-service
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
```

---

### 2️⃣ Backend Server

```bash
cd server
npm install
npx prisma db push
npm run dev
```

---

### 3️⃣ Frontend

```bash
cd client
npm install
npm run dev
```

👉 Open: `http://localhost:5173`

---

## 📡 API Example

### Chat Request

```json
{
  "message": "What is AI?",
  "level": 3
}
```

### Response

```json
{
  "response": "AI (Artificial Intelligence) is...",
  "intent": "technical_inquiry",
  "confidence": 0.92
}
```

---

## 📊 Dataset

Due to GitHub file size limitations, the dataset is not included.

👉 Download dataset here:
https://www.kaggle.com/datasets/multi-turn-chatbot-conversation-dataset

---

## 🏆 Key Highlights

* Built a **multi-service AI system**
* Implemented **hybrid NLP model**
* Designed **scalable backend architecture**
* Optimized dataset from **1GB → 2MB**
* Achieved **high intent classification accuracy**

---

## 🚀 Future Improvements

* 🌍 Multi-language support
* 🎤 Voice integration (speech-to-text)
* 🤖 Transformer models (BERT/GPT)
* 📊 Analytics dashboard

---

## 🤝 Contributing

Pull requests are welcome!
Feel free to fork and improve the project.

---

## 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

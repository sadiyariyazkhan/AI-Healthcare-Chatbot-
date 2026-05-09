# 🏥 AI Healthcare Chatbot

An intelligent, LLM-powered healthcare assistant built with **LLaMA 3.3**, **FastAPI**, and a **RAG-based CSV lookup system**. It understands medical queries, classifies intent, and responds with structured, accurate health information — including causes, symptoms, treatments, medications, tips, and specialist recommendations.

---

## 🚀 Live Demo

> Coming soon / [Add your deployed link here]

---

## 📸 Screenshots

> Add screenshots of your chatbot UI here

---

## ✨ Features

- 🤖 **LLM-powered responses** using LLaMA 3.3 via Groq API
- 🔍 **RAG-based CSV lookup** — checks a medical knowledge base before calling the LLM
- 🧠 **Smart query classification** — detects if user is asking about causes, symptoms, treatments, medications, tips, or doctors
- 🩺 **Specialist recommendation** — suggests the right doctor type based on the condition
- 🎙️ **Speech-to-Text (STT)** support for voice input
- ✍️ **Autocorrect** for misspelled medical terms
- 🧹 **Clean, structured responses** — numbered points, no raw Markdown clutter
- 💬 **Greeting & gratitude handling** for natural conversation flow

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI |
| LLM | LLaMA 3.3 70B (via Groq API) |
| RAG / Knowledge Base | Pandas CSV lookup |
| NLP | Custom query classifier, Autocorrect |
| Frontend | HTML/CSS/JS (Jinja2 templates) |
| Deployment | Uvicorn |

---

## 📁 Project Structure

```
AI-Healthcare-Chatbot/
│
├── main.py                 # FastAPI app — routes, logic, Groq integration
├── medical.csv             # Medical knowledge base (question-answer pairs)
├── requirements.txt        # Python dependencies
│
├── templates/
│   └── index.html          # Chat UI (served via FastAPI)
│
└── static/
    ├── style.css           # Stylesheet
    └── script.js           # Frontend JS (chat, STT, etc.)
```

---

## ⚙️ How It Works

```
User Message
     │
     ▼
Autocorrect & Normalize
     │
     ▼
CSV Exact Lookup ──── Found? ──► Return CSV Answer
     │
   Not Found
     │
     ▼
Query Type Detection
(disease / causes / symptoms / treatment /
 medicine / tips / doctor / general)
     │
     ▼
Groq LLM (LLaMA 3.3) with structured prompt
     │
     ▼
Clean & Format Response
     │
     ▼
Return to User
```

---

## 🔑 Query Types Detected

| Query Type | Example |
|-----------|---------|
| `disease` | "What is diabetes?" |
| `disease_with_causes` | "What causes asthma?" |
| `disease_with_symptoms` | "Symptoms of malaria?" |
| `disease_with_treatment` | "Treatment for hypertension?" |
| `medicine_only` | "What medicines are used for fever?" |
| `tips_only` | "Tips to manage stress?" |
| `doctor` | "Which doctor should I consult for chest pain?" |
| `full_disease_report` | "Full details about diabetes" |
| `general` | Everything else |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sadiyariyazkhan/AI-Healthcare-Chatbot.git
cd AI-Healthcare-Chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

```bash
# Linux / Mac
export GROQ_API_KEY="your_groq_api_key_here"

# Windows (Command Prompt)
set GROQ_API_KEY=your_groq_api_key_here
```

> Get your free API key at [console.groq.com](https://console.groq.com)

### 4. Run the app

```bash
uvicorn main:app --reload
```

### 5. Open in browser

```
http://127.0.0.1:8000
```

---

## 📦 Requirements

```
fastapi
uvicorn
groq
pandas
autocorrect
python-multipart
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the chat UI |
| `POST` | `/chat` | Accepts messages, returns AI reply |

### Example Request

```json
POST /chat
{
  "messages": [
    { "role": "user", "content": "What are the symptoms of diabetes?" }
  ]
}
```

### Example Response

```json
{
  "reply": "1. Frequent urination\n2. Excessive thirst\n3. Unexplained weight loss\n..."
}
```

---

## 🧠 Key Functions

| Function | Purpose |
|----------|---------|
| `detect_query_type()` | Classifies user intent from keywords |
| `lookup_csv_exact()` | Searches medical.csv for exact matches |
| `groq_chat()` | Sends structured prompt to LLaMA 3.3 |
| `clean_groq_reply()` | Strips Markdown, formats HTML response |
| `format_points_universal()` | Converts list responses to numbered points |

---

## 🔮 Future Improvements

- [ ] Deploy on Hugging Face Spaces / Render
- [ ] Add fuzzy matching for CSV lookup
- [ ] Support multi-turn conversation memory
- [ ] Add multilingual support (Hindi, Urdu)
- [ ] Integrate a proper medical database (e.g. MedQuAD)

---

## 👩‍💻 Author

**Sadiya Riyaz Khan**  
AI/ML Engineer · Delhi, India  
📧 sadiyariyazkhan012@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/sadiya-riyaz-khan) · [GitHub](https://github.com/sadiyariyazkhan)
---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

⭐ *If you found this project useful, please give it a star!*

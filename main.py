import os
import re
import html
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from groq import Groq
from autocorrect import Speller

# ---------------- FASTAPI SETUP ----------------
app = FastAPI(title="AI Healthcare Chatbot")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ---------------- GROQ SETUP ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment variables.")

GROQ_MODEL = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=GROQ_API_KEY)

# ---------------- LOAD CSV ----------------
try:
    df = pd.read_csv(os.path.join(BASE_DIR, "medical.csv"))
except FileNotFoundError:
    df = pd.DataFrame(columns=["question", "answer", "source", "focus_area"])
    print("Warning: medical.csv not found. CSV lookups will return 'Unknown'.")

# ---------------- DATA MODELS ----------------
class ChatRequest(BaseModel):
    messages: list

# ---------------- SPELL CHECKER ----------------
spell = Speller(lang='en')

# ---------------- GLOBAL KEYWORDS ----------------
doctor_phrases = ["doctor", "specialist", "consult", "which", "who", "best", "kind"]
tips_keywords = ["tip", "tips", "suggestion", "suggest", "advice", "how to", "ways to", "remedy"]
cause_keywords = ["cause", "causes"]
symptom_keywords = ["symptom", "symptoms"]
treatment_keywords = ["treatment", "therapy", "procedures", "surgeries"]
medicine_keywords = ["medicine", "medicines", "medication", "medications", "drugs"]
full_keywords = ["full info", "full report", "all details", "complete details","detail"]
disease_keywords = ["what", "explain", "disease"]

# ---------------- CLEANER FUNCTION ----------------
def clean_groq_reply(text: str) -> str:
    """
    Clean response:
    - Remove Markdown bold (**)
    - Remove #
    - Add colored spans for Explanation and Summary
    """
    if not text:
        return "No response from Groq API."
    text = html.unescape(text)
    # Remove HTML tags except <ul>, <li>
    text = re.sub(r"<(?!/?ul|/?li)[^>]+>", "", text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*\*', '', text)  # remove bold
    # Add colored headings
    text = re.sub(r'Explanation of the topic:|Explanation:', '<span style="color:blue;font-weight:normal;">Explanation</span>', text)
    text = re.sub(r'Summary:', '<span style="color:skyblue;font-weight:normal;">Summary</span>', text)
    return text.strip()

# ---------------- NORMALIZE TEXT ----------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ---------------- QUERY TYPE DETECTION ----------------
def detect_query_type(message: str) -> str:
    message_lower = message.lower()
    if any(kw in message_lower for kw in doctor_phrases):
        return "doctor"
    if any(kw in message_lower for kw in tips_keywords):
        return "tips_only"
    if any(kw in message_lower for kw in medicine_keywords):
        return "medicine_only"
    if any(kw in message_lower for kw in full_keywords) or (
        any(kw in message_lower for kw in disease_keywords) and
        any(kw in message_lower for kw in cause_keywords + symptom_keywords + treatment_keywords)
    ):
        return "full_disease_report"
    if any(kw in message_lower for kw in cause_keywords):
        return "disease_with_causes"
    if any(kw in message_lower for kw in symptom_keywords):
        return "disease_with_symptoms"
    if any(kw in message_lower for kw in treatment_keywords):
        return "disease_with_treatment"
    if any(kw in message_lower for kw in disease_keywords):
        return "disease"
    return "general"

# ---------------- GROQ CHAT FUNCTION ----------------
def groq_chat(messages, query_type="general"):
    """Send user messages to Groq with instructions based on query type."""
    if query_type == "disease":
        format_instruction = "<h2>Explanation</h2>Provide detailed explanation (8 lines)." \
                             "<h2>Summary</h2>Provide 2-3 line summary."
    elif query_type == "disease_with_causes":
        format_instruction = "<h2>Causes</h2> List and explain causes in points."
    elif query_type == "disease_with_symptoms":
        format_instruction = "<h2>Symptoms</h2> List symptoms in points."
    elif query_type == "disease_with_treatment":
        format_instruction = "<h2>Treatment</h2> List treatments in points."
    elif query_type == "medicine_only":
        format_instruction = "<h2>Medications</h2> List medicines, uses, dosage, precautions."
    elif query_type == "tips_only":
        format_instruction = "<h2>Tips / Advice</h2> Provide actionable tips."
    elif query_type == "doctor":
        format_instruction = "<h2>Recommended Specialist</h2> Provide suitable doctor/specialist."
    else:
        format_instruction = "Answer concisely using headings if relevant."

    system_prompt = {
        "role": "system",
        "content": f"You are a strict AI Healthcare Assistant. Respond ONLY to medical queries. {format_instruction}"
    }

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[system_prompt] + messages
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"Groq API error: {str(e)}"

# ---------------- CSV LOOKUP ----------------
def lookup_csv_exact(user_input: str):
    if df.empty or 'question' not in df.columns:
        return None
    user_norm = normalize_text(user_input)
    for _, row in df.iterrows():
        question_norm = normalize_text(str(row.get('question', '')))
        if user_norm == question_norm:
            return {
                "question": row.get('question', ''),
                "answer": row.get('answer', 'No answer available.'),
                "source": row.get('source', ''),
                "focus_area": row.get('focus_area', '')
            }
    return None

def format_csv_reply(item):
    """Return CSV as Question → Answer → Source → Focus Area without numbering"""
    parts = []
    if item.get('question'):
        parts.append(f"Question:\n{item['question']}")
    if item.get('answer'):
        parts.append(f"Answer:\n{item['answer']}")
    if item.get('source'):
        parts.append(f"Source:\n{item['source']}")
    if item.get('focus_area'):
        parts.append(f"Focus Area:\n{item['focus_area']}")
    return "\n\n".join(parts)

# ---------------- GREETINGS & FAREWELLS ----------------
def check_greetings_farewells(message: str) -> str:
    message_lower = message.lower()
    greetings = ["hello", "hi", "hey"]
    farewells = ["goodbye", "bye", "exit", "see you"]
    if any(g in message_lower for g in greetings):
        return "Hello! I'm here to assist you with your medical health and issues."
    elif any(f in message_lower for f in farewells):
        return "Goodbye! Take care, and feel free to reach out anytime with your health issues."
    return None

def check_gratitude(message: str) -> str:
    message_lower = message.lower()
    gratitude_keywords = ["thanks", "thank you", "thx","thnx", "thank u", "ty","thank you for this","thanks for this suggestion"]
    if any(kw in message_lower for kw in gratitude_keywords):
        return "You're welcome! I'm happy to help. Do you have any more medical questions?"
    return None

# ---------------- FORMAT POINTS ----------------
def format_points_universal(text: str) -> str:
    """
    Converts any list or structured content into:
    - Clean numbered points without bullets
    - Nested numbering for subsections
    This works for Causes, Symptoms, Treatment, Tips, Medications, etc.
    """
    if not text:
        return ""

    lines = text.split("\n")
    formatted = []
    main_counter = 1
    sub_counter = 1
    in_subsection = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove bullets, dashes, asterisks, extra spaces
        line = re.sub(r'^[\-\•\*\s]+', '', line)

        # Detect potential subsection header automatically
        if re.match(r'^[A-Z][A-Za-z0-9\s]*:$|^(Type \d+|Gestational|Other Forms?)', line):
            in_subsection = True
            sub_counter = 1
            formatted.append(f"{main_counter}. {line}")
            main_counter += 1
        elif in_subsection:
            formatted.append(f"   {sub_counter}. {line}")
            sub_counter += 1
        else:
            formatted.append(f"{main_counter}. {line}")
            main_counter += 1

    return "\n".join(formatted)

# ---------------- GET REPLY ----------------
def get_reply(messages):
    if not messages:
        return "No message received."

    last_message = messages[-1].get("content", "").strip()
    if not last_message:
        return "Please type a question."

    # CSV lookup first
    csv_item = lookup_csv_exact(last_message)
    if csv_item:
        reply = format_csv_reply(csv_item)
        reply = clean_groq_reply(reply)  # Clean markdown/HTML
        messages.append({"role": "assistant", "content": reply})
        return reply

    # Query type detection
    query_type = detect_query_type(last_message)

    # Greeting/farewell
    if query_type != "doctor":
        special_reply = check_greetings_farewells(last_message)
        if special_reply:
            messages.append({"role": "assistant", "content": special_reply})
            return special_reply
        
    # Gratitude check
        gratitude_reply = check_gratitude(last_message)
        if gratitude_reply:
            messages.append({"role": "assistant", "content": gratitude_reply})
            return gratitude_reply

    # Groq response
    reply = groq_chat(messages=[{"role": "user", "content": last_message}], query_type=query_type)
    reply = clean_groq_reply(reply)

    # Numbered formatting only for lists
    if query_type in ["disease_with_causes", "disease_with_symptoms", 
                      "disease_with_treatment", "medicine_only", "tips_only"]:
        reply = format_points_universal(reply)

    messages.append({"role": "assistant", "content": reply})
    return reply

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def chat_interface():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    html_content = ""
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    reply = get_reply(request.messages)
    return {"reply": reply}

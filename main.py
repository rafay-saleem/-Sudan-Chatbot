import streamlit as st
import pdfplumber
import re
import time
import os

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Sudan AI Chatbot",
    page_icon="🕶️",
    layout="centered"
)

# ====== STYLING ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Orbitron', sans-serif; background-color:#0b0c10; color:#f5f5f5; }

.title { font-size:3rem; font-weight:700; color:#ff4c4c; text-align:center; text-shadow:0 0 10px #ff0000,0 0 20px #ff4c4c; animation: neonGlow 1.5s ease-in-out infinite alternate;}
.subtitle {font-size:1.3rem; font-weight:600; color:#ff6b6b; text-align:center;}
.tagline {font-size:1rem; color:#ff7f7f; text-align:center;}
hr {border:none; height:2px; background:linear-gradient(to right,#ff4c4c,#ff0000); margin:1em 0; box-shadow:0 0 10px #ff0000;}

.user-msg {background-color:#1a0000;color:#ff4c4c;padding:10px;border-radius:10px;text-align:right;margin:5px 0;max-width:80%;word-wrap:break-word;}
.bot-msg {background-color:#330000;color:#ff7f7f;padding:10px;border-radius:10px;text-align:left;margin:5px 0;max-width:80%;word-wrap:break-word;animation: neonGlow 2s ease-in-out infinite alternate;}

.stButton>button {background-color:#1a0000;color:#ff4c4c;border:2px solid #ff0000;border-radius:12px;padding:0.5em 1.2em;font-weight:700;transition:all 0.3s ease;}
.stButton>button:hover {background-color:#ff0000;color:#0b0c10;transform:scale(1.05);}

input[type=text] {background-color:#1a0000;color:#ff4c4c;border:2px solid #ff0000;border-radius:12px;padding:10px;font-weight:600;width:100%;}

@keyframes neonGlow { from {text-shadow:0 0 5px #ff4c4c,0 0 10px #ff0000;} 
    to {text-shadow:0 0 20px #ff6b6b,0 0 30px #ff0000;} }

#chat-container { max-height:500px; overflow-y:auto; padding-right:10px; }
#related-container { display:flex; flex-wrap:wrap; gap:5px; margin-top:5px; }
.related-btn { background-color:#1a0000;color:#ff4c4c;border:2px solid #ff0000;border-radius:12px;padding:5px 10px;font-weight:600; cursor:pointer; }
.related-btn:hover { background-color:#ff0000;color:#0b0c10; transform:scale(1.05); }
</style>
""", unsafe_allow_html=True)

# ====== HEADER ======
st.markdown('<div class="title">🌍 Sudan AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Developed by Rafay Boss 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Ask in <b>English | Roman English | Urdu</b> (PDF knowledge only)</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ====== PDF LOADING ======
def load_pdf(file_path):
    text = ""
    if not file_path or not os.path.exists(file_path):
        return ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            ptxt = page.extract_text()
            if ptxt:
                text += re.sub(r'\n+', '\n', ptxt) + "\n"
    return text.lower()

pdf_path = "Circumstances of Sudan.pdf"
knowledge_base = load_pdf(pdf_path)
sentences = knowledge_base.split('\n')

# ====== LANGUAGE DETECTION ======
def detect_language(text):
    text = text.strip()
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return "urdu"
    roman_words = ["hai","kya","se","aur","nahi","ko","ki","ka","ke","kaun","kab","hae","ha"]
    if any(w in text.lower() for w in roman_words):
        return "roman"
    return "english"

# ====== RELATED TOPICS ======
related_topics = {
    "rsf": ["RSF origin","2019 conflict","Janjaweed","Government operations"],
    "sharia": ["Sharia law","1983 Nimeiri","Hudood laws","Second Civil War"],
    "south sudan": ["South Sudan independence","2011 secession","Oil divide","CPA 2005"],
    "oil": ["Oil disputes","North control","China pipelines","Revenue conflicts"],
    "civil war": ["First Civil War","Second Civil War","Anyanya","Addis Ababa Agreement"]
}

# ====== SESSION SAFE ======
if "messages" not in st.session_state: st.session_state.messages = []
if "last_user_input" not in st.session_state: st.session_state.last_user_input = ""

# ====== SHOW CHAT ======
def show_chat():
    st.markdown('<div id="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        cls = "user-msg" if m["role"]=="user" else "bot-msg"
        st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

show_chat()

# ====== USER INPUT ======
user_input = st.text_input("💬 Type your question here...", key="user_input")

# ====== HELPER FUNCTIONS ======
def find_sentences(query):
    query_words = re.findall(r'\w+', query.lower())
    matched = []
    for s in sentences:
        if all(w in s for w in query_words):
            matched.append(s.strip())
    # Merge multiple paragraphs if more than 1 sentence
    if len(matched) > 1:
        return " ".join(matched[:5])  # top 5 matches
    elif matched:
        return matched[0]
    else:
        return ""

def suggest_related(query):
    query_lower = query.lower()
    suggestions = []
    for key, vals in related_topics.items():
        if key in query_lower:
            suggestions.extend(vals)
    return list(dict.fromkeys(suggestions))[:5]  # max 5 unique suggestions

# ====== PROCESS INPUT ======
def process_input(query):
    if query.strip() == "" or query.strip() == st.session_state.last_user_input:
        return
    st.session_state.last_user_input = query.strip()
    st.session_state.messages.append({"role":"user","content":query})
    lang = detect_language(query)

    # PDF SEARCH LOGIC
    answer = find_sentences(query)
    if not answer:
        answer = {"english":"I have no info about that.",
                  "roman":"Mujhe iske bare mein info nahi mili.",
                  "urdu":"مجھے اس کے بارے میں معلومات نہیں ملی۔"}[lang]

    # ====== TYPING EFFECT ======
    placeholder = st.empty()
    txt = ""
    for ch in answer:
        txt += ch
        placeholder.markdown(f"<div class='bot-msg'>{txt}</div>", unsafe_allow_html=True)
        time.sleep(0.005)

    st.session_state.messages.append({"role":"assistant","content":answer})

    # ====== RELATED QUESTIONS ======
    suggestions = suggest_related(query)
    if suggestions:
        st.markdown('<div id="related-container">', unsafe_allow_html=True)
        for q in suggestions:
            if st.button(q, key=q):
                process_input(q)
        st.markdown('</div>', unsafe_allow_html=True)

process_input(user_input)
show_chat()

# ====== AUTO SCROLL ======
st.markdown("""
<script>
var chat = window.parent.document.getElementById('chat-container');
if(chat){ chat.scrollTop = chat.scrollHeight; }
</script>
""", unsafe_allow_html=True)

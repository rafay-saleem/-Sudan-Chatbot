import streamlit as st
from difflib import get_close_matches
from transformers import pipeline
import pdfplumber
import os
import time
import re

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Sudan AI Chatbot",
    page_icon="🕶️",
    layout="centered"
)

# ====== STYLING (RED + BLACK NEON) ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

html, body, [class*="css"] { font-family:'Orbitron', sans-serif; background-color:#0b0c10; color:#f5f5f5; }

.title { font-size:3rem; font-weight:700; color:#ff4c4c; text-align:center;
    text-shadow:0 0 10px #ff0000,0 0 20px #ff4c4c; animation: neonGlow 1.5s ease-in-out infinite alternate;}
.subtitle {font-size:1.3rem; font-weight:600; color:#ff6b6b; text-align:center;}
.tagline {font-size:1rem; color:#ff7f7f; text-align:center;}
hr {border:none; height:2px; background:linear-gradient(to right,#ff4c4c,#ff0000); margin:1em 0; box-shadow:0 0 10px #ff0000;}

.user-msg {background-color:#1a0000;color:#ff4c4c;padding:10px;border-radius:10px;text-align:right;margin:5px 0;max-width:80%;word-wrap:break-word;}
.bot-msg {background-color:#330000;color:#ff7f7f;padding:10px;border-radius:10px;text-align:left;margin:5px 0;max-width:80%;word-wrap:break-word;animation: neonGlow 2s ease-in-out infinite alternate;}

.stButton>button {background-color:#1a0000;color:#ff4c4c;border:2px solid #ff0000;border-radius:12px;padding:0.5em 1.2em;font-weight:700;transition:all 0.3s ease;}
.stButton>button:hover {background-color:#ff0000;color:#0b0c10;transform:scale(1.05);}

@keyframes neonGlow { from {text-shadow:0 0 5px #ff4c4c,0 0 10px #ff0000;} 
    to {text-shadow:0 0 20px #ff6b6b,0 0 30px #ff0000;} }

#chat-container { max-height:500px; overflow-y:auto; padding-right:10px; }
</style>
""", unsafe_allow_html=True)

# ====== HEADER ======
st.markdown('<div class="title">🌍 Sudan AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Developed by Rafay Boss 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Ask in <b>English | Roman English | Urdu</b> (PDF + AI fallback)</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ====== INTENTS + KEYWORDS ======
intents = {
    "history_sudan": ["history of sudan","pre-independence","first cold war","independence 1956","north south divide","civil war","post-independence","leaders","generals","resources","coups","oil","rsf","sharia","south sudan"],
    "rsf_origin": ["rsf origin","rapid support forces","janjaweed","rsf formed","rsf history","rsf conflict"],
    "sharia_law": ["sharia law","1983 sharia","nimeiri sharia","hudood laws","sharia imposed"],
    "south_sudan": ["south sudan independence","2011 south sudan","secession","south autonomy"],
    "oil_conflict": ["oil divide","china oil pipeline","north control oil","south resources","oil disputes","oil revenue","resources control"],
    "civil_wars": ["first civil war","second civil war","anya nya","civil war casualties","rebellion","conflict","addis ababa","cpa"],
}

# ====== PDF LOADING ======
def load_pdf_text(file_path):
    txt="" 
    if os.path.exists(file_path):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_txt = page.extract_text()
                if page_txt:
                    txt += re.sub(r'\n+', '\n', page_txt) + "\n"
    return txt.lower()

knowledge_base = load_pdf_text("Circumstances of Sudan.pdf")

# ====== AI FALLBACK ======
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# ====== LANGUAGE DETECTION ======
def detect_language(text):
    text = text.strip()
    if any('\u0600' <= ch <= '\u06FF' for ch in text): return "urdu"
    roman_words = ["hai","kya","se","aur","nahi","ko","ki","ka","ke","kaun","kab","hae","ha"]
    if any(w in text.lower() for w in roman_words): return "roman"
    return "english"

# ====== INTENT MATCH ======
def detect_intent(text):
    text = text.lower()
    for intent, keywords in intents.items():
        for k in keywords:
            if k in text: return intent
        if get_close_matches(text, keywords, n=1, cutoff=0.6):
            return intent
    return "unknown"

# ====== SESSION SAFE HISTORY ======
if "messages" not in st.session_state: st.session_state.messages = []

# ====== SHOW CHAT ======
st.markdown('<div id="chat-container">', unsafe_allow_html=True)
for m in st.session_state.messages:
    cls = "user-msg" if m["role"]=="user" else "bot-msg"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ====== USER INPUT ======
user_input = st.text_area("Type your question here...", height=70, key="user_input", placeholder="Ask in English | Roman | Urdu")

if st.button("Send") and user_input.strip()!="":
    st.session_state.messages.append({"role":"user","content":user_input})
    lang = detect_language(user_input)
    intent = detect_intent(user_input)

    reply = ""
    if intent == "history_sudan":
        # Full timeline summary
        reply = ("Sudan's History (Pre & Post Independence):\n\n"
                 "- Pre-independence: First Cold War era, Anyanya rebellion, North-South cultural and religious tensions, 1955 mutiny.\n"
                 "- Independence: 1 January 1956, Ismail al-Azhari became first Prime Minister.\n"
                 "- Post-independence conflicts: Political instability, generals' fights, coups, and resource disputes.\n"
                 "- First Civil War (1955-1972): Southern autonomy struggle, Anyanya movement, ended with Addis Ababa Agreement.\n"
                 "- Second Civil War (1983-2005): Sharia law imposed by Nimeiri, John Garang leads SPLA, massive casualties (~2 million) and displacement (~4-5 million), ended with CPA 2005.\n"
                 "- RSF Origin: Emerged from Janjaweed militias, involved in 2019 conflicts.\n"
                 "- Oil & Resources: North controlled most oil, pipelines built by China, disputes contributed to South Sudan independence.\n"
                 "- South Sudan Independence: 2011, formal secession after second civil war.\n"
                 "- Current Sudan: Continued tensions, coups, resource conflicts, international attention limited.")
    elif intent in ["rsf_origin","sharia_law","south_sudan","oil_conflict","civil_wars"]:
        try:
            qa = qa_pipeline(question=user_input, context=knowledge_base)
            if qa['score'] < 0.2:
                reply = {"english":"I have no info about that.",
                         "roman":"Mujhe iske bare mein info nahi mili.",
                         "urdu":"مجھے اس کے بارے میں معلومات نہیں ملی۔"}[lang]
            else:
                reply = qa['answer']
        except:
            reply = {"english":"I have no info about that.",
                     "roman":"Mujhe iske bare mein info nahi mili.",
                     "urdu":"مجھے اس کے بارے میں معلومات نہیں ملی۔"}[lang]
    else:
        try:
            qa = qa_pipeline(question=user_input, context=knowledge_base)
            if qa['score'] < 0.2:
                reply = {"english":"I have no info about that.",
                         "roman":"Mujhe iske bare mein info nahi mili.",
                         "urdu":"مجھے اس کے بارے میں معلومات نہیں ملی۔"}[lang]
            else:
                reply = qa['answer']
        except:
            reply = {"english":"I have no info about that.",
                     "roman":"Mujhe iske bare mein info nahi mili.",
                     "urdu":"مجھے اس کے بارے میں معلومات نہیں ملی۔"}[lang]

    # ====== TYPING EFFECT ======
    placeholder = st.empty()
    txt=""
    for ch in reply:
        txt += ch
        placeholder.markdown(f"<div class='bot-msg'>{txt}</div>", unsafe_allow_html=True)
        time.sleep(0.005)

    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.user_input=""

# ====== AUTO SCROLL ======
st.markdown("""
<script>
var chat = window.parent.document.getElementById('chat-container');
if(chat){ chat.scrollTop = chat.scrollHeight; }
</script>
""", unsafe_allow_html=True)

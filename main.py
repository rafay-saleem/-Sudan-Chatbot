import streamlit as st
from difflib import get_close_matches
from transformers import pipeline
import pdfplumber
import os
import time

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Sudan AI Chatbot",
    page_icon="🕶️",
    layout="centered"
)

# ====== CUSTOM STYLING (MAFIA LOOK + NEON ANIMATION) ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
    background-color: #0b0c10;
    color: #c5c6c7;
}

/* Neon header glow */
.title {
    font-size: 3rem;
    font-weight: 700;
    color: #66fcf1;
    text-align: center;
    text-shadow: 0 0 10px #45a29e, 0 0 20px #45a29e;
    margin-bottom: 0.2em;
    animation: neonGlow 1.5s ease-in-out infinite alternate;
}

.subtitle {
    font-size: 1.4rem;
    font-weight: 600;
    color: #f1c40f;
    text-align: center;
    text-shadow: 0 0 5px #f39c12;
}

.tagline {
    font-size: 1rem;
    color: #95a5a6;
    text-align: center;
    margin-top: 0.8em;
}

hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #66fcf1, #45a29e);
    margin: 1.5em 0;
    box-shadow: 0 0 10px #45a29e;
}

/* Chat bubbles */
.user-msg {
    background-color:#1f2833; 
    color:#66fcf1;
    padding:10px; 
    border-radius:10px; 
    text-align:right; 
    margin:5px 0;
    max-width: 80%;
    word-wrap: break-word;
}

.bot-msg {
    background-color:#45a29e; 
    color:#0b0c10;
    padding:10px; 
    border-radius:10px; 
    text-align:left; 
    margin:5px 0;
    max-width: 80%;
    word-wrap: break-word;
    animation: neonGlow 2s ease-in-out infinite alternate;
}

/* Button style */
.stButton>button {
    background-color: #1f2833;
    color: #66fcf1;
    border: 2px solid #45a29e;
    border-radius: 12px;
    padding: 0.5em 1.2em;
    font-weight: 700;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: #45a29e;
    color: #0b0c10;
    transform: scale(1.05);
    box-shadow: 0 0 10px #66fcf1;
}

/* Neon glow animation */
@keyframes neonGlow {
    from { text-shadow: 0 0 5px #45a29e, 0 0 10px #45a29e; }
    to { text-shadow: 0 0 20px #66fcf1, 0 0 30px #66fcf1; }
}

/* Scrollable chat window */
#chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
</style>
""", unsafe_allow_html=True)

# ====== HEADER ======
st.markdown('<div class="title">🌍 Sudan AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Developed by Rafay Boss 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Ask in <b>English | Roman English | اردو</b> (PDF + AI fallback)</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ====== INTENTS & RESPONSES (FULL ORIGINAL) ======
# Paste your full intents, responses, related_facts here (same as previous full version)
# For brevity, not repeating them here, just reuse your previous full lists.
intents = {
    "independence": ["sudan independence", "1956", "anglo egyptian", "egypt monarchy 1952", "sudanization 1953", "1 january 1956", "sudan free without war", "independence date"],
    "divide_break": ["sudan break", "north south divide", "culture religion different", "north muslim", "south christian", "discrimination"],
    "first_civil_war": ["first civil war", "pehli civil war", "1955 1972", "anya nya", "rebellion start", "south fear north"],
    "force_rule_reasons": ["force rule why", "political power denied", "culture imposed", "military control", "promises broken"],
    "culture_imposed": ["culture imposed", "arabic compulsory", "islamic national", "christian ignored", "language suppressed"],
    "military_control": ["military control", "mutiny 1955", "extra troops", "protests suppressed", "occupied territory"],
    "promises_broken": ["promises broken", "federal system denied", "autonomy promises", "identity ignored", "north cancel agreements"],
    "first_pm": ["first prime minister", "ismail al-azhari", "parliamentary system"],
    "abboud_coup": ["abboud coup", "1958 government overthrown", "civilian weak", "south crisis coup"],
    "anya_nya_movement": ["anya nya", "anya nya movement", "snake venom", "anya nya what did"],
    "second_civil_war": ["second civil war", "1983 2005", "nimeiri sharia", "john garang", "oil divide"],
    "sharia_law": ["sharia law", "september laws", "hudood", "nimeiri sharia", "1983 sharia"],
    "sharia_results": ["sharia results", "sharia implement after", "sharia consequences"],
    "rsf_origin": ["rsf origin", "janjaweed", "rsf formed", "rsf reason"],
    "saf_origin": ["saf origin", "sudanese armed forces history"],
    "rsf_saf_conflict": ["rsf saf conflict", "bashir removed", "2019 coup"],
    "sudan_famine": ["famine reasons", "qahet", "sudan hunger"],
    "civil_war_casualties": ["casualties", "deaths", "missing"],
    "addis_ababa": ["addis ababa", "1972 agreement", "south autonomy"],
    "south_sudan_independence": ["south sudan independence", "2011 independence"],
    "north_current": ["north sudan current", "sudan now"],
    "why_silent": ["world silent sudan", "duniya khamosh kyun"],
    "oil_qabza": ["oil resources control", "north south oil", "why no independence oil"],
    "third_civil_war": ["third civil war", "2023 war", "rsf saf war"],
    "john_garang": ["john garang", "garang biography"],
}

responses = {
    "independence": {
        "english": "Sudan gained independence on 1 January 1956 from Anglo-Egyptian control without a major war. Egypt ended monarchy in 1952, elections in 1953 started Sudanization. Ismail al-Azhari was the first PM. Related: This peaceful transition contrasted with later civil wars due to North-South divide.",
        "roman": "Sudan 1 January 1956 mein Anglo-Egyptian rule se azad hua bina major war ke. 1952 Egypt monarchy khatam, 1953 elections Sudanization shuru. Ismail al-Azhari first PM. Related: Peaceful azadi vs later North-South conflicts.",
        "urdu": "سوڈان 1 جنوری 1956 کو آزاد ہوا بغیر جنگ کے۔ 1952 میں مصر نے بادشاہت ختم کی، 1953 میں انتخابات کے ذریعے Sudanization شروع ہوئی۔ اسماعیل الازہری پہلا وزیراعظم۔ متعلقہ: یہ پرامن آزادی بعد کی جنگوں سے مختلف۔"
    },
    "anya_nya_movement": {
        "english": "Anya Nya Movement (Anyanya) means 'snake venom'. Formed in 1963 during First Civil War as Southern rebel group. Guerrilla warfare, ambushes, resistance for Southern rights and autonomy. Included teachers, students, farmers, ex-soldiers. Led to Addis Ababa Agreement 1972. Related: Fighters merged into army after 1972, many later joined SPLA in 1983.",
        "roman": "Anya Nya Movement matlab 'snake venom'. 1963 First Civil War me Southern rebel group bani. Guerrilla warfare, ambushes, resistance for Southern rights aur autonomy. Teachers, students, farmers, ex-soldiers involved. Led to Addis Ababa 1972. Related: Fighters merged army after 1972, many joined SPLA 1983.",
        "urdu": "انیا نیا موومنٹ کا مطلب 'سانپ کا زہر'. 1963 میں پہلی خانہ جنگی میں جنوبی بغاوت. گوریلا جنگ، شمالی فوج کے خلاف مزاحمت، جنوبی حقوق اور خودمختاری کے لیے. اس میں اساتذہ، طلبہ، کسان، سابق فوجی شامل تھے. 1972 میں Addis Ababa Agreement۔"
    },
    "second_civil_war": {
        "english": "Second Civil War (1983-2005) began when Nimeiri broke the Addis Ababa Agreement, imposed Sharia law, divided oil-rich states. Led by John Garang and SPLA. Casualties: ~2 million dead, 4-5 million displaced/missing. Ended with CPA 2005, leading to South Sudan independence in 2011.",
        "roman": "Second Civil War 1983-2005 Nimeiri ne Addis Ababa toda, Sharia lagaya, oil divide. John Garang SPLA leader. Casualties: ~2 million dead, 4-5 million displaced. Ended CPA 2005, South Sudan independence 2011.",
        "urdu": "دوسری جنگ 1983-2005, نمیری نے معاہدہ توڑا، شریعہ لگایا، تیل کے علاقے تقسیم. جان گارنگ SPLA لیڈر. تقریبا 2 لاکھ ہلاک، 4-5 لاکھ بے گھر. CPA 2005 کے ساتھ ختم، جنوبی سوڈان 2011 میں آزاد۔"
    },
}

related_facts = {
    "independence": "Related: Peaceful azadi 1956, North-South divide tension started. First deprivation 1955 mutiny.",
    "anya_nya_movement": "Related: Formed 1963, guerrilla warfare for rights. Led to 1972 Addis Ababa Agreement.",
    "second_civil_war": "Related: ~2 million dead, 4-5 million displaced. Led by John Garang. CPA 2005 ended, South Sudan 2011.",
}

# ====== LANGUAGE DETECTION ======
def detect_language(text):
    text = text.lower()
    if any('\u0600' <= ch <= '\u06FF' for ch in text):
        return "urdu"
    roman_words = ["hai","kya","ka","ki","ke","nahi","ho","raha","tha","thi","se","ne","ko","aur","bani","howa","azad","huan","hogi","kase","kb","hua"]
    if sum(1 for w in roman_words if w in text) >= 1:
        return "roman"
    return "english"

# ====== INTENT MATCHING ======
def detect_intent(text):
    text = text.lower()
    for intent, keywords in intents.items():
        matches = get_close_matches(text, keywords, n=1, cutoff=0.5)
        if matches:
            return intent
    return "unknown"

# ====== PDF LOADING ======
def load_pdf_text(file_path):
    pdf_text = ""
    if os.path.exists(file_path):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    pdf_text += txt + "\n"
    return pdf_text.lower()

pdf_path = "Circumstances of Sudan.pdf"
knowledge_base = load_pdf_text(pdf_path)

# ====== AI FALLBACK ======
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# ====== SESSION STATE ======
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====== SCROLLABLE CHAT CONTAINER ======
st.markdown('<div id="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    role_class = "user-msg" if message["role"]=="user" else "bot-msg"
    st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ====== MULTI-LINE USER INPUT ======
user_input = st.text_area("Type your question here...", key="user_input", placeholder="Ask in English | Roman | Urdu", height=70)

# ====== PROCESS INPUT ======
if st.button("Send") and user_input.strip() != "":
    st.session_state.messages.append({"role":"user","content":user_input})
    lang = detect_language(user_input)
    intent = detect_intent(user_input)
    
    # Generate bot reply
    if intent != "unknown" and intent in responses:
        if len(user_input.split()) <= 4:
            reply = responses[intent][lang].split(".")[0] + "."
        else:
            reply = responses[intent][lang]
            if intent in related_facts:
                reply += "\n\n" + related_facts[intent]
    else:
        try:
            qa = qa_pipeline(question=user_input, context=knowledge_base)
            reply = qa['answer']
        except:
            reply = {
                "english":"I understand the topic, but this specific question is not yet mapped.",
                "roman":"Main topic samajh raha hoon, lekin yeh sawal abhi exact map nahi hua.",
                "urdu":"میں موضوع سمجھ رہا ہوں، لیکن یہ سوال ابھی مکمل طور پر میپ نہیں ہوا۔"
            }[lang]

    # Typing effect simulation
    bot_message_placeholder = st.empty()
    bot_text = ""
    for char in reply:
        bot_text += char
        bot_message_placeholder.markdown(f"<div class='bot-msg'>{bot_text}</div>", unsafe_allow_html=True)
        time.sleep(0.01)  # Adjust typing speed
    
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.user_input = ""

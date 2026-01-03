import streamlit as st
from difflib import get_close_matches
from transformers import pipeline
import pdfplumber
import os


st.set_page_config(
    page_title="Sudan AI Chatbot",
    page_icon="🌍",
    layout="centered"
)

# ====== CUSTOM STYLING ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.main {
    background-color: #0f172a;
    color: #e5e7eb;
}

.title {
    font-size: 3rem;
    font-weight: 700;
    color: #38bdf8;
    text-align: center;
    margin-bottom: 0.2em;
}

.subtitle {
    font-size: 1.4rem;
    font-weight: 600;
    color: #facc15;
    text-align: center;
}

.tagline {
    font-size: 1rem;
    color: #cbd5f5;
    text-align: center;
    margin-top: 0.8em;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, #38bdf8, #6366f1);
    margin: 1.5em 0;
}
</style>
""", unsafe_allow_html=True)

# ====== HEADER ======
st.markdown('<div class="title">🌍 Sudan AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Developed by Rafay Boss 🚀</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="tagline">Ask in <b>English | Roman English | اردو</b> (PDF + AI fallback)</div>',
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)


# =========================
# INTENTS & RESPONSES
# =========================
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

# =========================
# LANGUAGE DETECTION
# =========================
def detect_language(text):
    text = text.lower()
    if any('\u0600' <= ch <= '\u06FF' for ch in text):
        return "urdu"
    roman_words = ["hai","kya","ka","ki","ke","nahi","ho","raha","tha","thi","se","ne","ko","aur","ku","bani","howa","azad","huan","hogi","kase","kb","hua"]
    if sum(1 for w in roman_words if w in text) >= 1:
        return "roman"
    return "english"

# =========================
# INTENT MATCHING (FUZZY)
# =========================
def detect_intent(text):
    text = text.lower()
    for intent, keywords in intents.items():
        matches = get_close_matches(text, keywords, n=1, cutoff=0.5)
        if matches:
            return intent
    return "unknown"

# =========================
# PDF LOADING FUNCTION
# =========================
def load_pdf_text(file_path):
    pdf_text = ""
    if os.path.exists(file_path):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    pdf_text += txt + "\n"
    return pdf_text.lower()

# Load PDF
pdf_path = "Circumstances of Sudan.pdf"
knowledge_base = load_pdf_text(pdf_path)

# =========================
# AI FALLBACK
# =========================
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# =========================
# STREAMLIT UI (MODERNIZED)
# =========================
st.set_page_config(page_title="Sudan Research Chatbot", page_icon="🌍", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
.stApp {background-color: #F2F3F4; font-family: 'Arial', sans-serif;}
.user-msg {background-color:#85C1E9; padding:10px; border-radius:10px; text-align:right; margin:5px 0;}
.bot-msg {background-color:#ABEBC6; padding:10px; border-radius:10px; text-align:left; margin:5px 0;}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>🌍 Sudan AI Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #34495E;'>Developed by <b>Rafay Boss 🚀</b></p>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("Ask in **English | Roman English | اردو** (PDF + AI fallback)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat ---
for message in st.session_state.messages:
    role_class = "user-msg" if message["role"]=="user" else "bot-msg"
    st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)

# --- User input ---
user_input = st.text_input("Type your question here...", key="user_input", placeholder="Ask in English | Roman | Urdu")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})


# --- Process input ---
if st.session_state.messages and st.session_state.messages[-1]["role"]=="user":
    user_text = st.session_state.messages[-1]["content"]
    lang = detect_language(user_text)
    intent = detect_intent(user_text)

    if intent != "unknown" and intent in responses:
        if len(user_text.split()) <= 4:
            reply = responses[intent][lang].split(".")[0] + "."
        else:
            reply = responses[intent][lang]  
            if intent in related_facts:
                reply += "\n\n" + related_facts[intent]
    else:
        try:
            qa = qa_pipeline(question=user_text, context=knowledge_base)
            reply = qa['answer']
        except:
            reply = {
                "english":"I understand the topic, but this specific question is not yet mapped.",
                "roman":"Main topic samajh raha hoon, lekin yeh sawal abhi exact map nahi hua.",
                "urdu":"میں موضوع سمجھ رہا ہوں، لیکن یہ سوال ابھی مکمل طور پر میپ نہیں ہوا۔"
            }[lang]

    st.session_state.messages.append({"role":"assistant","content":reply})
    st.experimental_rerun()

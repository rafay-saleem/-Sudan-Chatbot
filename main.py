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
    "independence": ["sudan independence","1956","anglo egyptian","sudan free","first pm"],
    "north_south_divide": ["north south divide","south sudan","divide reasons","sudan split","south independence"],
    "first_civil_war": ["first civil war","1955 1972","anya nya","anya nya movement","rebellion start"],
    "second_civil_war": ["second civil war","1983 2005","nimeiri","addis ababa","civil casualties"],
    "rsf_origin": ["rsf origin","janjaweed","rapid support forces","rsf formed","rsf history"],
    "saf_origin": ["saf origin","sudanese armed forces","saf history"],
    "rsf_saf_conflict": ["rsf saf conflict","2019 conflict","bashir removed","coup 2019"],
    "sharia_law": ["sharia law","september laws","hudood","1983 sharia"],
    "oil_resources": ["oil","oil divide","china oil pipeline","oil control north south"],
    "addis_ababa": ["addis ababa agreement","1972 agreement","south autonomy"],
    "civil_war_casualties": ["casualties","deaths","missing","war cost"],
}

# ====== RESPONSES ======
responses = {
    "independence": {
        "english":"Sudan gained independence on 1 January 1956 from Anglo-Egyptian colonial rule. Ismail al-Azhari became the first Prime Minister.",
        "roman":"Sudan 1 January 1956 ko Anglo-Egyptian control se azaad hua. Ismail al-Azhari pehle PM bane.",
        "urdu":"سوڈان 1 جنوری 1956 کو اینگلو-مصری حکمرانی سے آزاد ہوا۔ اسماعیل الازہری پہلے وزیراعظم تھے۔"
    },
    "north_south_divide": {
        "english":"The North-South divide in Sudan was due to cultural, religious and economic differences. It eventually led to the secession and creation of South Sudan in 2011.",
        "roman":"Sudan ka North-South divide cultural, religious aur economic differences ki wajah se tha. 2011 mein South Sudan ban gaya.",
        "urdu":"سوڈان میں شمال-جنوب تقسیم ثقافتی، مذہبی اور اقتصادی اختلافات کی وجہ سے تھی۔ 2011 میں جنوبی سوڈان بن گیا۔"
    },
    "first_civil_war": {
        "english":"The First Sudanese Civil War (1955–1972) began before independence and involved the Anyanya movement fighting for Southern autonomy. It ended with the Addis Ababa Agreement in 1972.",
        "roman":"First Civil War (1955-1972) independence se pehle shuru hui, Anyanya movement ne Southern autonomy ke liye laraai ki. 1972 mein Addis Ababa Agreement se khatam hui.",
        "urdu":"پہلی خانہ جنگی (1955-1972) آزادی سے پہلے شروع ہوئی، انیا نیا موومنٹ نے جنوبی خودمختاری کے لیے لڑائی کی۔ 1972 میں Addis Ababa Agreement سے ختم ہوئی۔"
    },
    "second_civil_war": {
        "english":"The Second Civil War (1983–2005) started when Sharia laws were imposed and the Addis Ababa Agreement was broken. It caused massive casualties and displacement.",
        "roman":"Second Civil War (1983-2005) tab shuru hui jab Sharia laws lagaye gaye aur Addis Ababa Agreement toda gaya. Bahut nuksan hua.",
        "urdu":"دوسری خانہ جنگی (1983-2005) شریعہ قوانین کے نفاذ اور Addis Ababa معاہدہ کے خلاف ورزی پر شروع ہوئی۔ بہت نقصان ہوا۔"
    },
    "rsf_origin": {
        "english":"The Rapid Support Forces (RSF) originated from the Janjaweed militias. They were later formalized into a paramilitary force.",
        "roman":"RSF Janjaweed militias se bani. Baad mein paramilitary force mein convert hui.",
        "urdu":"ریپڈ سپورٹ فورس (RSF) جانجاویڈ ملیشیاز سے بنی۔ بعد میں اسے پیرا ملٹری فورس میں تبدیل کیا گیا۔"
    },
    "rsf_saf_conflict": {
        "english":"RSF and Sudan Armed Forces (SAF) have been in conflict, especially after the 2019 coup and power struggles that followed. This caused widespread violence.",
        "roman":"RSF aur SAF ke beech takraar rahi, khaaskar 2019 ke coup ke baad. Is se bohot hinsa hui.",
        "urdu":"RSF اور SAF کے درمیان تنازع خصوصاً 2019 کے بغاوت کے بعد جاری رہا۔ اس سے بہت ہنگامہ ہوا۔"
    },
    "sharia_law": {
        "english":"Sharia law was imposed in 1983 under President Nimeiri, affecting many legal and social systems, and contributing to the Second Civil War.",
        "roman":"Sharia law 1983 mein Nimeiri ke daur mein lage. Is ne muashray aur kanoon par barha asar dala.",
        "urdu":"شریعہ قانون 1983 میں نمیری کے دور میں لاگو ہوا۔ اس نے سماجی اور قانونی نظام پر اثر ڈالا۔"
    },
    "oil_resources": {
        "english":"Oil resources in Sudan were a central cause of tension. Much of the infrastructure, including pipelines, was developed with foreign partners like China.",
        "roman":"Sudan ke oil resources ne tensions ko barhaya. Pipelines aur infrastructure China jaise partners ke sath banai gayi.",
        "urdu":"سوڈان کے تیل کے وسائل نے کشیدگی میں اضافہ کیا۔ پائپ لائنیں اور بنیادی ڈھانچہ چین جیسے شراکت داروں کے ساتھ بنایا گیا۔"
    },
    "addis_ababa": {
        "english":"The Addis Ababa Agreement (1972) ended the First Civil War and granted autonomy to the South for a period.",
        "roman":"Addis Ababa Agreement (1972) ne First Civil War ko khatam kiya aur South ko autonomy di.",
        "urdu":"Addis Ababa معاہدہ (1972) نے پہلی خانہ جنگی ختم کی اور جنوبی کو خودمختاری دی۔"
    },
    "civil_war_casualties": {
        "english":"Sudanese civil wars caused millions of deaths and displacement of communities across decades.",
        "roman":"Sudan ki civil wars ne laakhon logon ki jaan li aur qabeelay displaced hue.",
        "urdu":"سوڈان کی خانہ جنگیوں نے لاکھوں جانیں لیں اور لوگ بے گھر ہوئے۔"
    },
}

related_facts = {
    "independence":"Related: 1955 mutiny, peaceful transition, rise of national parties.",
    "north_south_divide":"Related: Cultural divide, resource disputes, missionary education differences.",
    "first_civil_war":"Related: Ended with Addis Ababa Agreement, reintegration of fighters.",
    "second_civil_war":"Related: Led to comprehensive peace process and finally South Sudan independence in 2011.",
    "rsf_origin":"Related: RSF played key roles in later conflicts including 2023 war.",
    "sharia_law":"Related: Hudood ordinances, resistance in non-Muslim regions.",
    "oil_resources":"Related: Oil revenue disputes, international involvement.",
    "addis_ababa":"Related: One of the major peace accords before 2011.",
    "civil_war_casualties":"Related: Lasting impacts on health, economy and social structures.",
}

# ====== LANGUAGE DETECTION ======
def detect_language(text):
    t = text.lower()
    if any('\u0600' <= ch <= '\u06FF' for ch in t): return "urdu"
    roman = ["hai","kya","se","aur","nahi","ko","ki","ka","ke","kaun","kab"]
    if any(w in t for w in roman): return "roman"
    return "english"

# ====== INTENT MATCHING ======
def detect_intent(text):
    t = text.lower()
    for intent, keywords in intents.items():
        for k in keywords:
            if k in t or get_close_matches(t, [k], n=1, cutoff=0.3):
                return intent
    return "unknown"

# ====== PDF LOADING ======
def load_pdf_text(file_path):
    txt="" 
    if os.path.exists(file_path):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                data = page.extract_text()
                if data: txt+=data+"\n"
    return txt.lower()

knowledge_base = load_pdf_text("Circumstances of Sudan.pdf")

# ====== AI FALLBACK ======
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# ====== SESSION SAFE HISTORY ======
if "messages" not in st.session_state: st.session_state.messages = []

# ====== SHOW CHAT ======
st.markdown('<div id="chat-container">', unsafe_allow_html=True)
for m in st.session_state.messages:
    cls = "user-msg" if m["role"]=="user" else "bot-msg"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ====== AUTO-SCROLL ======
st.markdown("""
<script>
var chat = window.parent.document.getElementById('chat-container');
if(chat){ chat.scrollTop = chat.scrollHeight; }
</script>
""", unsafe_allow_html=True)

# ====== USER INPUT ======
user_input = st.text_area("Type your question here...", height=70, key="user_input", placeholder="Ask in English | Roman | Urdu")

if st.button("Send") and user_input.strip()!="":
    st.session_state.messages.append({"role":"user","content":user_input})
    lang = detect_language(user_input)
    intent = detect_intent(user_input)

    if intent!="unknown" and intent in responses:
        reply = responses[intent][lang]
        if intent in related_facts: reply += "\n\n" + related_facts[intent]
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

    placeholder = st.empty()
    txt=""
    for ch in reply:
        txt += ch
        placeholder.markdown(f"<div class='bot-msg'>{txt}</div>", unsafe_allow_html=True)
        time.sleep(0.01)

    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.user_input = ""

import streamlit as st
import pickle
import pandas as pd
import random

# -------------------- SESSION STATE INIT --------------------
if "questions" not in st.session_state:
    st.session_state.questions = []
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "generated" not in st.session_state:
    st.session_state.generated = False

# IMPORTANT: scores must exist BEFORE sliders
if "qa_score" not in st.session_state:
    st.session_state.qa_score = 50
if "varc_score" not in st.session_state:
    st.session_state.varc_score = 50
if "di_score" not in st.session_state:
    st.session_state.di_score = 50
if "lr_score" not in st.session_state:
    st.session_state.lr_score = 50

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="CAT Prep AI", layout="centered")

# -------------------- UI --------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #dbeafe, #f0fdf4);
}
.main-title {
    font-size:40px;
    font-weight:800;
    text-align:center;
    color:#4f46e5;
}
.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0px 8px 20px rgba(0,0,0,0.08);
    margin-bottom:20px;
}
div.stButton > button {
    background: linear-gradient(90deg, #6366f1, #22c55e);
    color: white;
    border-radius: 12px;
    height: 3em;
}
.streak {
    font-size:20px;
    font-weight:700;
    color:#f59e0b;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODELS --------------------
weak_model = pickle.load(open('adaptive_weak_topic_model_large.pkl','rb'))

# -------------------- TITLE --------------------
st.markdown('<div class="main-title">🎯 AI CAT Prep Assistant</div>', unsafe_allow_html=True)

# -------------------- INPUT --------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.header("📊 Enter Your Mock Scores")

# KEY FIX: bind sliders to session_state
qa = st.slider("QA Score", 0, 100, key="qa_score")
varc = st.slider("VARC Score", 0, 100, key="varc_score")
di = st.slider("DI Score", 0, 100, key="di_score")
lr = st.slider("LR Score", 0, 100, key="lr_score")

lessons_done = st.slider("Lessons Completed", 0, 20, 5)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- BUTTON --------------------
if st.button("✨ Generate Analysis"):
    st.session_state.generated = True
    st.session_state.questions = []

# -------------------- MAIN FLOW --------------------
if st.session_state.generated:

    # -------------------- MODEL --------------------
    min_score = min(qa, varc, di, lr)

    user_data = pd.DataFrame([{
        'QA': qa,
        'VARC': varc,
        'DI': di,
        'LR': lr,
        'QA_diff': qa - min_score,
        'VARC_diff': varc - min_score,
        'DI_diff': di - min_score,
        'LR_diff': lr - min_score,
        'LessonsDone': lessons_done
    }])

    weak_topic = weak_model.predict(user_data)[0]

    st.subheader("📉 Initial Weak Area")
    st.success(weak_topic)

    # -------------------- QUESTION BANK --------------------
    question_bank = {
        "VARC": [
            {"q":"Synonym of Happy?","a":"joyful"},
            {"q":"Antonym of Increase?","a":"decrease"}
        ],
        "QA": [
            {"q":"20% of 150?","a":"30"},
            {"q":"2x+5=15, x=?","a":"5"}
        ],
        "DI": [
            {"q":"Profit 20 on 100 → %?","a":"20"},
            {"q":"Total 10+20+30?","a":"60"}
        ],
        "LR": [
            {"q":"2,4,8,16,?","a":"32"},
            {"q":"3,6,9,?","a":"12"}
        ]
    }

    # -------------------- TEST --------------------
    if not st.session_state.questions:
        all_questions = []
        for sub in ["QA","VARC","DI","LR"]:
            all_questions += question_bank[sub]
        st.session_state.questions = all_questions

    questions = st.session_state.questions
    answers = []

    for i, q in enumerate(questions):
        ans = st.text_input(f"Q{i+1}: {q['q']}", key=f"q_{i}")
        answers.append(ans)

    # -------------------- SUBMIT --------------------
    if st.button("🚀 Submit Test"):

        subject_scores = {"QA":0,"VARC":0,"DI":0,"LR":0}

        for i, q in enumerate(questions):
            for sub in question_bank:
                if q in question_bank[sub]:
                    subject = sub
                    break

            if answers[i].lower() == q['a']:
                subject_scores[subject] += 1

        # -------------------- MULTI WEAK --------------------
        min_score = min(subject_scores.values())
        weakest_subjects = [s for s in subject_scores if subject_scores[s] == min_score]

        st.error(f"Weak Areas: {', '.join(weakest_subjects)}")

        # -------------------- UPDATE SLIDERS (FIXED) --------------------
        st.session_state.qa_score = int((subject_scores["QA"]/2)*100)
        st.session_state.varc_score = int((subject_scores["VARC"]/2)*100)
        st.session_state.di_score = int((subject_scores["DI"]/2)*100)
        st.session_state.lr_score = int((subject_scores["LR"]/2)*100)

        st.success("✅ Sliders updated!")

        # -------------------- STREAK --------------------
        total = sum(subject_scores.values())
        if total >= 5:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 0

        st.markdown(f"<div class='streak'>🔥 Streak: {st.session_state.streak}</div>", unsafe_allow_html=True)

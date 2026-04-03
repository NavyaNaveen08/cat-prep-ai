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
if "pending_score_update" not in st.session_state:
    st.session_state.pending_score_update = False
if "test_submitted" not in st.session_state:
    st.session_state.test_submitted = False
if "test_results" not in st.session_state:
    st.session_state.test_results = None

# SCORE TRACKING
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

# -------------------- UI STYLING --------------------
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
.sub-text {
    text-align:center;
    color:#6b7280;
    margin-bottom:30px;
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
    font-size:16px;
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
mock_model = pickle.load(open('mock_generator_model.pkl','rb'))

# -------------------- TITLE --------------------
st.markdown('<div class="main-title">🎯 AI CAT Prep Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Smarter prep. Adaptive learning. Better results.</div>', unsafe_allow_html=True)

# -------------------- PENDING UPDATE BANNER --------------------
if st.session_state.pending_score_update:
    st.warning("⬆️ Your scores have been updated! Click **Generate Analysis** to start a new session with updated sliders.")

# -------------------- INPUT --------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.header("📊 Enter Your Mock Scores")

# Sliders using key= directly so session state updates reflect automatically
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
    st.session_state.test_submitted = False
    st.session_state.test_results = None
    st.session_state.pending_score_update = False

# -------------------- MAIN FLOW --------------------
if st.session_state.generated:

    min_score = min(qa, varc, di, lr)
    user_data = pd.DataFrame([{
        'QA': qa, 'VARC': varc, 'DI': di, 'LR': lr,
        'QA_diff': qa - min_score,
        'VARC_diff': varc - min_score,
        'DI_diff': di - min_score,
        'LR_diff': lr - min_score,
        'LessonsDone': lessons_done
    }])

    weak_topic = weak_model.predict(user_data)[0]

    # -------------------- QUESTION BANK --------------------
    question_bank = {
        "VARC": [
            {"q":"Synonym of Happy?","a":"joyful"},
            {"q":"Antonym of Increase?","a":"decrease"},
            {"q":"Meaning of Abundant?","a":"plenty"},
            {"q":"Opposite of Difficult?","a":"easy"}
        ],
        "QA": [
            {"q":"20% of 150?","a":"30"},
            {"q":"2x+5=15, x=?","a":"5"},
            {"q":"Square of 12?","a":"144"},
            {"q":"10% of 200?","a":"20"}
        ],
        "DI": [
            {"q":"Profit 20 on 100 → %?","a":"20"},
            {"q":"Total 10+20+30?","a":"60"},
            {"q":"Growth 50→75 %?","a":"50"},
            {"q":"Avg 40,50,60?","a":"50"}
        ],
        "LR": [
            {"q":"2,4,8,16,?","a":"32"},
            {"q":"Odd: Apple, Banana, Car?","a":"car"},
            {"q":"A=1,B=2,C=?","a":"3"},
            {"q":"3,6,9,?","a":"12"}
        ]
    }

    # Build lookup: question text → subject
    question_to_subject = {}
    for sub, qs in question_bank.items():
        for q in qs:
            question_to_subject[q["q"]] = sub

    # -------------------- MOCK TEST --------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Adaptive Mock Test (All Subjects)")

    if not st.session_state.questions:
        all_questions = []
        for sub in ["QA", "VARC", "DI", "LR"]:
            all_questions += random.sample(question_bank[sub], 2)
        st.session_state.questions = all_questions

    questions = st.session_state.questions

    if not st.session_state.test_submitted:
        answers = []
        for i, q in enumerate(questions):
            ans = st.text_input(f"Q{i+1}: {q['q']}", key=f"q_{i}")
            answers.append(ans)

        if st.button("🚀 Submit Test"):
            subject_scores = {"QA": 0, "VARC": 0, "DI": 0, "LR": 0}
            subject_counts = {"QA": 0, "VARC": 0, "DI": 0, "LR": 0}

            for i, q in enumerate(questions):
                subject = question_to_subject[q["q"]]
                subject_counts[subject] += 1
                if answers[i].strip().lower() == q['a']:
                    subject_scores[subject] += 1

            total_score = sum(subject_scores.values())
            min_s = min(subject_scores.values())
            weakest_subjects = [s for s, sc in subject_scores.items() if sc == min_s]

            if total_score >= 5:
                st.session_state.streak += 1
            else:
                st.session_state.streak = 0

            # Update scores via session state keys (sliders will reflect on next Generate)
            st.session_state.qa_score = int((subject_scores["QA"] / 2) * 100)
            st.session_state.varc_score = int((subject_scores["VARC"] / 2) * 100)
            st.session_state.di_score = int((subject_scores["DI"] / 2) * 100)
            st.session_state.lr_score = int((subject_scores["LR"] / 2) * 100)
            st.session_state.pending_score_update = True

            st.session_state.test_results = {
                "subject_scores": subject_scores,
                "subject_counts": subject_counts,
                "total_score": total_score,
                "weakest_subjects": weakest_subjects,
                "weak_topic": weak_topic
            }
            st.session_state.test_submitted = True
            st.rerun()

    # -------------------- SHOW RESULTS (persisted) --------------------
    if st.session_state.test_submitted and st.session_state.test_results:
        res = st.session_state.test_results
        subject_scores = res["subject_scores"]
        subject_counts = res["subject_counts"]
        total_score = res["total_score"]
        weakest_subjects = res["weakest_subjects"]
        saved_weak_topic = res["weak_topic"]

        st.subheader("📊 Your Performance")
        for sub in subject_scores:
            st.write(f"{sub}: {subject_scores[sub]}/{subject_counts[sub]}")

        st.error(f"📉 Weakest Areas: {', '.join(weakest_subjects)}")
        st.success(f"🎯 Total Score: {total_score}/8")
        st.progress(total_score / 8)
        st.markdown(f'<div class="streak">🔥 Streak: {st.session_state.streak}</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📉 Initial Weak Area (from scores)")
        st.success(saved_weak_topic)
        st.markdown('</div>', unsafe_allow_html=True)

        st.info("📊 Scores saved! Scroll up and click **Generate Analysis** to see updated sliders.")

        # -------------------- STUDY PLAN --------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📚 Personalized Study Plan")

        study_plan = {
            "QA": ["Revise arithmetic formulas", "Practice 10 quant questions", "Focus on weak topics"],
            "VARC": ["Read 2 articles (Aeon/TOI)", "Practice RC passages", "Revise vocabulary"],
            "DI": ["Solve DI sets", "Practice graphs/tables", "Improve calculations"],
            "LR": ["Solve puzzles", "Practice arrangements", "Work on patterns"]
        }

        for sub in weakest_subjects:
            st.markdown(f"### 🔹 {sub}")
            for task in study_plan[sub]:
                st.write(f"✅ {task}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

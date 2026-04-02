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

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="CAT Prep AI", layout="centered")

# -------------------- CUSTOM STYLING --------------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

/* Title */
.main-title {
    font-size:40px;
    font-weight:800;
    text-align:center;
    color:#4f46e5;
    margin-bottom:5px;
}

.sub-text {
    text-align:center;
    color:#6b7280;
    margin-bottom:30px;
}

/* Card UI */
.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0px 8px 20px rgba(0,0,0,0.05);
    margin-bottom:20px;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg, #6366f1, #22c55e);
    color: white;
    border-radius: 12px;
    height: 3em;
    font-size:16px;
    border: none;
}

/* Streak */
.streak {
    font-size:20px;
    font-weight:700;
    color:#f59e0b;
}

</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODELS --------------------
weak_model = pickle.load(open('adaptive_weak_topic_model_large.pkl','rb'))
mock_model = pickle.load(open('mock_generator_model.pkl','rb'))

# -------------------- TITLE --------------------
st.markdown('<div class="main-title">🎯 AI CAT Prep Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Smarter prep. Adaptive learning. Better results.</div>', unsafe_allow_html=True)

# -------------------- INPUT --------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.header("📊 Enter Your Mock Scores")

qa = st.slider("QA Score", 0, 100, 50)
varc = st.slider("VARC Score", 0, 100, 50)
di = st.slider("DI Score", 0, 100, 50)
lr = st.slider("LR Score", 0, 100, 50)

lessons_done = st.slider("Lessons Completed", 0, 20, 5)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- GENERATE BUTTON --------------------
if st.button("✨ Generate Analysis"):
    st.session_state.generated = True
    st.session_state.questions = []

# -------------------- MAIN FLOW --------------------
if st.session_state.generated:

    # -------------------- MODEL 1 INPUT --------------------
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

    # -------------------- MODEL 1 --------------------
    weak_topic = weak_model.predict(user_data)[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📉 Your Weak Area")
    st.success(weak_topic)
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------- MODEL 2 --------------------
    model2_input = pd.DataFrame({
        'QA':[qa],
        'VARC':[varc],
        'DI':[di],
        'LR':[lr],
        'LessonsDone':[lessons_done]
    })

    topic = mock_model.predict(model2_input)[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 AI Recommended Topic")
    st.info(topic)
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------- QUESTION BANK --------------------
    question_bank = {
        "VARC": [
            {"q":"Synonym of Happy?","a":"joyful"},
            {"q":"Antonym of Increase?","a":"decrease"},
            {"q":"Meaning of Abundant?","a":"plenty"},
            {"q":"Opposite of Difficult?","a":"easy"},
            {"q":"Correct sentence?","a":"she goes to school"}
        ],
        "QA": [
            {"q":"20% of 150?","a":"30"},
            {"q":"2x+5=15, x=?","a":"5"},
            {"q":"Average of 10,20,30?","a":"20"},
            {"q":"Square of 12?","a":"144"},
            {"q":"10% of 200?","a":"20"}
        ],
        "DI": [
            {"q":"Profit 20 on 100 → %?","a":"20"},
            {"q":"Total 10+20+30?","a":"60"},
            {"q":"Growth 50→75 %?","a":"50"},
            {"q":"Avg 40,50,60?","a":"50"},
            {"q":"Ratio 2:4?","a":"1:2"}
        ],
        "LR": [
            {"q":"2,4,8,16,?","a":"32"},
            {"q":"Odd: Apple, Banana, Car?","a":"car"},
            {"q":"A=1,B=2,C=?","a":"3"},
            {"q":"Mirror LEFT?","a":"tfel"},
            {"q":"3,6,9,?","a":"12"}
        ]
    }

    # -------------------- MOCK TEST --------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📝 Your Personalized Mock")

    num_questions = 3

    if not st.session_state.questions:
        st.session_state.questions = random.sample(question_bank[topic], num_questions)

    questions = st.session_state.questions

    answers = []

    for i, q in enumerate(questions):
        ans = st.text_input(f"Q{i+1}: {q['q']}", key=f"q_{i}")
        answers.append(ans)

    # -------------------- SUBMIT BUTTON --------------------
    if st.button("🚀 Submit Test"):

        score = 0

        for i in range(num_questions):
            if answers[i].lower() == questions[i]['a']:
                score += 1

        st.success(f"🎯 Score: {score}/{num_questions}")

        # progress bar (UI only)
        st.progress(score / num_questions)

        # -------------------- STREAK --------------------
        if score >= 2:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 0

        st.markdown(f'<div class="streak">🔥 Streak: {st.session_state.streak}</div>', unsafe_allow_html=True)

        # -------------------- FEEDBACK --------------------
        if score <= 1:
            st.error("Revise this topic again!")
            next_topic = topic
        elif score == 2:
            st.warning("You're improving, keep practicing!")
            next_topic = topic
        else:
            st.success("Great job! Move ahead 🎉")
            next_topic = random.choice(['QA','VARC','DI','LR'])

        st.subheader("📈 Next Recommended Topic")
        st.write(next_topic)

        st.write("💡 Tip: Focus on weak areas and analyze mistakes!")

    st.markdown('</div>', unsafe_allow_html=True)

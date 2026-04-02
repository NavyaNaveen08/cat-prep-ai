import streamlit as st
import pickle
import pandas as pd
import random

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="CAT Prep AI", layout="centered")

# -------------------- CUSTOM STYLING --------------------
st.markdown("""
<style>
.big-title {
    font-size:32px !important;
    font-weight:700;
    color:#4B8BBE;
}
.sub-text {
    font-size:18px;
    color:#555;
}
.stButton>button {
    background-color:#4CAF50;
    color:white;
    border-radius:10px;
    height:3em;
    width:100%;
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODELS --------------------
weak_model = pickle.load(open('adaptive_weak_topic_model_large.pkl','rb'))
mock_model = pickle.load(open('mock_generator_model.pkl','rb'))

# -------------------- SESSION STATE (STREAK) --------------------
if "streak" not in st.session_state:
    st.session_state.streak = 0

# -------------------- TITLE --------------------
st.markdown('<p class="big-title">🎯 AI CAT Prep Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Smarter prep. Better results.</p>', unsafe_allow_html=True)

# -------------------- INPUT --------------------
st.header("📊 Enter Your Mock Scores")

qa = st.slider("QA Score", 0, 100, 50)
varc = st.slider("VARC Score", 0, 100, 50)
di = st.slider("DI Score", 0, 100, 50)
lr = st.slider("LR Score", 0, 100, 50)

lessons_done = st.slider("Lessons Completed", 0, 20, 5)

# -------------------- BUTTON --------------------
if st.button("✨ Generate Analysis"):

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

    st.subheader("📉 Your Weak Area")
    st.success(weak_topic)

    # -------------------- MODEL 2 INPUT --------------------
    model2_input = pd.DataFrame({
        'QA':[qa],
        'VARC':[varc],
        'DI':[di],
        'LR':[lr],
        'LessonsDone':[lessons_done]
    })

    topic = mock_model.predict(model2_input)[0]

    st.subheader("🧠 AI Recommended Topic")
    st.info(topic)

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
    st.subheader("📝 Your Personalized Mock")

    num_questions = 3
    selected_questions = random.sample(question_bank[topic], num_questions)

    user_answers = []

    for i, q in enumerate(selected_questions):
        ans = st.text_input(f"Q{i+1}: {q['q']}")
        user_answers.append(ans)

    # -------------------- SUBMIT --------------------
    if st.button("🚀 Submit Test"):

        score = 0

        for i in range(num_questions):
            if user_answers[i].lower() == selected_questions[i]['a']:
                score += 1

        st.success(f"🎯 Score: {score}/{num_questions}")

        # -------------------- STREAK --------------------
        if score == num_questions:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 0

        st.write(f"🔥 Current Streak: {st.session_state.streak}")

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

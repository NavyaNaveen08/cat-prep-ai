import streamlit as st
import pickle
import pandas as pd
import random

# -------------------- LOAD MODELS --------------------
weak_model = pickle.load(open('adaptive_weak_topic_model_large.pkl','rb'))
mock_model = pickle.load(open('mock_generator_model.pkl','rb'))

# -------------------- TITLE --------------------
st.set_page_config(page_title="CAT Prep AI", layout="centered")

st.title("🎯 AI-Powered CAT Prep Assistant")
st.write("Personalized learning using AI")

# -------------------- INPUT --------------------
st.header("Enter Your Mock Scores")

qa = st.slider("QA Score", 0, 100, 50)
varc = st.slider("VARC Score", 0, 100, 50)
di = st.slider("DI Score", 0, 100, 50)
lr = st.slider("LR Score", 0, 100, 50)

lessons_done = st.slider("Lessons Completed", 0, 20, 5)

# -------------------- BUTTON --------------------
if st.button("Generate Analysis"):

    # -------------------- PREPARE DATA --------------------
    

       # -------------------- PREPARE DATA --------------------

    min_score = min(qa, varc, di, lr)
    
    data_dict = {
        'QA': qa,
        'VARC': varc,
        'DI': di,
        'LR': lr,
        'QA_diff': qa - min_score,
        'VARC_diff': varc - min_score,
        'DI_diff': di - min_score,
        'LR_diff': lr - min_score,
        'LessonsDone': lessons_done
    }
    
    user_data = pd.DataFrame([data_dict])
    
    # -------------------- MODEL 1 --------------------
    
    weak_topic = weak_model.predict(user_data)[0]
    
    st.subheader("📉 Your Weak Area")
    st.success(weak_topic)
    
    # -------------------- ADD ENCODE --------------------
    
    weak_map = {'QA':0,'VARC':1,'DI':2,'LR':3}
    user_data['WeakTopicEncoded'] = weak_map[weak_topic]
    
    # -------------------- FORCE COLUMN ORDER --------------------
    
    final_columns = ['QA','VARC','DI','LR',
                     'QA_diff','VARC_diff','DI_diff','LR_diff',
                     'LessonsDone','WeakTopicEncoded']
    
    user_data = user_data[final_columns]
    
    # -------------------- MODEL 2 --------------------
    
    topics = []
    
    for _ in range(5):
        topic = mock_model.predict(user_data)[0]
        topics.append(topic)

    st.subheader("🧠 AI Recommended Mock Topics")
    st.write(topics)

    # -------------------- QUESTION BANK --------------------
    question_bank = {
        'QA': [
            "What is 20% of 150?",
            "Solve: 2x + 5 = 15",
            "Average of 10, 20, 30?"
        ],
        'VARC': [
            "Synonym of 'Happy'?",
            "Antonym of 'Increase'?",
            "Find the grammar error"
        ],
        'DI': [
            "Interpret the bar graph",
            "Find total revenue from table",
            "Analyze the pie chart"
        ],
        'LR': [
            "Next in series: 2, 4, 8, 16, ?",
            "Coding-decoding question",
            "Find the odd one out"
        ]
    }

    # -------------------- MOCK TEST --------------------
    st.subheader("📝 Your Personalized Mock Test")

    for i, t in enumerate(topics):
        q = random.choice(question_bank[t])
        st.write(f"Q{i+1}: {q}")
st.write("Columns passed to model:", user_data.columns)

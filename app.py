import streamlit as st
import pickle
import pandas as pd
import random
import time
import plotly.express as px

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
if "qa_score" not in st.session_state:
    st.session_state.qa_score = 50
if "varc_score" not in st.session_state:
    st.session_state.varc_score = 50
if "di_score" not in st.session_state:
    st.session_state.di_score = 50
if "lr_score" not in st.session_state:
    st.session_state.lr_score = 50
if "score_history" not in st.session_state:
    st.session_state.score_history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

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
.diff-easy { color: #16a34a; font-weight:700; }
.diff-medium { color: #d97706; font-weight:700; }
.diff-hard { color: #dc2626; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODELS --------------------
weak_model = pickle.load(open('adaptive_weak_topic_model_large.pkl','rb'))
mock_model = pickle.load(open('mock_generator_model.pkl','rb'))

# -------------------- QUESTION BANK (global, always available) --------------------
question_bank = {
    "VARC": [
        {"q": "Which word is closest in meaning to 'Eloquent'?", "a": "fluent", "difficulty": "easy",
         "explanation": "Eloquent means fluent or persuasive in speaking/writing."},
        {"q": "Antonym of 'Obscure'?", "a": "clear", "difficulty": "easy",
         "explanation": "Obscure means unclear or unknown; its antonym is clear/obvious."},
        {"q": "Choose the correct sentence: (a) He don't know (b) He doesn't know", "a": "b", "difficulty": "medium",
         "explanation": "With third-person singular (he/she/it), use 'doesn't' not 'don't'."},
        {"q": "The passage implies the author is primarily concerned with — (a) profits (b) ethics (c) speed", "a": "b", "difficulty": "hard",
         "explanation": "RC inference questions require identifying the central concern, not surface details."},
        {"q": "Fill in the blank: She was _____ by the complexity of the problem. (a) elated (b) baffled (c) amused", "a": "b", "difficulty": "medium",
         "explanation": "Baffled means totally confused, which fits complexity of a problem."},
        {"q": "Synonym of 'Candid'?", "a": "honest", "difficulty": "easy",
         "explanation": "Candid means truthful and straightforward, i.e., honest."},
    ],
    "QA": [
        {"q": "If 2x + 3y = 12 and x - y = 1, find x.", "a": "3", "difficulty": "medium",
         "explanation": "From x - y = 1, x = y+1. Substitute: 2(y+1)+3y=12 → 5y=10 → y=2, x=3."},
        {"q": "A train 200m long passes a pole in 10s. Speed in km/h?", "a": "72", "difficulty": "medium",
         "explanation": "Speed = 200/10 = 20 m/s. Convert: 20 × 18/5 = 72 km/h."},
        {"q": "What is 15% of 240?", "a": "36", "difficulty": "easy",
         "explanation": "15% of 240 = (15/100) × 240 = 36."},
        {"q": "A shopkeeper marks up by 25% then gives 10% discount. Profit %?", "a": "12.5", "difficulty": "hard",
         "explanation": "SP = 1.25 × 0.9 = 1.125 of CP. Profit = 12.5%."},
        {"q": "If a:b = 2:3 and b:c = 4:5, find a:c.", "a": "8:15", "difficulty": "hard",
         "explanation": "a:b:c = 2:3 → scale b to 12: 8:12:15. So a:c = 8:15."},
        {"q": "Square root of 1764?", "a": "42", "difficulty": "easy",
         "explanation": "42 × 42 = 1764."},
    ],
    "DI": [
        {"q": "Sales in Jan=400, Feb=500, Mar=600. Avg monthly sales?", "a": "500", "difficulty": "easy",
         "explanation": "Average = (400+500+600)/3 = 1500/3 = 500."},
        {"q": "Revenue grew from 80L to 100L. Growth %?", "a": "25", "difficulty": "easy",
         "explanation": "Growth % = (20/80) × 100 = 25%."},
        {"q": "Pie chart: A=30%, B=45%, C=25% of 200 units. How many in B?", "a": "90", "difficulty": "medium",
         "explanation": "B = 45% of 200 = 90 units."},
        {"q": "If Col A shows 120 and Col B shows 150, what % is A of B?", "a": "80", "difficulty": "medium",
         "explanation": "(120/150) × 100 = 80%."},
        {"q": "Table: 5 products, profits 12,18,9,21,15. Which is median profit?", "a": "15", "difficulty": "hard",
         "explanation": "Sort: 9,12,15,18,21. Median (middle value) = 15."},
        {"q": "Index number base year=100, current=135. % increase?", "a": "35", "difficulty": "medium",
         "explanation": "% increase = 135-100 = 35%."},
    ],
    "LR": [
        {"q": "Series: 3, 6, 11, 18, 27, ?", "a": "38", "difficulty": "medium",
         "explanation": "Differences: 3,5,7,9,11 (odd numbers). Next: 27+11=38."},
        {"q": "If COLD=DPME, what does WARM=?", "a": "xbsn", "difficulty": "hard",
         "explanation": "Each letter shifts +1. W→X, A→B, R→S, M→N = XBSN."},
        {"q": "A is B's sister. B is C's brother. C is D's father. How is A related to D?", "a": "aunt", "difficulty": "hard",
         "explanation": "A is B's sister → A is female. B is C's brother → same generation. C is D's father → D is C's child. A is D's aunt."},
        {"q": "Odd one out: 8, 27, 64, 100, 125", "a": "100", "difficulty": "medium",
         "explanation": "8=2³, 27=3³, 64=4³, 125=5³ are perfect cubes. 100 is not."},
        {"q": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops Lazzies?", "a": "yes", "difficulty": "easy",
         "explanation": "Transitive logic: Bloops→Razzies→Lazzies, so Bloops are Lazzies."},
        {"q": "Complete: AZ, BY, CX, ?", "a": "dw", "difficulty": "easy",
         "explanation": "First letter goes A,B,C,D (forward). Second goes Z,Y,X,W (backward). Answer: DW."},
    ]
}

# Global lookup: question text → subject
question_to_subject = {}
for sub, qs in question_bank.items():
    for item in qs:
        question_to_subject[item["q"]] = sub

# -------------------- TITLE --------------------
st.markdown('<div class="main-title">🎯 AI CAT Prep Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Smarter prep. Adaptive learning. Better results.</div>', unsafe_allow_html=True)

# -------------------- PENDING UPDATE BANNER --------------------
if st.session_state.pending_score_update:
    st.warning("⬆️ Your scores have been updated! Click **Generate Analysis** to start a new session with updated sliders.")

# -------------------- INPUT --------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.header("📊 Enter Your Mock Scores")

qa = st.slider("QA Score", 0, 100, st.session_state.qa_score)
varc = st.slider("VARC Score", 0, 100, st.session_state.varc_score)
di = st.slider("DI Score", 0, 100, st.session_state.di_score)
lr = st.slider("LR Score", 0, 100, st.session_state.lr_score)
lessons_done = st.slider("Lessons Completed", 0, 20, 5)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- BUTTON --------------------
if st.button("✨ Generate Analysis"):
    st.session_state.generated = True
    st.session_state.questions = []
    st.session_state.test_submitted = False
    st.session_state.test_results = None
    st.session_state.pending_score_update = False
    st.session_state.start_time = None
    st.session_state.qa_score = qa
    st.session_state.varc_score = varc
    st.session_state.di_score = di
    st.session_state.lr_score = lr

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

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📉 Initial Weak Area (from scores)")
    st.success(weak_topic)
    st.markdown('</div>', unsafe_allow_html=True)

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

        # -------------------- TIMER --------------------
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        elapsed = int(time.time() - st.session_state.start_time)
        time_limit = 8 * 60  # 8 minutes for 8 questions
        remaining = time_limit - elapsed
        mins, secs = divmod(max(remaining, 0), 60)
        timer_color = "#dc2626" if remaining < 60 else "#4f46e5"
        st.markdown(f"<h3 style='color:{timer_color}'>⏱️ Time Remaining: {mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)

        answers = []
        for i, q in enumerate(questions):
            diff = q.get("difficulty", "medium")
            diff_color = {"easy": "#16a34a", "medium": "#d97706", "hard": "#dc2626"}.get(diff, "#4f46e5")
            st.markdown(f"<span style='color:{diff_color}; font-weight:700;'>[{diff.upper()}]</span> Q{i+1}: {q['q']}", unsafe_allow_html=True)
            ans = st.text_input("Your answer:", key=f"q_{i}", label_visibility="collapsed")
            answers.append(ans)

        # Auto-submit if time runs out
        if remaining <= 0:
            st.warning("⏰ Time's up! Auto-submitting...")
            st.session_state.test_submitted = True
            st.rerun()

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

            st.session_state.qa_score = int((subject_scores["QA"] / 2) * 100)
            st.session_state.varc_score = int((subject_scores["VARC"] / 2) * 100)
            st.session_state.di_score = int((subject_scores["DI"] / 2) * 100)
            st.session_state.lr_score = int((subject_scores["LR"] / 2) * 100)
            st.session_state.pending_score_update = True

            # Append to score history for trend chart
            st.session_state.score_history.append({
                "Attempt": len(st.session_state.score_history) + 1,
                "QA": subject_scores["QA"],
                "VARC": subject_scores["VARC"],
                "DI": subject_scores["DI"],
                "LR": subject_scores["LR"],
                "Total": total_score
            })

            time_taken = int(time.time() - st.session_state.start_time)

            st.session_state.test_results = {
                "subject_scores": subject_scores,
                "subject_counts": subject_counts,
                "total_score": total_score,
                "weakest_subjects": weakest_subjects,
                "answers": answers,
                "questions": questions,
                "time_taken": time_taken,
                "weak_topic": weak_topic
            }
            st.session_state.test_submitted = True
            st.rerun()

    # -------------------- SHOW RESULTS --------------------
    if st.session_state.test_submitted and st.session_state.test_results:
        res = st.session_state.test_results
        subject_scores = res["subject_scores"]
        subject_counts = res["subject_counts"]
        total_score = res["total_score"]
        weakest_subjects = res["weakest_subjects"]
        saved_answers = res["answers"]
        saved_questions = res["questions"]
        time_taken = res["time_taken"]
        saved_weak_topic = res["weak_topic"]

        # -------------------- SCORE + TIME --------------------
        st.subheader("📊 Your Performance")
        time_mins, time_secs = divmod(time_taken, 60)
        st.write(f"⏱️ Time taken: **{time_mins:02d}:{time_secs:02d}**")

        # Subject-wise accuracy bars
        for sub in subject_scores:
            accuracy = int((subject_scores[sub] / subject_counts[sub]) * 100)
            st.write(f"**{sub}** — {subject_scores[sub]}/{subject_counts[sub]} ({accuracy}%)")
            st.progress(accuracy / 100)

        st.error(f"📉 Weakest Areas: {', '.join(weakest_subjects)}")
        st.success(f"🎯 Total Score: {total_score}/8")
        st.progress(total_score / 8)
        st.markdown(f'<div class="streak">🔥 Streak: {st.session_state.streak}</div>', unsafe_allow_html=True)

        # -------------------- WEAK TOPIC (both model + test) --------------------
        worst_sub = min(subject_scores, key=subject_scores.get)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Weak Area Analysis")
        st.warning(f"📊 Model predicted weak area: **{saved_weak_topic}**")
        st.error(f"📝 Your test confirms weakest subject: **{worst_sub}** ({subject_scores[worst_sub]}/{subject_counts[worst_sub]} correct)")
        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------- ANSWER REVIEW --------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Answer Review")
        for i, q in enumerate(saved_questions):
            user_ans = saved_answers[i] if i < len(saved_answers) else ""
            correct = user_ans.strip().lower() == q['a']
            diff = q.get("difficulty", "medium")
            diff_color = {"easy": "#16a34a", "medium": "#d97706", "hard": "#dc2626"}.get(diff, "#4f46e5")
            if correct:
                st.success(f"✅ Q{i+1} [{diff.upper()}]: {q['q']}")
            else:
                st.error(f"❌ Q{i+1} [{diff.upper()}]: {q['q']}")
                st.write(f"Your answer: **{user_ans if user_ans else 'No answer'}** | Correct: **{q['a']}**")
                st.info(f"💡 {q.get('explanation', 'Review this topic.')}")
        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------- PROGRESS TREND CHART --------------------
        if len(st.session_state.score_history) > 1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📈 Your Progress Over Attempts")
            df_history = pd.DataFrame(st.session_state.score_history)
            fig = px.line(df_history, x="Attempt", y=["QA", "VARC", "DI", "LR"],
                          markers=True, title="Subject-wise Score Trend")
            fig.update_layout(yaxis_title="Score (out of 2)", xaxis_title="Attempt")
            st.plotly_chart(fig, use_container_width=True)
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

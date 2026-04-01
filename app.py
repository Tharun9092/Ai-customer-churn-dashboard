import streamlit as st
import numpy as np
import pickle
import matplotlib.pyplot as plt

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Churn Dashboard", layout="wide")

# ==============================
# CLEAN PROFESSIONAL CSS
# ==============================
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #94BBE9;
}

/* Title */
.title {
    font-size: 38px;
    font-weight: 700;
    color: #f2fafa;
}

/* Subtitle */
.subtitle {
    font-size: 16px;
    color: #f2fafa;
    margin-bottom: 20px;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    text-align: center;
    transition: all 0.2s ease;
}
.card:hover {
    box-shadow: 0px 6px 20px rgba(0,0,0,0.08);
}

/* Section headers */
h2 {
    color: #1e293b;
}

/* Text */
p, li {
    color: #475569;
}

/* Button */
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 200px;
}
.stButton>button:hover {
    background-color: #1d4ed8;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# LOAD MODEL
# ==============================
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# ==============================
# HEADER
# ==============================
st.markdown('<div class="title">📊 Customer Churn Prediction Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered system to predict and analyze customer churn risk</div>', unsafe_allow_html=True)

st.markdown("---")

# ==============================
# SIDEBAR INPUTS
# ==============================
st.sidebar.header("Customer Profile")

credit_score = st.sidebar.slider("Credit Score", 300, 900, 600)
country = st.sidebar.selectbox("Country", ["France", "Spain", "Germany"])
gender = st.sidebar.selectbox("Gender", ["Female", "Male"])
age = st.sidebar.slider("Age", 18, 90, 30)
tenure = st.sidebar.slider("Tenure", 0, 10, 3)
balance = st.sidebar.number_input("Balance", 0.0, 300000.0, 50000.0)
products_number = st.sidebar.slider("Products", 1, 4, 1)
credit_card = st.sidebar.selectbox("Has Credit Card", ["No", "Yes"])
active_member = st.sidebar.selectbox("Active Member", ["No", "Yes"])
estimated_salary = st.sidebar.number_input("Salary", 0.0, 200000.0, 50000.0)

# ==============================
# MAPPING
# ==============================
country_map = {"France": 0, "Spain": 1, "Germany": 2}
gender_map = {"Female": 0, "Male": 1}
binary_map = {"No": 0, "Yes": 1}

# ==============================
# PREDICTION
# ==============================
if st.button("Predict Churn"):

    input_data = np.array([[credit_score,
                            country_map[country],
                            gender_map[gender],
                            age,
                            tenure,
                            balance,
                            products_number,
                            binary_map[credit_card],
                            binary_map[active_member],
                            estimated_salary]])

    input_scaled = scaler.transform(input_data)
    prob = model.predict_proba(input_scaled)[0][1]

    st.markdown("## Results Overview")

    col1, col2, col3 = st.columns(3)

    # Probability
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>Churn Probability</h4>
            <h2>{prob:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Risk Level
    with col2:
        if prob < 0.3:
            risk = "Low Risk"
            color = "#16a34a"
        elif prob < 0.7:
            risk = "Medium Risk"
            color = "#f59e0b"
        else:
            risk = "High Risk"
            color = "#dc2626"

        st.markdown(f"""
        <div class="card">
            <h4>Risk Level</h4>
            <h2 style="color:{color}">{risk}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Status
    with col3:
        if prob < 0.3:
            status = "Customer is Stable"
        elif prob < 0.7:
            status = "Needs Attention"
        else:
            status = "High Churn Risk"

        st.markdown(f"""
        <div class="card">
            <h4>Status</h4>
            <p>{status}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==============================
    # GRAPH (CLEAR & PROFESSIONAL)
    # ==============================
    st.markdown("## Churn Analysis")

    fig, ax = plt.subplots()

    bars = ax.bar(["Stay", "Churn"], [1 - prob, prob],
                  color=["#22c55e", "#ef4444"])

    ax.set_ylabel("Probability")
    ax.set_title("Customer Churn Distribution")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f'{height:.2f}', ha='center')

    st.pyplot(fig)

    st.markdown("---")

    # ==============================
    # INSIGHTS
    # ==============================
    st.markdown("## Key Insights")

    insights = []
    if age > 50:
        insights.append("Older customers have higher churn tendency")
    if active_member == "No":
        insights.append("Inactive users are more likely to leave")
    if balance > 100000:
        insights.append("High balance customers need attention")

    if insights:
        for i in insights:
            st.write(f"• {i}")
    else:
        st.write("Customer profile is relatively stable")

    st.markdown("---")

    # ==============================
    # BUSINESS IMPACT
    # ==============================
    st.markdown("## Business Interpretation")

    if prob > 0.7:
        st.error("Immediate retention strategy required")
    elif prob > 0.3:
        st.warning("Monitor customer engagement")
    else:
        st.success("Customer retention is stable")

    st.markdown("---")

    # ==============================
    # RECOMMENDATIONS
    # ==============================
    st.markdown("## Recommended Actions")

    st.write("✔ Offer personalized retention incentives")
    st.write("✔ Improve customer engagement programs")
    st.write("✔ Focus on high-risk customer segments")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("Built by Tharun | AI Project")
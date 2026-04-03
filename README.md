# 🚀 ChurnPredict — AI Customer Churn Intelligence Platform

A production-style **AI-powered customer churn prediction system** with a modern dashboard, authentication system, and automated business reports.

Built to simulate a real-world analytics product used by companies to **detect churn early and take action**.

---

## 📌 Overview

ChurnPredict analyzes customer data and predicts the probability of churn using a machine learning model.
It presents results through a clean, interactive dashboard with **risk classification, insights, and downloadable reports**.

This project demonstrates **end-to-end ML + product thinking** — not just a model.

---

## ✨ Key Features

* 🔐 **Authentication System**
  Secure login & signup with session management

* 📊 **Real-Time Churn Prediction**
  Instant probability scoring using trained ML model

* ⚠️ **Risk Classification Engine**
  Categorizes users into:

  * Low Risk
  * Medium Risk
  * High Risk

* 📈 **Interactive Analytics Dashboard**

  * Churn vs Retention visualization
  * Probability comparison charts
  * Feature importance insights

* 🧠 **Business Insights Engine**
  Automatically generates insights based on user input

* 💡 **Actionable Recommendations**
  Suggests retention strategies for decision-making

* 📄 **Automated PDF Reports**

  * Professional multi-page report
  * Includes KPIs, charts, and insights
  * Ready for stakeholders

* 🎨 **Advanced UI/UX**
  Custom-designed dark theme with modern layout and styling

---

## 🖼️ Application Preview

### 🔐 Authentication Screen

<img src="Authentication Overview.png" width="100%" />

### 📊 Dashboard Interface

<img src="Dashboard Overview.png" width="100%" />

### 📈 Prediction & Insights

<img src="Prediction Overview.png" width="100%" />

### 📄 PDF Report Output

<img src="Report Overview.png" width="100%" />

---

## 🧠 How It Works

1. User enters customer details (age, balance, tenure, etc.)
2. Data is transformed using a scaler
3. Machine learning model predicts churn probability
4. System generates:

   * Risk level
   * Visual insights
   * Business recommendations
5. User can export a detailed PDF report

---

## 🛠️ Tech Stack

### 💻 Frontend & UI

* Streamlit
* Custom CSS (advanced styling)

### 🧠 Machine Learning

* Scikit-learn (Random Forest)
* NumPy

### 📊 Visualization

* Matplotlib

### 📄 Reporting

* ReportLab (PDF generation)

---

## 📂 Project Structure

```bash
ChurnPredict/
│── app.py              # Main application
│── model.pkl           # Trained ML model
│── scaler.pkl          # Data scaler
│── users.json          # Authentication storage
│── requirements.txt    # Dependencies
│── README.md
│── assets/             # Images/screenshots (recommended)
```

---

## 🌐 Live Demo

👉 [https://ai-customer-churn-dashboard-tharun9092.streamlit.app/](https://ai-customer-churn-dashboard-prediction.streamlit.app/)

---

## ⚙️ Run Locally

```bash
git clone https://github.com/Tharun9092/Ai-customer-churn-dashboard.git
cd Ai-customer-churn-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Model Details

* Model: Random Forest Classifier
* Preprocessing: StandardScaler
* Features:

  * Credit Score
  * Age
  * Balance
  * Tenure
  * Products
  * Active Member
  * Salary
* Output:

  * Churn Probability (%)
  * Risk Category

---

## 📈 Business Impact

* Detects high-risk customers early
* Helps reduce churn with targeted actions
* Improves retention strategies
* Enables data-driven decision making
* Automates reporting for stakeholders

---

## 🚀 What Makes This Project Strong

* Goes beyond ML → **complete product**
* Includes **authentication + UI + reporting**
* Focuses on **business value, not just accuracy**
* Clean, modern dashboard (not default Streamlit UI)

---

## 🔮 Future Improvements

* SHAP explainability for model decisions
* Bulk prediction via CSV upload
* Backend API (FastAPI)
* Database integration for users
* Cloud deployment with custom domain

---

## 👨‍💻 Author

**Tharun Reddy**
AI & Machine Learning Enthusiast

---

## ⭐ If you found this useful

Give this repo a ⭐ and feel free to connect!
https://www.linkedin.com/in/tharun-kumar-reddy-6941a22a6/

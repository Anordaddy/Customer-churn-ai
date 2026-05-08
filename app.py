import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Customer Churn AI",
    page_icon="📊",
    layout="wide"
)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("churn_model.pkl")
columns = joblib.load("model_columns.pkl")

# =========================
# HEADER (PROFESSIONAL UI)
# =========================
st.markdown(
    """
    <div style='text-align:center; padding:10px'>
        <h1 style='color:#1F2937;'>Customer Churn AI System</h1>
        <p style='color:gray; font-size:16px;'>
        Machine Learning-powered customer churn prediction & risk analysis
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("Customer Information")

tenure = st.sidebar.slider("Tenure (Months)", 0, 72, 12)
monthly_charges = st.sidebar.number_input("Monthly Charges", 0.0, 200.0, 70.0)
total_charges = st.sidebar.number_input("Total Charges", 0.0, 10000.0, 1000.0)

contract = st.sidebar.selectbox(
    "Contract Type",
    ["Month-to-month", "One year", "Two year"]
)

internet = st.sidebar.selectbox(
    "Internet Service",
    ["DSL", "Fiber optic", "No"]
)

payment = st.sidebar.selectbox(
    "Payment Method",
    [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]
)

online_security = st.sidebar.selectbox("Online Security", ["Yes", "No"])
tech_support = st.sidebar.selectbox("Tech Support", ["Yes", "No"])

# =========================
# INPUT PREPARATION
# =========================
def prepare_input():
    df = pd.DataFrame([[0] * len(columns)], columns=columns)

    df["tenure"] = tenure
    df["MonthlyCharges"] = monthly_charges
    df["TotalCharges"] = total_charges

    if contract == "One year":
        df["Contract_One year"] = 1
    elif contract == "Two year":
        df["Contract_Two year"] = 1

    if internet == "Fiber optic":
        df["InternetService_Fiber optic"] = 1
    elif internet == "No":
        df["InternetService_No"] = 1

    if payment == "Electronic check":
        df["PaymentMethod_Electronic check"] = 1

    if online_security == "Yes":
        df["OnlineSecurity_Yes"] = 1

    if tech_support == "Yes":
        df["TechSupport_Yes"] = 1

    return df

# =========================
# PREDICTION BUTTON
# =========================
if st.button("Predict Churn"):

    input_df = prepare_input()
    prob = model.predict_proba(input_df)[0][1]

    # =========================
    # KPI METRICS
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Churn Probability", f"{prob:.2f}")
    col2.metric("Risk Level", "High" if prob > 0.45 else "Low")
    col3.metric("Model Confidence", "XGBoost")

    st.progress(float(prob))

    st.markdown("---")

    # =========================
    # RISK CLASSIFICATION
    # =========================
    st.subheader("Risk Analysis")

    if prob > 0.45:
        st.error("🔴 High Risk of Churn")
        st.write("Recommendation: Offer discount or retention strategy")

    elif prob > 0.25:
        st.warning("🟡 Medium Risk")
        st.write("Recommendation: Monitor customer behavior")

    else:
        st.success("🟢 Low Risk")
        st.write("Customer likely to stay")

    # =========================
    # RISK DISTRIBUTION
    # =========================
    st.subheader("📊 Risk Distribution")

    risk_df = pd.DataFrame({
        "Category": ["Risk", "Safe"],
        "Value": [prob, 1 - prob]
    })

    st.bar_chart(risk_df.set_index("Category"))

    st.markdown("---")

    # =========================
    # FEATURE IMPORTANCE
    # =========================
    st.subheader("Key Drivers of Churn")

    importance_df = pd.DataFrame({
        "Feature": columns,
        "Importance": model.feature_importances_
    }).sort_values(by="Importance", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(importance_df["Feature"], importance_df["Importance"])
    ax.invert_yaxis()
    ax.set_xlabel("Importance Score")

    st.pyplot(fig)

    st.markdown("---")

    # =========================
    # INSIGHT BOX (VERY IMPORTANT)
    # =========================
    st.info(
        "💡 Insight: Customers with shorter tenure, fiber optic internet, "
        "and month-to-month contracts are more likely to churn."
    )

    # =========================
    # DOWNLOAD REPORT
    # =========================
    report_df = pd.DataFrame({
        "Tenure": [tenure],
        "MonthlyCharges": [monthly_charges],
        "TotalCharges": [total_charges],
        "ChurnProbability": [prob]
    })

    csv = report_df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Prediction Report",
        data=csv,
        file_name="churn_prediction_report.csv",
        mime="text/csv"
    )
# 📊 Telco Customer Churn Prediction Web Application

An end-to-end Machine Learning web platform designed to evaluate and predict customer churn risk using customer demographics, subscribed services, account details, and billing history. Built with **Flask**, **Scikit-Learn (Random Forest)**, and **Bootstrap 5**.

---

## 🚀 Key Features

- **Executive Analytics Dashboard**: High-level KPI metrics and interactive visual charts (Doughnut and Bar charts) powered by **Chart.js**.
- **Single Customer Prediction Form**: Real-time evaluation across all 19 customer features with instant churn risk probability scoring and risk level badges.
- **Batch CSV Scoring Pipeline**: Upload a `.csv` dataset of customer records to process batch predictions, inspect results in a tabular preview, and download the scored dataset.
- **Theme Support**: Seamless toggling between **Light Mode** and **Dark Mode** with persistent client-side state.
- **Clean Architecture**: Clean code structure with decoupled templates and model inference routines.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Machine Learning**: Scikit-Learn (Random Forest Classifier), Pandas, NumPy, Joblib
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

---

## 📂 Project Structure

```text
Telco-Churn-Flask-App/
│
├── app.py                     # Flask application routes and inference pipeline
├── churn_rf_model.pkl         # Trained Random Forest model binary
├── requirements.txt           # Project dependencies
├── .gitignore                 # Files excluded from git tracking
├── README.md                  # Project documentation
│
└── templates/
    ├── dashboard.html         # Executive analytics dashboard
    ├── predict.html           # Single customer risk evaluator form
    └── batch.html             # Batch CSV upload and scoring preview
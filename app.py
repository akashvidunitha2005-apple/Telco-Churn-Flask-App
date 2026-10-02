from flask import Flask, render_template, request, Response
import joblib
import pandas as pd
import numpy as np
import io

app = Flask(__name__)

model = joblib.load('churn_rf_model.pkl')
expected_features = list(model.feature_names_in_)
scored_data_store = None

@app.route('/')
def dashboard():
    stats = {
        'total_customers': '7,043',
        'churn_rate': '26.54%',
        'active_customers': '5,174',
        'high_risk_customers': '1,869'
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('predict.html', show_result=False)

    try:
        gender = request.form.get('gender', 'Male')
        senior_citizen = int(request.form.get('SeniorCitizen', 0))
        partner = request.form.get('Partner', 'No')
        dependents = request.form.get('Dependents', 'No')

        phone_service = request.form.get('PhoneService', 'Yes')
        multiple_lines = request.form.get('MultipleLines', 'No')
        internet_service = request.form.get('InternetService', 'Fiber optic')
        online_security = request.form.get('OnlineSecurity', 'No')
        online_backup = request.form.get('OnlineBackup', 'No')
        device_protection = request.form.get('DeviceProtection', 'No')
        tech_support = request.form.get('TechSupport', 'No')
        streaming_tv = request.form.get('StreamingTV', 'No')
        streaming_movies = request.form.get('StreamingMovies', 'No')

        tenure = float(request.form.get('tenure', 0))
        contract = request.form.get('Contract', 'Month-to-month')
        paperless_billing = request.form.get('PaperlessBilling', 'Yes')
        payment_method = request.form.get('PaymentMethod', 'Electronic check')
        monthly_charges = float(request.form.get('MonthlyCharges', 0))
        total_charges = float(request.form.get('TotalCharges', 0))

        raw_data = {
            'gender': [gender],
            'SeniorCitizen': [senior_citizen],
            'Partner': [partner],
            'Dependents': [dependents],
            'tenure': [tenure],
            'PhoneService': [phone_service],
            'MultipleLines': [multiple_lines],
            'InternetService': [internet_service],
            'OnlineSecurity': [online_security],
            'OnlineBackup': [online_backup],
            'DeviceProtection': [device_protection],
            'TechSupport': [tech_support],
            'StreamingTV': [streaming_tv],
            'StreamingMovies': [streaming_movies],
            'Contract': [contract],
            'PaperlessBilling': [paperless_billing],
            'PaymentMethod': [payment_method],
            'MonthlyCharges': [monthly_charges],
            'TotalCharges': [total_charges]
        }
        df_raw = pd.DataFrame(raw_data)
        df_encoded = pd.get_dummies(df_raw, drop_first=True)

        input_data = pd.DataFrame(0.0, index=[0], columns=expected_features)
        for col in df_encoded.columns:
            if col in input_data.columns:
                input_data[col] = df_encoded[col].values[0]

        prob = model.predict_proba(input_data)[0][1]
        risk_percentage = round(prob * 100, 2)

        if risk_percentage >= 70:
            risk_level = "High Risk"
            risk_badge = "bg-danger"
            prediction_text = "Action Required: High risk of customer churn."
        elif risk_percentage >= 40:
            risk_level = "Moderate Risk"
            risk_badge = "bg-warning text-dark"
            prediction_text = "Monitor: Moderate churn risk detected."
        else:
            risk_level = "Low Risk / Safe"
            risk_badge = "bg-success"
            prediction_text = "Loyal Customer: Low churn probability."

        return render_template('predict.html',
                               show_result=True,
                               risk_percentage=risk_percentage,
                               risk_level=risk_level,
                               risk_badge=risk_badge,
                               prediction_text=prediction_text)

    except Exception as e:
        return render_template('predict.html', error=str(e), show_result=False)

@app.route('/batch', methods=['GET', 'POST'])
def batch():
    global scored_data_store
    if request.method == 'GET':
        return render_template('batch.html', uploaded=False)

    try:
        uploaded_file = request.files.get('dataset_file')
        if not uploaded_file or uploaded_file.filename == '':
            return render_template('batch.html', error="Please choose a CSV file to upload.", uploaded=False)

        df_input = pd.read_csv(uploaded_file)
        df_proc = df_input.copy()

        if 'TotalCharges' in df_proc.columns:
            df_proc['TotalCharges'] = pd.to_numeric(df_proc['TotalCharges'], errors='coerce').fillna(0.0)

        df_encoded = pd.get_dummies(df_proc, drop_first=True)

        scoring_matrix = pd.DataFrame(0.0, index=range(len(df_proc)), columns=expected_features)
        for col in df_encoded.columns:
            if col in scoring_matrix.columns:
                scoring_matrix[col] = df_encoded[col].values

        probabilities = model.predict_proba(scoring_matrix)[:, 1]
        df_input['Churn_Probability_%'] = (probabilities * 100).round(2)
        df_input['Churn_Prediction'] = np.where(probabilities >= 0.5, 'Yes (Will Churn)', 'No (Retained)')

        scored_data_store = df_input.copy()

        total_rows = len(df_input)
        churn_count = int((probabilities >= 0.5).sum())
        retained_count = total_rows - churn_count
        churn_pct = round((churn_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

        preview_data = df_input.head(10).to_dict(orient='records')
        table_columns = list(df_input.columns)

        return render_template('batch.html',
                               uploaded=True,
                               total_rows=total_rows,
                               churn_count=churn_count,
                               retained_count=retained_count,
                               churn_pct=churn_pct,
                               columns=table_columns,
                               rows=preview_data)

    except Exception as e:
        return render_template('batch.html', error=f"Processing error: {str(e)}", uploaded=False)

@app.route('/download_batch')
def download_batch():
    global scored_data_store
    if scored_data_store is None:
        return "No data available for download.", 400

    csv_buffer = io.StringIO()
    scored_data_store.to_csv(csv_buffer, index=False)
    csv_output = csv_buffer.getvalue()

    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=telco_scored_results.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
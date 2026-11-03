# 🤖 TrainReady – AI-Powered Dataset Quality Analyzer

TrainReady is a web-based application designed to analyze dataset quality and determine whether a dataset is ready for Machine Learning model training.

It helps users identify data quality issues, understand dataset characteristics, and make informed decisions before starting the model training process.

## ✨ Features

- **Dataset Upload:** Upload datasets in CSV, XLSX, and XLS formats.
- **Data Quality Analysis:** Analyze datasets for potential quality issues.
- **Missing Values Detection:** Identify missing or null values in columns.
- **Duplicate Detection:** Detect duplicate records.
- **Data Type Analysis:** Identify incorrect or inconsistent data types.
- **Invalid Data Detection:** Highlight potentially invalid data.
- **Redundant Data Detection:** Identify unnecessary or repetitive information.
- **Noise Analysis:** Identify potential noise in the dataset.
- **Dataset Readiness:** Generate a readiness percentage and status.
- **Visual Reports:** Display analysis results through charts and summary cards.
- **Key Insights:** Provide useful insights about the dataset.

## 🛠️ Technologies Used

**Frontend:**
- HTML5
- CSS3
- JavaScript

**Backend:**
- Python
- Flask
- Flask-CORS

**Data Analysis:**
- Pandas
- NumPy
- OpenPyXL
- xlrd

## 📂 Project Structure

```text
TrainReady/
│
├── backend/
│   ├── app.py
│   ├── analyzer.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── results.html
│   ├── style.css
│   └── script.js
│
└── README.md
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_LINK
```

### 2. Navigate to the Backend

```bash
cd TrainReady/backend
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open the Application

Open the frontend `index.html` file in your browser and start uploading datasets for analysis.

## 🔍 How It Works

1. Upload a dataset.
2. TrainReady processes and analyzes the uploaded data.
3. The analyzer checks for different data quality issues.
4. Analysis results are generated.
5. View the dataset summary, charts, insights, and readiness percentage.

## 🎯 Project Objective

The main objective of TrainReady is to simplify the dataset preparation process by identifying data quality issues before machine learning model training.

It helps users understand the condition of their datasets and determine what improvements may be required before using them for ML applications.

## 👩‍💻 Developed By

**Dinkal Leuva**

B.Tech – Information Technology

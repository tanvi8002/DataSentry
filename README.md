# DataSentry – Automated Data Quality Checker

DataSentry is a Python-based data quality checking application built with Streamlit. It helps users inspect, validate, clean and download datasets through a simple web interface.

## Features

- Upload CSV and Excel datasets.
- Preview uploaded data.
- Detect missing values and duplicate records.
- Identify invalid email addresses and age values.
- Calculate a data quality score out of 100.
- Visualize data quality using charts.
- Clean datasets by removing duplicates and handling missing or invalid values.
- Download cleaned datasets in CSV and Excel formats.
- Generate downloadable PDF data quality reports.

## Technologies Used

- Python
- Pandas
- Streamlit
- Matplotlib
- OpenPyXL
- ReportLab

## Project Structure

```text
DataSentry/
│
├── data/
│   └── sample_customers.csv
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd DataSentry
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

## Sample Dataset

A sample customer dataset is included in the `data` folder to demonstrate missing values, duplicate records and invalid age values.

## Future Improvements

- Add customizable data validation rules.
- Support more file formats.
- Add SQL database connectivity.
- Create advanced data quality dashboards.

## Author

Tanvi Ranpise

## Application Screenshots

### DataSentry Dashboard

![Dashboard](screenshots/dashboard.png)

### Data Quality Analysis

![Data Quality](screenshots/data_quality.png)

### Data Cleaning

![Data Cleaning](screenshots/cleaning.png)

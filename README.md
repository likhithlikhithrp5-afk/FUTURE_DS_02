# Customer Retention & Churn Analysis Project

## Objective
This project analyzes customer retention and churn using a synthetic but realistic subscription dataset. It is designed to mirror the kind of work expected in SaaS, fintech, edtech, and subscription-based businesses.

## Files
- [outputs/customer_churn_data.csv](outputs/customer_churn_data.csv)
- [outputs/churn_analysis_dashboard.png](outputs/churn_analysis_dashboard.png)
- [outputs/summary.txt](outputs/summary.txt)
- [outputs/retention_report.md](outputs/retention_report.md)
- [retention_analysis.py](retention_analysis.py)
- [requirements.txt](requirements.txt)

## How to Reproduce
Install the Python dependencies, then run the analysis script from the project folder:

```powershell
pip install -r requirements.txt
python retention_analysis.py
```

## Key Findings
- Overall churn rate: 37.7%
- Highest-churn plan: Free
- Highest-churn region: Africa
- Low-engagement customers churn more often, indicating that activation and onboarding are the strongest retention levers.

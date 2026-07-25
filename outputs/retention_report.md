# Customer Retention & Churn Analysis Report

## Executive Summary

- Overall churn rate is 37.7%, indicating that roughly one in every 3 customers leaves the platform.
- The highest-churn plan is Free, while the most at-risk region is Africa.
- Customers with low engagement and high support demand are the most likely to churn, suggesting that onboarding quality and product adoption need attention.

## Key Insights

- Plan-wise churn: plan
Free          0.440000
Pro           0.358804
Basic         0.334247
Enterprise    0.321101
- Region-wise churn: region
Africa           0.428571
Asia             0.405738
North America    0.387692
Europe           0.346875
LATAM            0.341709
- Engagement-level churn: engagement_score
Low          0.460177
Medium       0.334520
High         0.336842
Very High    0.359322

## Recommended Actions

- Improve onboarding for new customers, especially for Free and Basic plan users, to boost activation and early engagement.
- Proactively contact customers with low engagement scores or frequent support tickets before they churn.
- Introduce tiered retention offers and lifecycle campaigns for regions showing above-average churn.
- Track retention monthly by cohort and compare it against support usage, activation milestones, and plan upgrades.

## Files Produced

- Data: outputs/customer_churn_data.csv
- Dashboard image: outputs/churn_analysis_dashboard.png
- Summary metrics: outputs/summary.txt
- Report: outputs/retention_report.md
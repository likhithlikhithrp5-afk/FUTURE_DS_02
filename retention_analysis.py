import os
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# -----------------------------
# 1) Create a realistic dataset
# -----------------------------
np.random.seed(42)

n = 1200

# Build customer-level dataframe
customers = pd.DataFrame({
    'customer_id': [f'CUST{i:04d}' for i in range(1, n + 1)],
    'signup_date': np.random.choice(pd.date_range('2022-01-01', '2025-01-31', freq='MS'), size=n),
    'plan': np.random.choice(['Free', 'Basic', 'Pro', 'Enterprise'], size=n, p=[0.35, 0.30, 0.25, 0.10]),
    'region': np.random.choice(['North America', 'Europe', 'Asia', 'LATAM', 'Africa'], size=n, p=[0.30, 0.25, 0.20, 0.15, 0.10]),
    'segment': np.random.choice(['Individual', 'SMB', 'Enterprise'], size=n, p=[0.45, 0.35, 0.20]),
    'monthly_spend': np.round(np.clip(np.random.normal(35, 18, n), 5, 200), 2),
    'support_tickets': np.random.poisson(1.8, n),
    'days_active': np.random.randint(30, 650, n),
    'engagement_score': np.random.randint(20, 100, n),
    'churned': np.random.choice([0, 1], size=n, p=[0.72, 0.28]),
})

# Stronger signal for churn by plan/engagement/support
customers.loc[customers['plan'].eq('Free'), 'churned'] = np.random.choice([0, 1], size=customers['plan'].eq('Free').sum(), p=[0.55, 0.45])
customers.loc[customers['engagement_score'] < 40, 'churned'] = np.random.choice([0, 1], size=(customers['engagement_score'] < 40).sum(), p=[0.50, 0.50])
customers.loc[customers['support_tickets'] > 4, 'churned'] = np.random.choice([0, 1], size=(customers['support_tickets'] > 4).sum(), p=[0.45, 0.55])
customers['churned'] = customers['churned'].astype(int)

# Add tenure and last activity
customers['tenure_days'] = np.clip(customers['days_active'] + np.random.randint(0, 90, n), 30, 720)
customers['last_activity_date'] = pd.to_datetime(customers['signup_date']) + pd.to_timedelta(customers['tenure_days'], unit='D')
customers['signup_month'] = customers['signup_date'].dt.to_period('M').astype(str)
customers['cohort'] = customers['signup_month']

# Output files
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)
customers.to_csv(output_dir / 'customer_churn_data.csv', index=False)

# -----------------------------
# 2) Cohort analysis
# -----------------------------
customers['signup_month'] = pd.to_datetime(customers['signup_month'])
customers['month_index'] = (customers['signup_month'].dt.year - customers['signup_month'].dt.year.min()) * 12 + (customers['signup_month'].dt.month - customers['signup_month'].dt.month.min())

# Use signup month to create retention by cohort
cohort_summary = []
for cohort_month, grp in customers.groupby('signup_month'):
    cohort_size = len(grp)
    if cohort_size == 0:
        continue
    for month_number in range(1, 7):
        active = (grp['tenure_days'] >= month_number * 30).sum()
        retention = active / cohort_size if cohort_size else np.nan
        cohort_summary.append((cohort_month.strftime('%Y-%m'), month_number, cohort_size, active, retention))

retention_df = pd.DataFrame(cohort_summary, columns=['cohort', 'month_number', 'cohort_size', 'active_customers', 'retention_rate'])

# -----------------------------
# 3) Metrics
# -----------------------------
churn_rate = customers['churned'].mean()
plan_churn = customers.groupby('plan')['churned'].mean().sort_values(ascending=False)
region_churn = customers.groupby('region')['churned'].mean().sort_values(ascending=False)
segment_churn = customers.groupby('segment')['churned'].mean().sort_values(ascending=False)
engagement_churn = customers.groupby(pd.cut(customers['engagement_score'], bins=[0, 40, 60, 80, 100], labels=['Low','Medium','High','Very High']), observed=False)['churned'].mean()

# -----------------------------
# 4) Visualizations
# -----------------------------
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_theme(style='whitegrid')

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Churn by plan
plan_churn.plot(kind='bar', ax=axes[0, 0], color=['#ef4444', '#f59e0b', '#3b82f6', '#10b981'])
axes[0, 0].set_title('Churn rate by plan')
axes[0, 0].set_ylabel('Churn rate')
axes[0, 0].tick_params(axis='x', rotation=0)

# Churn by region
region_churn.plot(kind='bar', ax=axes[0, 1], color=['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'])
axes[0, 1].set_title('Churn rate by region')
axes[0, 1].set_ylabel('Churn rate')
axes[0, 1].tick_params(axis='x', rotation=0)

# Engagement vs churn
engagement_churn.plot(kind='bar', ax=axes[1, 0], color=['#f87171', '#fb923c', '#60a5fa', '#34d399'])
axes[1, 0].set_title('Churn rate by engagement level')
axes[1, 0].set_ylabel('Churn rate')
axes[1, 0].tick_params(axis='x', rotation=0)

# Retention by cohort
pivot = retention_df.pivot(index='cohort', columns='month_number', values='retention_rate').fillna(np.nan)
if not pivot.empty:
    pivot.iloc[:, :6].plot(ax=axes[1, 1], marker='o', linewidth=2.5)
    axes[1, 1].set_title('Retention rates by cohort (first 6 months)')
    axes[1, 1].set_ylabel('Retention rate')
    axes[1, 1].set_xlabel('Months since signup')
    axes[1, 1].legend(title='Cohort', loc='best')

plt.tight_layout()
plt.savefig(output_dir / 'churn_analysis_dashboard.png', dpi=200)
plt.close()

# -----------------------------
# 5) Summary report data
# -----------------------------
summary = {
    'Overall churn rate': round(churn_rate, 3),
    'Highest churn plan': plan_churn.index[0],
    'Highest churn region': region_churn.index[0],
    'Lowest engagement churn': round(engagement_churn.loc['Low'], 3) if 'Low' in engagement_churn.index else np.nan,
    'Average monthly spend': round(customers['monthly_spend'].mean(), 2),
    'Average tenure days': round(customers['tenure_days'].mean(), 1),
    'Average support tickets': round(customers['support_tickets'].mean(), 2),
}

with open(output_dir / 'summary.txt', 'w', encoding='utf-8') as f:
    for k, v in summary.items():
        f.write(f'{k}: {v}\n')

# -----------------------------
# 6) Build a polished markdown report
# -----------------------------
report_lines = []
report_lines.append('# Customer Retention & Churn Analysis Report')
report_lines.append('')
report_lines.append('## Executive Summary')
report_lines.append('')
report_lines.append(f'- Overall churn rate is {summary["Overall churn rate"]:.1%}, indicating that roughly one in every {int(round(1/summary["Overall churn rate"] ))} customers leaves the platform.')
report_lines.append(f'- The highest-churn plan is {summary["Highest churn plan"]}, while the most at-risk region is {summary["Highest churn region"]}.')
report_lines.append(f'- Customers with low engagement and high support demand are the most likely to churn, suggesting that onboarding quality and product adoption need attention.')
report_lines.append('')
report_lines.append('## Key Insights')
report_lines.append('')
report_lines.append(f'- Plan-wise churn: {plan_churn.to_string()}')
report_lines.append(f'- Region-wise churn: {region_churn.to_string()}')
report_lines.append(f'- Engagement-level churn: {engagement_churn.to_string()}')
report_lines.append('')
report_lines.append('## Recommended Actions')
report_lines.append('')
report_lines.append('- Improve onboarding for new customers, especially for Free and Basic plan users, to boost activation and early engagement.')
report_lines.append('- Proactively contact customers with low engagement scores or frequent support tickets before they churn.')
report_lines.append('- Introduce tiered retention offers and lifecycle campaigns for regions showing above-average churn.')
report_lines.append('- Track retention monthly by cohort and compare it against support usage, activation milestones, and plan upgrades.')
report_lines.append('')
report_lines.append('## Files Produced')
report_lines.append('')
report_lines.append('- Data: outputs/customer_churn_data.csv')
report_lines.append('- Dashboard image: outputs/churn_analysis_dashboard.png')
report_lines.append('- Summary metrics: outputs/summary.txt')
report_lines.append('- Report: outputs/retention_report.md')

Path(output_dir / 'retention_report.md').write_text('\n'.join(report_lines), encoding='utf-8')

print('Analysis completed successfully.')
print('Files created in outputs/')

# Dashboard — Last Mile Auditor

A Streamlit dashboard auditing delivery performance across Brazil for Veridi Logistics. Reads a pre-cleaned master dataset produced by the analysis notebook and renders six charts plus four KPIs.

**Live demo:** [last-mile-auditor.streamlit.app](https://last-mile-auditor-bvqjee7s2tdg7h8dnd5ylr.streamlit.app/)

For project context, executive summary, and analytical findings, see the [project root README](../README.md).

## What it shows

- **KPI strip** — % late, avg delay among late orders, avg review score, total orders. Thresholds calibrated to the real Olist baseline (8% national late rate).
- **Late delivery rate by state** — horizontal bar with traffic-light coloring. Headline answer to "is this regional or nationwide?"
- **Delivery status distribution** — On Time / Late / Super Late counts.
- **Delay vs review score scatter** — with regression line; visualizes the correlation between lateness and customer sentiment.
- **Average review score per delivery status** — quantifies the score collapse from On Time (4.29) to Super Late (1.78).
- **Promise Gap by State** (Candidate's Choice) — median actual delivery time vs. late rate per state, sized by order volume. Isolates whether each state needs a carrier fix or an estimator fix.
- **Top product categories by late rate** — uses the bonus Portuguese→English translation.

State and delivery-status filters apply across all charts.

## Run locally

​```bash
# From the dashboard/ folder
pip install -r requirements.txt
streamlit run app.py
​```

The app reads `data/master_dataset.csv`. To regenerate that file, run the data-export cell at the end of `Last_Mile_Logistics_Auditor.ipynb` in the project root.

## Deploy to Streamlit Cloud

1. Push the repo to GitHub. `data/master_dataset.csv` must be committed for the deployment to find it.
2. Go to https://share.streamlit.io → New app
3. Repository: `<your-username>/last-mile-auditor`, Branch: `main`, Main file path: `dashboard/app.py`
4. Click Deploy. First build takes ~2 minutes.

## Project structure

​```
dashboard/
├── app.py                   # Main Streamlit app
├── requirements.txt         # Loosened pins (pandas, numpy, matplotlib, streamlit)
├── runtime.txt              # Pins Python 3.11 for Streamlit Cloud
├── README.md                # This file
├── .gitignore
├── .streamlit/
│   └── config.toml          # Dark theme config
└── data/
    └── master_dataset.csv   # Pre-cleaned data from the notebook (committed)
​```

## Data

The master dataset is built by the upstream notebook (joining four Olist tables — orders, reviews, customers, products — plus the order_items table for product category mapping). All cleaning, joining, and feature engineering happens upstream; this dashboard only reads the result.

Source: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
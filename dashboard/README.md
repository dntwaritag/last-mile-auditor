# Veridi Logistics — Last Mile Auditor (Dashboard)

A Streamlit dashboard auditing delivery performance across Brazil for Veridi Logistics. Reads a pre-cleaned master dataset produced by the analysis notebook and renders six charts plus four KPIs.

**Live demo:** _[paste your Streamlit Cloud URL here once deployed]_

## What it shows

- KPI strip: % late, avg delay among late orders, avg review score, total orders
- Late delivery rate by state (horizontal bar)
- Delivery status distribution (On Time / Late / Super Late)
- Delay vs. review score scatter with regression line
- Average review score per delivery status
- **Promise Gap by State** — Candidate's Choice analysis isolating estimator vs. carrier failure modes
- Top product categories by late rate (uses the bonus Portuguese→English translation)

Filters: state and delivery status, applied across all charts.

## Setup (local)

```bash
git clone <this-repo>
cd <this-repo>
pip install -r requirements.txt
streamlit run app.py
```

The app reads `data/master_dataset.csv`. To regenerate it, run the data-export cell in the analysis notebook (`Last_Mile_Logistics_Auditor.ipynb`) — it builds the file from the four Olist CSVs.

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub. **The `data/master_dataset.csv` file must be committed** so the cloud deployment can read it. (~30 MB, well under GitHub's 100 MB per-file limit and Streamlit Cloud's 1 GB app limit.)
2. Go to https://share.streamlit.io
3. Click "New app" → select this repo → main branch → `app.py`
4. Click "Deploy". The first build takes ~3 minutes.
5. Once live, copy the public URL into the project README.

## Project structure

```
dashboard/
├── app.py                   # main Streamlit app
├── requirements.txt         # pinned dependencies
├── README.md                # this file
├── .gitignore
├── .streamlit/
│   └── config.toml          # dark theme config
└── data/
    └── master_dataset.csv   # produced by the analysis notebook (committed)
```

## Data source

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). The master dataset is built by joining four Olist tables (orders, reviews, customers, products) plus the order_items table for product category mapping. Cleaning, joining, and feature engineering happen in the upstream notebook; this dashboard reads the result.

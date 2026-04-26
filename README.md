# Last Mile Logistics Auditor

## A. Executive Summary

Veridi Logistics's CEO suspected that customer dissatisfaction was being driven less by raw shipping speed and more by inaccurate delivery promises. Analysis of **96,470 delivered orders** from the Olist dataset confirms the hypothesis with two precise findings: **(1) the late-delivery problem is regional, not nationwide** — the national late rate is **8.1%**, but Alagoas (AL) sits at **23.9%**, almost **3x the national average**, alongside three other Northern/Northeastern states (MA, PI, CE) above 15%; and **(2) late deliveries are the dominant driver of negative reviews** — average review score collapses from **4.29 stars** for on-time orders to **1.78 stars** for orders more than five days late, with a Pearson correlation of **-0.267** between delay days and review score. The recommended action is twofold: **recalibrate the delivery-date estimator for high-risk states** to stop over-promising at checkout, and **prioritize closing the "Super Late" tail** (>5 days late) since this 4.4% of orders causes a disproportionate 1.68-star score drop versus merely-Late orders.

## B. Project Links

- **Notebook:** [`Last_Mile_Logistics_Auditor.ipynb`](./Last_Mile_Logistics_Auditor.ipynb) (with [HTML export](./Last_Mile_Logistics_Auditor.html))
- **Dashboard:** [last-mile-auditor.streamlit.app](https://last-mile-auditor-bvqjee7s2tdg7h8dnd5ylr.streamlit.app/)
- **Presentation:** [Slides](https://docs.google.com/presentation/d/1DMbSpKTZuulcX6ozxeyZ3bXJ8Fd0uaBX/edit?usp=sharing&ouid=112215962694689143745&rtpof=true&sd=true)
- **Video walkthrough :** [Presentation](https://drive.google.com/file/d/1OWjQEKUljaGXWKX6z0TD0xttKjMbWVPu/view?usp=sharing)

## C. Technical Explanation

### Data Cleaning

Five date columns in `olist_orders_dataset.csv` were parsed to `datetime` so that delay arithmetic was possible. Orders with status other than `delivered` (canceled, unavailable, shipped, processing, etc.) were excluded — **2,963 rows removed** — because they have no actual delivery timestamp and cannot be evaluated for delay. This is documented as an explicit business decision rather than silent filtering. A small residual of `delivered` orders with null delivery timestamps (8 rows, 0.008%) were dropped as data-quality issues, leaving 96,470 clean orders.

### Join Strategy

The master table was built by left-joining `reviews` and `customers` onto the cleaned `orders` table. The reviews table has a 1-to-many relationship with `order_id` — the most common silent bug on this dataset. To prevent row inflation, reviews were collapsed to one row per `order_id` (keeping the most recent review by creation date) before the join. Both joins are guarded by an `assert` confirming the master table row count equals the cleaned orders count. **No row inflation occurred.** 99.3% of the master table has a review attached.

### Feature Engineering

Two delay features were derived:

- `Days_Difference = order_estimated_delivery_date - order_delivered_customer_date` (positive = early, per the brief)
- `Delay_Days = -Days_Difference`, used for the three-bucket classifier:
  - **On Time** (`Delay_Days <= 0`)
  - **Late** (`0 < Delay_Days <= 5`)
  - **Super Late** (`Delay_Days > 5`)

The sign-flipped helper exists so the bucketing rules read naturally and avoid the common error of inverting the late/early condition.

### Bonus — Product Category Translation

The `product_category_name` column ships in Portuguese (e.g., `cama_mesa_banho`). I attached the English translation from `product_category_name_translation.csv` via a left join on `product_category_name`, achieving **98.6% coverage**. The remaining 1.4% are Olist products with null category names — a known data-quality issue in the source. The English categories are surfaced in the dashboard's "Top Product Categories by Late Rate" chart.

### Candidate's Choice — Promise Gap by State

A state-level analysis comparing **median promised delivery time** (estimated date - purchase date) against **median actual delivery time** (delivered date - purchase date), plotted as a scatter with bubble size proportional to order volume.

**Why it matters to the business.** The standard "% late by state" chart tells the CEO *where* the problem is, but not *which lever to pull*. The promise-gap view separates two distinct failure modes: a state can be late because the carrier is slow (fix operations) or because the website is over-promising relative to realistic carrier performance (fix the estimator). High-late-rate states with small promise-vs-actual gaps need carrier intervention; high-late-rate states with already-long promises need an estimator that reflects reality. This converts a diagnostic into a routing decision for the operations team.

## Repository Structure

​```
last-mile-auditor/
├── README.md                             # This file — Executive Summary, Links, Technical notes
├── Last_Mile_Logistics_Auditor.ipynb     # Main analysis notebook
├── Last_Mile_Logistics_Auditor.html      # HTML export for GitHub viewing
├── Last_Mile_Logistics_Auditor.pdf     # pdf export for GitHub viewing
├── .gitignore                            # Excludes raw Olist CSVs
└── dashboard/                            # Streamlit dashboard (deploys to Streamlit Cloud)
    ├── app.py
    ├── requirements.txt
    ├── runtime.txt
    ├── README.md                         # Dashboard-specific README
    ├── data/
    │   └── master_dataset.csv            # Pre-cleaned data produced by the notebook
    └── .streamlit/config.toml
​```

## Running the Notebook Locally

1. Download the [Olist dataset from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and unzip the CSVs into `./data/` at the project root.
2. Install dependencies: `pip install pandas numpy matplotlib jupyter`
3. Open `Last_Mile_Logistics_Auditor.ipynb` and Run All. The notebook produces `data/master_dataset.csv`, which the dashboard reads.

Raw Olist CSVs are excluded from version control via `.gitignore`. Only the pre-cleaned `master_dataset.csv` is committed (under `dashboard/data/`) so the deployed dashboard has the data it needs.
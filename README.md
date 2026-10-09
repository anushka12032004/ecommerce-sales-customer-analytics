# 🛒 E-commerce Sales & Customer Analytics Dashboard

Interactive dashboard analysing **~400K transactions** of a UK-based online gift retailer (Dec 2010 – Dec 2011).

**Live demo:** _add your Streamlit link here_
**Tech:** Python, Pandas, Plotly, Streamlit
**Dataset:** [Kaggle: E-Commerce Data](https://www.kaggle.com/datasets/carrie1/ecommerce-data) (UCI Online Retail)

## Features
- KPI cards: revenue, orders, customers, average order value
- Filters by country and date range
- Monthly revenue trend, top products, top countries
- Day x Hour purchase-time heatmap
- RFM customer segmentation (Champions, Loyal, At Risk, Lost, Potential)
- Monthly cohort retention heatmap

## Data cleaning
- Dropped rows with missing CustomerID
- Removed cancelled invoices (InvoiceNo starting with "C")
- Removed non-positive quantity and price
- Removed an extreme bulk order (quantity of 80,995 units, later cancelled under a different invoice) that distorted the top-product chart

## Key findings and recommendations

| # | Finding | Recommendation |
|---|---|---|
| 1 | **Champions are 13.7% of customers but generate 52.3% of revenue.** Champions + Loyal together are 34.9% of customers and 76.0% of revenue. | Launch a VIP/loyalty programme with early access and free shipping for these two groups. |
| 2 | **Revenue peaks in November** (about £0.98M, UK) versus about £0.4-0.5M in the first half of the year, roughly double. (December is incomplete; data ends 9 Dec.) | Build stock and run marketing campaigns from September to November. |
| 3 | **Only about 20% of new customers return in their second month** (Jan-Oct 2011 cohorts). | Send a post-purchase email series (day 7 and day 21) with a second-order discount. |
| 4 | **654 "At Risk" customers hold £1.05M (12.2% of revenue)**: they bought often but have gone quiet. | Run a targeted win-back campaign for this group first, because it is cheaper than acquiring new customers. |
| 5 | **The UK generates 81.5% of revenue** (£7.06M of £8.67M) and 90% of customers. Sales happen Tuesday to Thursday, 10am-3pm; **no sales on Saturday**. | Schedule email campaigns for Tuesday-Thursday mornings. Test international marketing to reduce dependence on one market. |

## Run locally
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
Place `data.csv` (from Kaggle) in the same folder.

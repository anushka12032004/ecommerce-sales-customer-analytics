import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="E-commerce Analytics", layout="wide")


@st.cache_data
def load():
    df = pd.read_csv("data.csv", encoding="latin1")
    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]  # remove cancellations
    df = df[(df.Quantity > 0) & (df.UnitPrice > 0)]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Revenue"] = df.Quantity * df.UnitPrice
    df["Month"] = df.InvoiceDate.dt.strftime("%Y-%m")
    df["Hour"] = df.InvoiceDate.dt.hour
    df["Day"] = df.InvoiceDate.dt.day_name()
    return df.reset_index(drop=True)


df = load()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
countries = st.sidebar.multiselect(
    "Country", sorted(df.Country.unique()), default=["United Kingdom"]
)
dmin, dmax = df.InvoiceDate.min().date(), df.InvoiceDate.max().date()
dates = st.sidebar.date_input("Date range", (dmin, dmax), dmin, dmax)
if countries:
    df = df[df.Country.isin(countries)]
if len(dates) == 2:
    df = df[(df.InvoiceDate.dt.date >= dates[0]) & (df.InvoiceDate.dt.date <= dates[1])]
df = df.copy()

st.title("🛒 E-commerce Sales & Customer Analytics")

if df.empty:
    st.warning("No data for these filters.")
    st.stop()

# ---------- KPIs ----------
orders = df.InvoiceNo.nunique()
rev = df.Revenue.sum()
cust = df.CustomerID.nunique()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"£{rev:,.0f}")
c2.metric("Orders", f"{orders:,}")
c3.metric("Customers", f"{cust:,}")
c4.metric("Avg Order Value", f"£{rev / orders:,.2f}")

tab1, tab2, tab3 = st.tabs(["📈 Sales", "👥 Customers (RFM)", "🔁 Retention"])

# ---------- Sales ----------
with tab1:
    m = df.groupby("Month").Revenue.sum().reset_index()
    st.plotly_chart(
        px.line(m, x="Month", y="Revenue", markers=True, title="Monthly Revenue"),
        width="stretch",
    )
    a, b = st.columns(2)
    top = df.groupby("Description").Revenue.sum().nlargest(10).reset_index()
    a.plotly_chart(
        px.bar(top, x="Revenue", y="Description", orientation="h",
               title="Top 10 Products by Revenue"),
        width="stretch",
    )
    ctry = df.groupby("Country").Revenue.sum().nlargest(10).reset_index()
    b.plotly_chart(
        px.bar(ctry, x="Country", y="Revenue", title="Top Countries"),
        width="stretch",
    )
    heat = df.groupby(["Day", "Hour"]).Revenue.sum().reset_index()
    st.plotly_chart(
        px.density_heatmap(heat, x="Hour", y="Day", z="Revenue",
                           title="When do customers buy? (Day x Hour)"),
        width="stretch",
    )

# ---------- RFM ----------
with tab2:
    snap = df.InvoiceDate.max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snap - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()
    rfm["R"] = pd.qcut(rfm.Recency.rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm.Frequency.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M"] = pd.qcut(rfm.Monetary.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)

    def seg(r):
        if r.R >= 4 and r.F >= 4:
            return "Champions"
        if r.R >= 3 and r.F >= 3:
            return "Loyal"
        if r.R <= 2 and r.F >= 3:
            return "At Risk"
        if r.R == 1 and r.F <= 2:
            return "Lost"
        return "Potential"

    rfm["Segment"] = rfm.apply(seg, axis=1)

    s = rfm.groupby("Segment").agg(
        Customers=("CustomerID", "count"), Revenue=("Monetary", "sum")
    ).reset_index()
    s["Customer %"] = (s.Customers / s.Customers.sum() * 100).round(1)
    s["Revenue %"] = (s.Revenue / s.Revenue.sum() * 100).round(1)

    a, b = st.columns(2)
    a.plotly_chart(
        px.pie(s, names="Segment", values="Customers", title="Customers by Segment"),
        width="stretch",
    )
    b.plotly_chart(
        px.bar(s, x="Segment", y="Revenue", title="Revenue by Segment"),
        width="stretch",
    )
    st.subheader("Segment summary (use these numbers in your README)")
    st.dataframe(s)
    st.subheader("Top 50 customers")
    st.dataframe(rfm.sort_values("Monetary", ascending=False).head(50))
    st.download_button("Download RFM table", rfm.to_csv(index=False), "rfm.csv")

# ---------- Cohort retention ----------
with tab3:
    d = df.copy()
    d["OrderMonth"] = d.InvoiceDate.dt.year * 12 + d.InvoiceDate.dt.month
    first = d.groupby("CustomerID").InvoiceDate.transform("min")
    d["CohortMonth"] = first.dt.year * 12 + first.dt.month
    d["Cohort"] = first.dt.strftime("%Y-%m")
    d["Index"] = d.OrderMonth - d.CohortMonth
    co = d.groupby(["Cohort", "Index"]).CustomerID.nunique().unstack(fill_value=0)
    ret = (co.divide(co[0], axis=0) * 100).round(1)
    st.plotly_chart(
        px.imshow(ret, text_auto=".0f", aspect="auto", color_continuous_scale="Blues",
                  title="Customer Retention % by Monthly Cohort (columns = months since first purchase)"),
        width="stretch",
    )

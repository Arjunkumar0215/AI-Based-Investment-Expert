import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================================
# INVESTMENT PORTFOLIO RULES
# ============================================================

PORTFOLIO_RULES = {
    "18-27": {
        "short": {
            "High": {"Stocks": 45, "Mutual Fund": 15, "Gold/Silver": 20, "Bond/FD": 20},
            "Moderate": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 30},
            "Low": {"Stocks": 25, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 35},
        },
        "medium": {
            "High": {"Stocks": 50, "Mutual Fund": 20, "Gold/Silver": 15, "Bond/FD": 15},
            "Moderate": {"Stocks": 40, "Mutual Fund": 20, "Gold/Silver": 20, "Bond/FD": 20},
            "Low": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 30},
        },
        "long": {
            "High": {"Stocks": 55, "Mutual Fund": 20, "Gold/Silver": 15, "Bond/FD": 10},
            "Moderate": {"Stocks": 45, "Mutual Fund": 20, "Gold/Silver": 20, "Bond/FD": 15},
            "Low": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 30},
        },
    },
    "28-40": {
        "short": {
            "High": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 35, "Bond/FD": 20},
            "Moderate": {"Stocks": 25, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 35},
            "Low": {"Stocks": 20, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 40},
        },
        "medium": {
            "High": {"Stocks": 40, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 20},
            "Moderate": {"Stocks": 35, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 25},
            "Low": {"Stocks": 25, "Mutual Fund": 10, "Gold/Silver": 35, "Bond/FD": 30},
        },
        "long": {
            "High": {"Stocks": 45, "Mutual Fund": 20, "Gold/Silver": 25, "Bond/FD": 10},
            "Moderate": {"Stocks": 40, "Mutual Fund": 15, "Gold/Silver": 30, "Bond/FD": 15},
            "Low": {"Stocks": 35, "Mutual Fund": 10, "Gold/Silver": 35, "Bond/FD": 20},
        },
    },
    "41-55": {
        "short": {
            "High": {"Stocks": 25, "Mutual Fund": 10, "Gold/Silver": 35, "Bond/FD": 30},
            "Moderate": {"Stocks": 20, "Mutual Fund": 10, "Gold/Silver": 35, "Bond/FD": 35},
            "Low": {"Stocks": 10, "Mutual Fund": 15, "Gold/Silver": 35, "Bond/FD": 40},
        },
        "medium": {
            "High": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 35, "Bond/FD": 20},
            "Moderate": {"Stocks": 25, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 35},
            "Low": {"Stocks": 20, "Mutual Fund": 10, "Gold/Silver": 40, "Bond/FD": 30},
        },
        "long": {
            "High": {"Stocks": 40, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 20},
            # Kept exactly as supplied by the user (totals 85%).
            "Moderate": {"Stocks": 30, "Mutual Fund": 15, "Gold/Silver": 30, "Bond/FD": 25},
            "Low": {"Stocks": 20, "Mutual Fund": 15, "Gold/Silver": 30, "Bond/FD": 35},
        },
    },
    "56-69": {
        "short": {
            "High": {"Stocks": 20, "Mutual Fund": 10, "Gold/Silver": 25, "Bond/FD": 45},
            "Moderate": {"Stocks": 15, "Mutual Fund": 10, "Gold/Silver": 20, "Bond/FD": 55},
            "Low": {"Stocks": 10, "Mutual Fund": 10, "Gold/Silver": 15, "Bond/FD": 65},
        },
        "medium": {
            "High": {"Stocks": 25, "Mutual Fund": 15, "Gold/Silver": 30, "Bond/FD": 30},
            "Moderate": {"Stocks": 20, "Mutual Fund": 10, "Gold/Silver": 30, "Bond/FD": 40},
            "Low": {"Stocks": 15, "Mutual Fund": 10, "Gold/Silver": 25, "Bond/FD": 50},
        },
        "long": {
            "High": {"Stocks": 25, "Mutual Fund": 20, "Gold/Silver": 35, "Bond/FD": 20},
            "Moderate": {"Stocks": 20, "Mutual Fund": 20, "Gold/Silver": 30, "Bond/FD": 30},
            "Low": {"Stocks": 15, "Mutual Fund": 15, "Gold/Silver": 25, "Bond/FD": 45},
        },
    },
    "70+": {
        "safe": {"Stocks": 10, "Mutual Fund": 10, "Gold/Silver": 20, "Bond/FD": 60}
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def age_group(age: int) -> str:
    if 18 <= age <= 27:
        return "18-27"
    if 28 <= age <= 40:
        return "28-40"
    if 41 <= age <= 55:
        return "41-55"
    if 56 <= age <= 69:
        return "56-69"
    if age >= 70:
        return "70+"
    return "Under 18"


def period_group(years: float) -> str:
    if years < 3:
        return "short"
    if years <= 8:
        return "medium"
    return "long"


def period_label(period: str) -> str:
    return {
        "short": "Less than 3 years",
        "medium": "3–8 years",
        "long": "More than 8 years (up to 30 years)",
        "safe": "Age 70+ safety allocation",
    }.get(period, period)


def get_portfolio(age: int, years: float | None = None, risk: str | None = None):
    if age >= 70:
        return PORTFOLIO_RULES["70+"]["safe"], "70+", "safe"

    group = age_group(age)
    period = period_group(years)

    if risk not in {"High", "Moderate", "Low"}:
        raise ValueError("Risk must be High, Moderate, or Low.")

    return PORTFOLIO_RULES[group][period][risk], group, period


def normalize_weights(portfolio: dict) -> tuple[dict, float]:
    total = sum(portfolio.values())
    if total == 0:
        return portfolio.copy(), 0
    normalized = {k: (v / total) * 100 for k, v in portfolio.items()}
    return normalized, total


def distribution_df(portfolio: dict, amount: float) -> pd.DataFrame:
    rows = []
    for asset, pct in portfolio.items():
        rows.append(
            {
                "Asset": asset,
                "Allocation (%)": pct,
                "Amount (₹)": amount * pct / 100,
            }
        )
    return pd.DataFrame(rows)


def format_inr(value: float) -> str:
    return f"₹{value:,.2f}"


def investment_reasons(age: int, years: float | None, risk: str | None, portfolio: dict) -> list[str]:
    reasons = []

    if age >= 70:
        reasons.append("The portfolio is designed around capital preservation with a high Bond/FD allocation.")
        reasons.append("The lower stock allocation aims to reduce portfolio volatility.")
        reasons.append("Gold/Silver adds diversification rather than relying on a single asset type.")
        reasons.append("This is a safety-oriented rule from your allocation model.")
        return reasons

    if years < 3:
        reasons.append("The short investment horizon favors more defensive assets because there is less time to recover from market declines.")
    elif years <= 8:
        reasons.append("The medium-term horizon allows a balanced mix between growth assets and relatively stable assets.")
    else:
        reasons.append("The longer horizon gives the portfolio more room to use growth-oriented assets such as stocks and mutual funds.")

    if risk == "High":
        reasons.append("Your High-risk selection increases the allocation to growth assets, especially stocks.")
    elif risk == "Moderate":
        reasons.append("Your Moderate-risk selection balances growth potential with defensive allocations.")
    else:
        reasons.append("Your Low-risk selection places relatively more weight on defensive assets such as Gold/Silver and Bond/FD.")

    max_asset = max(portfolio, key=portfolio.get)
    reasons.append(f"{max_asset} receives the largest allocation in this rule set, reflecting the priorities of your selected profile.")

    return reasons


def suggestions(age: int, years: float | None, risk: str | None, portfolio: dict) -> list[str]:
    tips = [
        "Review the portfolio periodically instead of changing it because of short-term market movements.",
        "Keep an emergency fund separate from long-term investments.",
        "Consider diversification within each category rather than putting all of an allocation into one product.",
        "Check taxes, fees, liquidity, and product risk before investing.",
    ]

    if age >= 70:
        tips.insert(0, "Prioritize liquidity and capital preservation when choosing individual products within Bond/FD and other categories.")
    elif years < 3:
        tips.insert(0, "For a short horizon, avoid treating the stock allocation as guaranteed or capital-protected.")
    elif years > 8:
        tips.insert(0, "For a long horizon, review the portfolio annually and rebalance toward the target percentages when needed.")

    return tips


def build_report(age, years, risk, investment_amount, portfolio, annual_income=None):
    total_pct = sum(portfolio.values())
    group = age_group(age)
    period = "70+" if age >= 70 else period_group(years)

    lines = [
        f"Investment Profile: Age {age} ({group})",
        f"Risk Tolerance: {risk if risk else 'Safety allocation'}",
        f"Investment Period: {period_label(period)}",
        f"Investment Amount: {format_inr(investment_amount)}",
        f"Rule Allocation Total: {total_pct:.0f}%",
    ]

    if annual_income is not None:
        lines.append(f"Annual Income: {format_inr(annual_income)}")
        lines.append(f"Annual-Income-Based Investment (25%): {format_inr(annual_income * 0.25)}")

    if abs(total_pct - 100) > 0.01:
        lines.append(
            "Note: The selected rule totals less than 100%, so the displayed allocation follows your original rule exactly and leaves the remaining percentage unallocated."
        )

    return "\n".join(lines)



# ============================================================
# STREAMLIT UI — CLEAN / INTERACTIVE VERSION
# ============================================================

st.set_page_config(
    page_title="Investment Expert",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #374151 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,.12);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
    }

    .hero p {
        margin: .35rem 0 0;
        color: #d1d5db;
    }

    .profile-card {
        padding: 1rem 1.15rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 16px;
        background: rgba(128,128,128,.06);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin: .3rem 0 .7rem;
    }

    .asset-card {
        padding: .85rem 1rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,.22);
        margin-bottom: .55rem;
    }

    .asset-name {
        font-weight: 700;
        font-size: .98rem;
    }

    .asset-value {
        font-size: 1.25rem;
        font-weight: 800;
    }

    .muted {
        color: #6b7280;
        font-size: .85rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.2);
        padding: .65rem .8rem;
        border-radius: 14px;
        background: rgba(128,128,128,.04);
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>💼 Investment Expert</h1>
    <p>Build a simple portfolio recommendation from your age, investment horizon and risk profile.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar inputs
# -----------------------------
with st.sidebar:
    st.markdown("## 👤 Investor Profile")
    st.caption("Enter your details to generate a recommendation.")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=120,
        value=30,
        step=1,
        help="Your current age."
    )

    investment_amount = st.number_input(
        "Investment Amount (₹)",
        min_value=0.0,
        value=100000.0,
        step=10000.0,
        format="%.0f",
        help="Amount you want to allocate using this recommendation."
    )

    if age >= 70:
        years = None
        risk = None
        st.info("For age 70+, the model automatically uses its safety allocation.")
    else:
        years = st.slider(
            "Investment Horizon (Years)",
            min_value=0.0,
            max_value=30.0,
            value=10.0,
            step=0.5,
            help="How long you expect to stay invested."
        )

        risk = st.radio(
            "Risk Tolerance",
            ["Low", "Moderate", "High"],
            index=1,
            horizontal=True,
            help="Choose how much portfolio volatility you are comfortable with."
        )

    st.divider()

    with st.expander("💰 Optional income analysis"):
        annual_income_enabled = st.checkbox(
            "Calculate income-based investment",
            value=False
        )

        annual_income = None
        if annual_income_enabled:
            annual_income = st.number_input(
                "Annual Income (₹)",
                min_value=0.0,
                value=1000000.0,
                step=50000.0,
                format="%.0f"
            )

    st.caption("Educational tool — not personalized financial advice.")

try:
    portfolio, group, period = get_portfolio(age, years, risk)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

total_pct = sum(portfolio.values())
allocated_amount = investment_amount * total_pct / 100
unallocated_amount = investment_amount - allocated_amount

# -----------------------------
# Profile summary
# -----------------------------
st.markdown('<div class="section-title">Your Recommendation</div>', unsafe_allow_html=True)

profile_cols = st.columns(4)

profile_cols[0].metric("Age", f"{age}")
profile_cols[1].metric(
    "Horizon",
    "Safety allocation" if age >= 70 else period_label(period)
)
profile_cols[2].metric(
    "Risk",
    "Safety" if age >= 70 else risk
)
profile_cols[3].metric(
    "Rule Total",
    f"{total_pct:.0f}%"
)

if age >= 70:
    st.success("🛡️ Safety-oriented portfolio selected for age 70+.")
else:
    st.success(
        f"Recommended profile: **{group} · {period_label(period)} · {risk} Risk**"
    )

if abs(total_pct - 100) > 0.01:
    st.warning(
        f"This rule set totals **{total_pct:.0f}%**. "
        f"The remaining **{100-total_pct:.0f}%** is intentionally left unallocated "
        "because the original allocation rule was preserved."
    )

# -----------------------------
# Main dashboard
# -----------------------------
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown('<div class="section-title">📊 Portfolio Allocation</div>', unsafe_allow_html=True)

    for asset, pct in portfolio.items():
        amount = investment_amount * pct / 100
        st.markdown(
            f"""
            <div class="asset-card">
                <div class="asset-name">{asset}</div>
                <div class="asset-value">{pct:.0f}% · {format_inr(amount)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    m1, m2 = st.columns(2)
    m1.metric("Investment", format_inr(investment_amount))
    m2.metric("Allocated", format_inr(allocated_amount))

    if abs(total_pct - 100) > 0.01:
        st.metric("Unallocated", format_inr(unallocated_amount))

with right:
    st.markdown('<div class="section-title">🥧 Portfolio Mix</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    ax.pie(
        list(portfolio.values()),
        labels=list(portfolio.keys()),
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops={"width": 0.42, "edgecolor": "white"},
        pctdistance=0.78,
    )
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# -----------------------------
# Optional income analysis
# -----------------------------
if annual_income_enabled and annual_income is not None:
    st.divider()
    st.markdown('<div class="section-title">💰 Income-Based View</div>', unsafe_allow_html=True)

    annual_recommended = annual_income * 0.25

    i1, i2, i3 = st.columns(3)
    i1.metric("Annual Income", format_inr(annual_income))
    i2.metric("25% Annual Investment", format_inr(annual_recommended))
    i3.metric("Monthly Equivalent", format_inr(annual_recommended / 12))

    annual_table = distribution_df(portfolio, annual_recommended)
    annual_table["Allocation"] = annual_table["Allocation (%)"].map(lambda x: f"{x:.0f}%")
    annual_table["Amount"] = annual_table["Amount (₹)"].map(format_inr)

    st.dataframe(
        annual_table[["Asset", "Allocation", "Amount"]],
        hide_index=True,
        use_container_width=True
    )

# -----------------------------
# Insights
# -----------------------------
st.divider()
reason_col, suggestion_col = st.columns(2, gap="large")

with reason_col:
    with st.expander("💡 Why this allocation?", expanded=True):
        for reason in investment_reasons(age, years, risk, portfolio):
            st.markdown(f"- {reason}")

with suggestion_col:
    with st.expander("✅ Practical suggestions", expanded=True):
        for tip in suggestions(age, years, risk, portfolio):
            st.markdown(f"- {tip}")

# -----------------------------
# Report
# -----------------------------
st.divider()
st.markdown('<div class="section-title">📄 Report</div>', unsafe_allow_html=True)

report_text = build_report(
    age=age,
    years=years,
    risk=risk,
    investment_amount=investment_amount,
    portfolio=portfolio,
    annual_income=annual_income if annual_income_enabled else None,
)

with st.expander("View full report"):
    st.text_area(
        "Report Summary",
        value=report_text,
        height=220,
        label_visibility="collapsed"
    )

report_download = report_text + "\n\nPortfolio Distribution:\n"
for asset, pct in portfolio.items():
    amount = investment_amount * pct / 100
    report_download += f"- {asset}: {pct:.0f}% = {format_inr(amount)}\n"

if annual_income_enabled and annual_income is not None:
    report_download += "\nAnnual Income Recommendation (25%):\n"
    annual_recommended = annual_income * 0.25
    report_download += f"- Annual income: {format_inr(annual_income)}\n"
    report_download += f"- Recommended annual investment: {format_inr(annual_recommended)}\n"
    for asset, pct in portfolio.items():
        amount = annual_recommended * pct / 100
        report_download += f"- {asset}: {pct:.0f}% = {format_inr(amount)}\n"

st.download_button(
    "⬇️ Download Investment Report",
    data=report_download,
    file_name=f"investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    mime="text/plain",
    use_container_width=True,
)

st.caption(
    "Educational calculator based on the allocation rules supplied. "
    "It does not guarantee returns and is not individualized financial advice."
)


import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io

st.set_page_config(page_title="Real Estate Analyzer", layout="wide")
st.title("Real Estate Investment Analyzer")

# Sidebar Inputs
st.sidebar.header("Property Details")
st.sidebar.markdown("👈 **Use this panel to enter property details and get results.**")
st.info("📱 On mobile? Tap the top-left menu > to enter property info.")
purchase_price = st.sidebar.number_input("Purchase Price ($)", value=200000)
down_payment = st.sidebar.number_input("Down Payment ($)", value=40000)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=6.5)
loan_term = st.sidebar.number_input("Loan Term (years)", value=30)
annual_property_tax = st.sidebar.number_input("Annual Property Tax ($)", value=3600)
annual_insurance = st.sidebar.number_input("Annual Insurance ($)", value=1200)
monthly_maintenance = st.sidebar.number_input("Monthly Maintenance ($)", value=150)
square_footage = st.sidebar.number_input("Property Square Footage", value=1500)

st.sidebar.header("Local Comps")
avg_price_per_sqft = st.sidebar.number_input("Average Price per Sq Ft ($)", value=160.0)
avg_rent_per_sqft = st.sidebar.number_input("Average Rent per Sq Ft ($)", value=1.2)

st.sidebar.header("Rent & Market")
rent_low = st.sidebar.number_input("Low Rent Estimate ($)", value=1600)
rent_mid = st.sidebar.number_input("Mid Rent Estimate ($)", value=1800)
rent_high = st.sidebar.number_input("High Rent Estimate ($)", value=2000)
appreciation_rate = st.sidebar.number_input("Annual Appreciation Rate (%)", value=3.0)
hold_years = st.sidebar.number_input("Hold Period (Years)", value=5)

st.sidebar.header("Flip Options")
rehab_cost = st.sidebar.number_input("Rehab Cost ($)", value=30000)
target_resale_value = st.sidebar.number_input("Target Resale Value After Rehab ($)", value=275000)

# Calculations
loan_amount = purchase_price - down_payment
monthly_interest = interest_rate / 12 / 100
months = loan_term * 12
mortgage = loan_amount * (monthly_interest * (1 + monthly_interest)**months) / ((1 + monthly_interest)**months - 1)

monthly_property_tax = annual_property_tax / 12
monthly_insurance = annual_insurance / 12
total_monthly_cost = mortgage + monthly_property_tax + monthly_insurance + monthly_maintenance

future_value = purchase_price * ((1 + appreciation_rate / 100) ** hold_years)
appreciation_gain = future_value - purchase_price
flip_profit = target_resale_value - purchase_price - rehab_cost

# Sq Ft Comps
market_value_by_sqft = avg_price_per_sqft * square_footage
rent_estimate_by_sqft = avg_rent_per_sqft * square_footage

# Rent Scenarios
rent_data = []
for rent in [rent_low, rent_mid, rent_high]:
    cash_flow = rent - total_monthly_cost
    annual_profit = cash_flow * 12
    total_cash_invested = down_payment + (monthly_maintenance * 12 * hold_years)
    roi = ((annual_profit * hold_years) + appreciation_gain) / total_cash_invested * 100

    if roi >= 10 and cash_flow > 0:
        strategy = "Good Rental"
        color = "green"
    elif appreciation_gain / purchase_price >= 0.15 and cash_flow < 100:
        strategy = "Better as a Flip"
        color = "blue"
    elif roi < 5 and cash_flow < 0:
        strategy = "Bad Buy"
        color = "red"
    else:
        strategy = "Depends on Goals"
        color = "orange"

    rent_data.append({
        "Rent": rent,
        "Monthly Cash Flow": round(cash_flow, 2),
        "Annual Profit": round(annual_profit, 2),
        "ROI (%)": round(roi, 2),
        "Strategy": strategy,
        "Color": color
    })

df = pd.DataFrame(rent_data)

# Output Section
st.subheader("Monthly Ownership Cost Breakdown")
st.write(f"**Mortgage**: ${mortgage:.2f}")
st.write(f"**Total Monthly Cost**: ${total_monthly_cost:.2f}")

st.subheader("Appreciation Forecast")
st.write(f"Future Value After {hold_years} Years: **${future_value:,.2f}**")
st.write(f"Expected Appreciation Gain: **${appreciation_gain:,.2f}**")

st.subheader("Flip Profit Analysis")
st.write(f"Flip Profit (Resale - Purchase - Rehab): **${flip_profit:,.2f}**")

st.subheader("Sq Ft Comparison Analysis")
st.write(f"**Estimated Market Value (by area comps):** ${market_value_by_sqft:,.2f}")
st.write(f"**Your Purchase Price:** ${purchase_price:,.2f}")
st.write(f"**Difference:** ${market_value_by_sqft - purchase_price:,.2f}")
st.write(f"**Estimated Rent (by area comps):** ${rent_estimate_by_sqft:,.2f}")

st.subheader("Rental Strategy Comparison")
for i, row in df.iterrows():
    st.markdown(
        f'''
        <div style="padding: 10px; border-left: 5px solid {row["Color"]}; background-color: #f9f9f9; margin-bottom: 10px;">
            <strong>Rent:</strong> ${row["Rent"]} <br>
            <strong>Monthly Cash Flow:</strong> ${row["Monthly Cash Flow"]} <br>
            <strong>Annual Profit:</strong> ${row["Annual Profit"]} <br>
            <strong>ROI:</strong> {row["ROI (%)"]}% <br>
            <strong>Strategy:</strong> <span style="color:{row["Color"]}; font-weight:bold;">{row["Strategy"]}</span>
        </div>
        ''', unsafe_allow_html=True
    )

# Chart
st.subheader("Cash Flow Comparison")
fig, ax = plt.subplots()
ax.bar(df["Rent"], df["Monthly Cash Flow"], color=df["Color"])
ax.set_xlabel("Rent Price ($)")
ax.set_ylabel("Monthly Cash Flow ($)")
ax.set_title("Monthly Cash Flow by Rent Tier")
st.pyplot(fig)

# Export Options
st.subheader("Export Report")
export_format = st.selectbox("Select Export Format", ["Excel", "CSV"])
if export_format == "Excel":
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Rental Analysis', index=False)
    st.download_button("Download Excel Report", buffer.getvalue(), file_name="real_estate_report.xlsx")
else:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV Report", csv, file_name="real_estate_report.csv")

# profit_loss.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_profit_loss_section():
    """Create profit and loss forecast section"""
    left_column, right_column = st.columns([1, 2])

    # Historical data (2023)
    historical_data = {
        "Revenue(A)": 1000,
        "Cost(B)": 600,
        "Gross Profit(A-B)": 400,
        "Selling Expense(C)": 100,
        "Admin Expense(D)": 80,
        "Financial Expense(E)": 20,
        "Net Profit(A-B-C-D-E)": 200,
    }

    with left_column:
        st.subheader("Historical Data (2023)")
        hist_df = pd.DataFrame({"Amount": historical_data}).round(2)
        st.dataframe(hist_df)

        st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
        st.markdown("### Revenue Growth Rate")
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        years = ["2024E", "2025E", "2026E"]

        # Revenue growth settings
        revenue_growth_rates = []
        for year in years:
            growth = st.slider(
                f"{year} Growth Rate(%)",
                min_value=0.0,
                max_value=50.0,
                value=15.0,
                step=1.0,
                key=f"revenue_growth_{year}"
            ) / 100
            revenue_growth_rates.append(growth)

        st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
        st.markdown("### Cost/Revenue Ratio")
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        # Cost ratio settings
        cost_ratios = []
        for year in years:
            ratio = st.slider(
                f"{year} Cost Ratio(%)",
                min_value=40.0,
                max_value=80.0,
                value=60.0,
                step=1.0,
                key=f"cost_ratio_{year}"
            ) / 100
            cost_ratios.append(ratio)

        st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
        st.markdown("### Expense Ratios")
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

        # Expense ratios
        sales_expense_ratios = []
        management_expense_ratios = []
        financial_expense_ratios = []

        for year in years:
            st.markdown(f"**{year}**")
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                sales = st.slider(
                    "Selling(%)",
                    min_value=0.0,
                    max_value=30.0,
                    value=10.0,
                    step=0.5,
                    key=f"sales_{year}"
                ) / 100
                sales_expense_ratios.append(sales)

            with col2:
                management = st.slider(
                    "Admin(%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=7.0,
                    step=0.5,
                    key=f"management_{year}"
                ) / 100
                management_expense_ratios.append(management)

            with col3:
                financial = st.slider(
                    "Financial(%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=2.0,
                    step=0.5,
                    key=f"financial_{year}"
                ) / 100
                financial_expense_ratios.append(financial)

            st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    forecast_df = None

    if st.button("Generate P&L Forecast"):
        # Generate forecast data
        forecast_years = ["2023A"] + years
        revenues = [historical_data["Revenue(A)"]]

        # Calculate revenues
        for growth_rate in revenue_growth_rates:
            revenues.append(revenues[-1] * (1 + growth_rate))

        # Calculate costs and profits
        costs = [historical_data["Cost(B)"]] + [rev * ratio for rev, ratio in zip(revenues[1:], cost_ratios)]
        gross_profits = [rev - cost for rev, cost in zip(revenues, costs)]

        sales_expenses = [historical_data["Selling Expense(C)"]] + [rev * ratio for rev, ratio in
                                                                    zip(revenues[1:], sales_expense_ratios)]
        management_expenses = [historical_data["Admin Expense(D)"]] + [rev * ratio for rev, ratio in
                                                                       zip(revenues[1:], management_expense_ratios)]
        financial_expenses = [historical_data["Financial Expense(E)"]] + [rev * ratio for rev, ratio in
                                                                          zip(revenues[1:], financial_expense_ratios)]

        operating_profits = [
            rev - cost - sales - mgmt - fin
            for rev, cost, sales, mgmt, fin in zip(
                revenues, costs, sales_expenses, management_expenses, financial_expenses
            )
        ]

        # Create forecast DataFrame
        data = {
            "Revenue(A)": revenues,
            "Cost(B)": costs,
            "Gross Profit(A-B)": gross_profits,
            "Selling Expense(C)": sales_expenses,
            "Admin Expense(D)": management_expenses,
            "Financial Expense(E)": financial_expenses,
            "Net Profit(A-B-C-D-E)": operating_profits
        }

        forecast_df = pd.DataFrame(data, index=forecast_years).T

        # Display results
        with right_column:
            st.subheader("Key Metrics")
            col1, col2, col3 = st.columns(3)

            with col1:
                gross_margins = [gp / rev for gp, rev in zip(gross_profits, revenues)]
                st.metric(
                    "Gross Margin",
                    f"{gross_margins[-1]:.1%}",
                    f"{(gross_margins[-1] - gross_margins[0]):.1%}"
                )

            with col2:
                net_margins = [np / rev for np, rev in zip(operating_profits, revenues)]
                st.metric(
                    "Net Margin",
                    f"{net_margins[-1]:.1%}",
                    f"{(net_margins[-1] - net_margins[0]):.1%}"
                )

            with col3:
                revenue_growth = (revenues[-1] / revenues[0]) ** (1 / 3) - 1
                st.metric(
                    "Revenue CAGR",
                    f"{revenue_growth:.1%}",
                    ""
                )

            # Charts
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Financial Performance', 'Margin Trends'),
                vertical_spacing=0.12
            )

            # Financial performance trend
            fig.add_trace(
                go.Bar(
                    name='Revenue',
                    x=years,
                    y=revenues[1:],
                    marker_color='lightblue'
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Bar(
                    name='Net Profit',
                    x=years,
                    y=operating_profits[1:],
                    marker_color='darkblue'
                ),
                row=1, col=1
            )

            # Margin trends
            fig.add_trace(
                go.Scatter(
                    name='Gross Margin',
                    x=years,
                    y=gross_margins[1:],
                    mode='lines+markers',
                    line=dict(color='green')
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    name='Net Margin',
                    x=years,
                    y=net_margins[1:],
                    mode='lines+markers',
                    line=dict(color='red')
                ),
                row=2, col=1
            )

            # Update layout
            fig.update_layout(
                height=600,
                showlegend=True,
                title_text="Financial Analysis"
            )

            # Update y-axes labels
            fig.update_yaxes(title_text="Amount", row=1, col=1)
            fig.update_yaxes(title_text="Ratio", row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # Display forecast table
            st.subheader("P&L Forecast")
            st.dataframe(forecast_df.round(2))

            st.success("✅ P&L Forecast Generated")

    return forecast_df


if __name__ == "__main__":
    st.set_page_config(page_title="P&L Forecast", layout="wide")
    st.title("P&L Forecast")
    create_profit_loss_section()
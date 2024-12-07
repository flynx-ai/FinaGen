# cash_flow.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_cash_flow_section(profit_loss_data, balance_sheet_data):
    """
    Create cash flow statement forecast
    profit_loss_data: P&L forecast DataFrame
    balance_sheet_data: Balance sheet forecast DataFrame
    """
    left_column, right_column = st.columns([1.2, 1.8])

    with left_column:
        st.subheader("Cash Flow Assumptions")

        # Depreciation assumption
        depreciation_rate = st.slider(
            "Fixed Assets Depreciation Rate(%)",
            min_value=0.0,
            max_value=20.0,
            value=10.0,
            step=0.5,
            help="Annual depreciation rate"
        ) / 100

    if st.button("Generate Cash Flow Forecast"):
        try:
            years = ["2023A", "2024E", "2025E", "2026E"]

            # Get data from P&L
            net_profits = profit_loss_data.loc["Net Profit(A-B-C-D-E)"].values

            # Get data from Balance Sheet
            fixed_assets = balance_sheet_data.loc["Fixed Assets(I)"].values
            receivables = balance_sheet_data.loc["Accounts Receivable(G)"].values
            prepayments = balance_sheet_data.loc["Prepayments(H)"].values
            payables = balance_sheet_data.loc["Accounts Payable(J)"].values
            advances = balance_sheet_data.loc["Advances from Customers(K)"].values
            capital_changes = np.diff(balance_sheet_data.loc["Share Capital(L)"].values)

            # Calculate depreciation
            depreciation = fixed_assets * depreciation_rate

            # Calculate working capital changes
            receivables_change = np.diff(receivables)
            prepayments_change = np.diff(prepayments)
            payables_change = np.diff(payables)
            advances_change = np.diff(advances)

            # Initialize cash flows
            operating_cash_flows = []
            investing_cash_flows = []
            financing_cash_flows = []

            # First year data
            operating_cash_flows.append(net_profits[0] + depreciation[0])
            investing_cash_flows.append(0)
            financing_cash_flows.append(0)

            # Calculate cash flows for forecast years
            for i in range(1, 4):
                # Operating cash flow
                operating_cf = (
                        net_profits[i] +  # Net profit
                        depreciation[i] -  # Add back depreciation
                        receivables_change[i - 1] -  # Change in receivables
                        prepayments_change[i - 1] +  # Change in prepayments
                        payables_change[i - 1] +  # Change in payables
                        advances_change[i - 1]  # Change in advances
                )
                operating_cash_flows.append(operating_cf)

                # Investing cash flow (fixed assets investment)
                investing_cf = -(fixed_assets[i] - fixed_assets[i - 1] + depreciation[i])
                investing_cash_flows.append(investing_cf)

                # Financing cash flow
                financing_cf = capital_changes[i - 1]
                financing_cash_flows.append(financing_cf)

            # Calculate net cash flow
            net_cash_flows = [
                op + inv + fin
                for op, inv, fin in zip(
                    operating_cash_flows,
                    investing_cash_flows,
                    financing_cash_flows
                )
            ]

            # Create cash flow statement
            cash_flow_data = {
                "Operating Cash Flow(N)": operating_cash_flows,
                "Investing Cash Flow(O)": investing_cash_flows,
                "Financing Cash Flow(P)": financing_cash_flows,
                "**Net Cash Flow(N+O+P)**": net_cash_flows
            }

            # Create DataFrame
            cash_flow_df = pd.DataFrame(cash_flow_data, index=years).T

            with right_column:
                # Display key metrics
                st.subheader("Key Metrics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    operating_cf_ratio = [
                        ocf / np if np != 0 else 0
                        for ocf, np in zip(operating_cash_flows, net_profits)
                    ]
                    st.metric(
                        "Operating CF / Net Profit",
                        f"{operating_cf_ratio[-1]:.1%}",
                        f"{(operating_cf_ratio[-1] - operating_cf_ratio[0]):.1%}"
                    )

                with col2:
                    capex_ratio = [
                        -icf / ocf if ocf != 0 else 0
                        for icf, ocf in zip(investing_cash_flows, operating_cash_flows)
                    ]
                    st.metric(
                        "CAPEX / Operating CF",
                        f"{capex_ratio[-1]:.1%}",
                        f"{(capex_ratio[-1] - capex_ratio[0]):.1%}"
                    )

                with col3:
                    cf_growth = (net_cash_flows[-1] / net_cash_flows[0]) ** (1 / 3) - 1 if net_cash_flows[0] != 0 else 0
                    st.metric(
                        "Net CF CAGR",
                        f"{cf_growth:.1%}",
                        ""
                    )

                # Create visualization
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=(
                        'Cash Flow Components',
                        'Cash Flow Waterfall',
                        'Cash Flow Trends',
                        'Cash Flow Composition'
                    ),
                    specs=[
                        [{"type": "bar"}, {"type": "waterfall"}],
                        [{"type": "scatter"}, {"type": "pie"}]  # 明确指定饼图类型
                    ]
                )

                # Cash Flow Components
                fig.add_trace(
                    go.Bar(
                        name='Operating CF',
                        x=years[1:],
                        y=operating_cash_flows[1:],
                        marker_color='green'
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Bar(
                        name='Investing CF',
                        x=years[1:],
                        y=investing_cash_flows[1:],
                        marker_color='red'
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Bar(
                        name='Financing CF',
                        x=years[1:],
                        y=financing_cash_flows[1:],
                        marker_color='blue'
                    ),
                    row=1, col=1
                )

                # Waterfall chart
                fig.add_trace(
                    go.Waterfall(
                        name="Waterfall",
                        orientation="v",
                        measure=["relative"] * 3,
                        x=["Operating", "Investing", "Financing"],
                        y=[operating_cash_flows[-1], investing_cash_flows[-1], financing_cash_flows[-1]],
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                    ),
                    row=1, col=2
                )

                # Cash Flow Trends
                fig.add_trace(
                    go.Scatter(
                        name='Net Cash Flow',
                        x=years,
                        y=net_cash_flows,
                        mode='lines+markers',
                        line=dict(color='purple', width=2)
                    ),
                    row=2, col=1
                )

                # Cash Flow Composition (Pie Chart)
                last_year_data = {
                    'Operating': abs(operating_cash_flows[-1]),
                    'Investing': abs(investing_cash_flows[-1]),
                    'Financing': abs(financing_cash_flows[-1])
                }
                fig.add_trace(
                    go.Pie(
                        values=list(last_year_data.values()),
                        labels=list(last_year_data.keys()),
                        hole=0.3
                    ),
                    row=2, col=2
                )

                fig.update_layout(
                    height=800,
                    width=None,
                    showlegend=True,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display forecast table
                st.subheader("Cash Flow Forecast")
                st.dataframe(
                    cash_flow_df.round(2),
                    width=None,
                    height=None
                )

                st.success("✅ Cash Flow Forecast Generated")

        except Exception as e:
            st.error(f"Error generating cash flow forecast: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(page_title="Cash Flow Forecast", layout="wide")
    st.title("Cash Flow Forecast")

    # Example data for testing
    example_pl_data = pd.DataFrame({
        "2023A": {"Net Profit(A-B-C-D-E)": 200},
        "2024E": {"Net Profit(A-B-C-D-E)": 230},
        "2025E": {"Net Profit(A-B-C-D-E)": 264.5},
        "2026E": {"Net Profit(A-B-C-D-E)": 304.17}
    }).T

    example_bs_data = pd.DataFrame({
        "2023A": {"Fixed Assets(I)": 16, "Accounts Receivable(G)": 110},
        "2024E": {"Fixed Assets(I)": 19.2, "Accounts Receivable(G)": 126.5},
        "2025E": {"Fixed Assets(I)": 23.04, "Accounts Receivable(G)": 145.48},
        "2026E": {"Fixed Assets(I)": 27.65, "Accounts Receivable(G)": 167.3}
    }).T

    create_cash_flow_section(example_pl_data, example_bs_data)
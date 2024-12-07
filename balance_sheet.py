# balance_sheet.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_balance_sheet_section(profit_loss_data):
    """
    Create balance sheet forecast section
    profit_loss_data: DataFrame with P&L forecast data
    """
    left_column, right_column = st.columns([1.2, 1.8])

    # Historical data (2023)
    historical_bs = {
        "Cash(F)": 1260.00,
        "Accounts Receivable(G)": 110.00,
        "Prepayments(H)": 6.00,
        "Fixed Assets(I)": 16.00,
        "Total Assets(F+G+H+I)": 1392.00,  # 移除加粗标记
        "Accounts Payable(J)": 120.00,
        "Advances from Customers(K)": 10.00,
        "Total Liabilities(J+K)": 130.00,  # 移除加粗标记
        "Share Capital(L)": 1333.52,
        "Retained Earnings(M)": -71.52,
        "Total Equity(L+M)": 1262.00,
        "Total Liabilities & Equity(J+K+L+M)": 1392.00  # 移除加粗标记
    }

    with left_column:
        st.subheader("Historical Data (2023)")
        hist_df = pd.DataFrame({"Amount": historical_bs}).round(2)

        st.dataframe(
            hist_df,
            width=800,  # 增加宽度
            height=None  # 自动调整高度
        )
        st.subheader("Forecast Assumptions")

        # Working capital ratios
        st.markdown("##### Working Capital Ratios")
        receivables_ratio = st.slider("AR/Revenue Ratio", 0.0, 0.3, 0.11, 0.01,
                                      help="Accounts Receivable as % of Revenue")
        prepayment_ratio = st.slider("Prepayment/Cost Ratio", 0.0, 0.1, 0.01, 0.01,
                                     help="Prepayments as % of Cost")
        payables_ratio = st.slider("AP/Cost Ratio", 0.0, 0.4, 0.20, 0.01,
                                   help="Accounts Payable as % of Cost")
        advance_ratio = st.slider("Customer Advances/Revenue", 0.0, 0.1, 0.01, 0.01,
                                  help="Advances as % of Revenue")

        # Asset growth
        st.markdown("##### Asset Growth")
        fixed_asset_growth = st.slider("Fixed Assets Growth Rate", 0.0, 0.5, 0.20, 0.01,
                                       help="Annual growth rate of fixed assets")

        # Equity changes
        st.markdown("##### Equity Changes")
        capital_increase = st.number_input("Capital Increase in 2024", value=325.00, step=10.0,
                                           help="Additional capital in 2024")

    if st.button("Generate Balance Sheet Forecast"):
        try:
            years = ["2023A", "2024E", "2025E", "2026E"]
            revenues = profit_loss_data.loc["Revenue(A)"].values
            costs = profit_loss_data.loc["Cost(B)"].values
            net_profits = profit_loss_data.loc["Net Profit(A-B-C-D-E)"].values

            # Initialize forecast data
            forecast_data = {k: [v] for k, v in historical_bs.items()}

            # Generate forecast
            for i in range(1, 4):  # 3 forecast years
                # Calculate assets
                receivables = revenues[i] * receivables_ratio
                prepayments = costs[i] * prepayment_ratio
                fixed_assets = forecast_data["Fixed Assets(I)"][-1] * (1 + fixed_asset_growth)

                # Calculate liabilities
                payables = costs[i] * payables_ratio
                advances = revenues[i] * advance_ratio
                total_liabilities = payables + advances

                # Calculate equity
                capital = forecast_data["Share Capital(L)"][-1] + (capital_increase if i == 1 else 0)
                retained_earnings = forecast_data["Retained Earnings(M)"][-1] + net_profits[i]
                total_equity = capital + retained_earnings

                # Calculate balancing cash
                total_liab_equity = total_liabilities + total_equity
                other_assets = receivables + prepayments + fixed_assets
                cash = total_liab_equity - other_assets

                # Update forecast data
                forecast_data["Cash(F)"].append(cash)
                forecast_data["Accounts Receivable(G)"].append(receivables)
                forecast_data["Prepayments(H)"].append(prepayments)
                forecast_data["Fixed Assets(I)"].append(fixed_assets)
                forecast_data["Total Assets(F+G+H+I)"].append(total_liab_equity)
                forecast_data["Accounts Payable(J)"].append(payables)
                forecast_data["Advances from Customers(K)"].append(advances)
                forecast_data["Total Liabilities(J+K)"].append(total_liabilities)
                forecast_data["Share Capital(L)"].append(capital)
                forecast_data["Retained Earnings(M)"].append(retained_earnings)
                forecast_data["Total Equity(L+M)"].append(total_equity)
                forecast_data["Total Liabilities & Equity(J+K+L+M)"].append(total_liab_equity)

            # Create forecast DataFrame
            forecast_df = pd.DataFrame(forecast_data, index=years).T

            def style_dataframe(df):
                """为DataFrame添加样式"""
                return df.style.apply(lambda x: ['font-weight: bold' if i in [
                    'Total Assets(F+G+H+I)',
                    'Total Liabilities(J+K)',
                    'Total Liabilities & Equity(J+K+L+M)'
                ] else '' for i in x.index], axis=0)

            # Display results
            with right_column:
                # Key metrics
                st.subheader("Key Metrics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    debt_ratios = [
                        l / a for l, a in zip(
                            forecast_df.loc["Total Liabilities(J+K)"],
                            forecast_df.loc["Total Assets(F+G+H+I)"]
                        )
                    ]
                    st.metric(
                        "Debt Ratio",
                        f"{debt_ratios[-1]:.1%}",
                        f"{(debt_ratios[-1] - debt_ratios[0]):.1%}"
                    )

                with col2:
                    fixed_asset_ratios = [
                        f / a for f, a in zip(
                            forecast_df.loc["Fixed Assets(I)"],
                            forecast_df.loc["Total Assets(F+G+H+I)"]
                        )
                    ]
                    st.metric(
                        "Fixed Asset Ratio",
                        f"{fixed_asset_ratios[-1]:.1%}",
                        f"{(fixed_asset_ratios[-1] - fixed_asset_ratios[0]):.1%}"
                    )

                with col3:
                    equity_ratios = [
                        e / a for e, a in zip(
                            forecast_df.loc["Total Equity(L+M)"],
                            forecast_df.loc["Total Assets(F+G+H+I)"]
                        )
                    ]
                    st.metric(
                        "Equity Ratio",
                        f"{equity_ratios[-1]:.1%}",
                        f"{(equity_ratios[-1] - equity_ratios[0]):.1%}"
                    )

                # Charts
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=(
                        'Balance Sheet Structure',
                        'Asset Composition',
                        'Key Ratios Trend',
                        'Equity & Liability Composition'
                    ),
                    specs=[[{"type": "bar"}, {"type": "pie"}],
                           [{"type": "scatter"}, {"type": "pie"}]]
                )

                # Balance Sheet Structure
                fig.add_trace(
                    go.Bar(name='Total Assets',
                           x=years,
                           y=forecast_df.loc["Total Assets(F+G+H+I)"],
                           marker_color='lightblue'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Bar(name='Total Equity',
                           x=years,
                           y=forecast_df.loc["Total Equity(L+M)"],
                           marker_color='darkblue'),
                    row=1, col=1
                )
                fig.update_layout(
                    height=800,
                    width=None,  # 自动适应宽度
                    showlegend=True,
                    margin=dict(l=20, r=20, t=40, b=20)  # 减少边距
                )

                # Asset Composition (latest year)
                asset_composition = {
                    'Cash': forecast_df.loc["Cash(F)"].iloc[-1],
                    'AR': forecast_df.loc["Accounts Receivable(G)"].iloc[-1],
                    'Prepayments': forecast_df.loc["Prepayments(H)"].iloc[-1],
                    'Fixed Assets': forecast_df.loc["Fixed Assets(I)"].iloc[-1]
                }
                fig.add_trace(
                    go.Pie(values=list(asset_composition.values()),
                           labels=list(asset_composition.keys()),
                           name="Asset Composition"),
                    row=1, col=2
                )

                # Key Ratios Trend
                fig.add_trace(
                    go.Scatter(x=years, y=debt_ratios,
                               name='Debt Ratio',
                               mode='lines+markers'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=years, y=equity_ratios,
                               name='Equity Ratio',
                               mode='lines+markers'),
                    row=2, col=1
                )

                # Liability & Equity Composition (latest year)
                le_composition = {
                    'Liabilities': forecast_df.loc["Total Liabilities(J+K)"].iloc[-1],
                    'Equity': forecast_df.loc["Total Equity(L+M)"].iloc[-1]
                }
                fig.add_trace(
                    go.Pie(values=list(le_composition.values()),
                           labels=list(le_composition.keys()),
                           name="L&E Composition"),
                    row=2, col=2
                )

                fig.update_layout(height=800, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

                # Display forecast table
                st.subheader("Balance Sheet Forecast")
                st.dataframe(
                    forecast_df.round(2),
                    width=None,  # 自动适应宽度
                    height=None  # 自动调整高度
                )

            st.success("✅ Balance Sheet Forecast Generated")
            return forecast_df

        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")
            return None

    return None


if __name__ == "__main__":
    st.set_page_config(page_title="Balance Sheet Forecast", layout="wide")
    st.title("Balance Sheet Forecast")

    # Test data
    example_data = pd.DataFrame({
        "2023A": {"Revenue(A)": 1000, "Cost(B)": 600, "Net Profit(A-B-C-D-E)": 200},
        "2024E": {"Revenue(A)": 1150, "Cost(B)": 690, "Net Profit(A-B-C-D-E)": 230},
        "2025E": {"Revenue(A)": 1322.5, "Cost(B)": 793.5, "Net Profit(A-B-C-D-E)": 264.5},
        "2026E": {"Revenue(A)": 1520.87, "Cost(B)": 912.52, "Net Profit(A-B-C-D-E)": 304.17}
    }).T

    create_balance_sheet_section(example_data)
# main.py
import streamlit as st
import pandas as pd
from profit_loss import create_profit_loss_section
from balance_sheet import create_balance_sheet_section
from cash_flow import create_cash_flow_section


def init_session_state():
    """Initialize session state variables"""
    if 'profit_loss_data' not in st.session_state:
        st.session_state['profit_loss_data'] = None
    if 'balance_sheet_data' not in st.session_state:
        st.session_state['balance_sheet_data'] = None
    if 'is_pl_generated' not in st.session_state:
        st.session_state['is_pl_generated'] = False
    if 'is_bs_generated' not in st.session_state:
        st.session_state['is_bs_generated'] = False


def reset_all_data():
    """Reset all data"""
    st.session_state['profit_loss_data'] = None
    st.session_state['balance_sheet_data'] = None
    st.session_state['is_pl_generated'] = False
    st.session_state['is_bs_generated'] = False


# Page configuration
st.set_page_config(
    page_title="Financial Forecast Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Page title
st.title("Financial Forecast Model")

# Create tabs
tab1, tab2, tab3 = st.tabs(["P&L Forecast", "Balance Sheet Forecast", "Cash Flow Forecast"])

# P&L Tab
with tab1:
    pl_result = create_profit_loss_section()
    if pl_result is not None:
        st.session_state['profit_loss_data'] = pl_result
        st.session_state['is_pl_generated'] = True
        # Clear subsequent forecasts when P&L is regenerated
        st.session_state['balance_sheet_data'] = None
        st.session_state['is_bs_generated'] = False

# Balance Sheet Tab
with tab2:
    if st.session_state['is_pl_generated']:
        bs_result = create_balance_sheet_section(st.session_state['profit_loss_data'])
        if bs_result is not None:
            st.session_state['balance_sheet_data'] = bs_result
            st.session_state['is_bs_generated'] = True
    else:
        st.info("⚠️ Please generate P&L forecast first")

# Cash Flow Tab
with tab3:
    if st.session_state['is_pl_generated'] and st.session_state['is_bs_generated']:
        create_cash_flow_section(
            st.session_state['profit_loss_data'],
            st.session_state['balance_sheet_data']
        )
    else:
        if not st.session_state['is_pl_generated']:
            st.info("⚠️ Please generate P&L forecast first")
        elif not st.session_state['is_bs_generated']:
            st.info("⚠️ Please generate Balance Sheet forecast first")

# Sidebar
with st.sidebar:
    st.markdown("### Forecast Status")

    # Display status
    st.write("P&L: ",
             "✅ Generated" if st.session_state['is_pl_generated'] else "⏳ Pending")
    st.write("Balance Sheet: ",
             "✅ Generated" if st.session_state['is_bs_generated'] else "⏳ Pending")

    st.markdown("---")

    # Reset button
    if st.button("🔄 Reset All Data", help="Clear all forecast data and start over"):
        reset_all_data()
        st.experimental_rerun()

    # Instructions
    st.markdown("---")
    st.markdown("""
    #### Instructions
    1. Generate P&L forecast
    2. Generate Balance Sheet forecast
    3. View Cash Flow forecast

    Note: Regenerating P&L forecast will clear existing Balance Sheet forecast data.
    """)

if __name__ == "__main__":
    st.write("Please use the tabs above to generate forecasts.")
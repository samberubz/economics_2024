from datetime import datetime
import pandas as pd
import streamlit as st
import cufflinks as cf
import yfinance as yf
from fredapi import Fred
import plotly.graph_objects as go


def date_format(y):
    # Convert the string to a datetime object
    date_object = datetime.utcfromtimestamp(y)  # Adjust the format accordingly
    formatted_date = date_object.strftime("%B %d, %Y")
    return formatted_date


def format_int_with_commas(x):
    """
    Formats an integer with commas as thousand separators.
    """
    return f"{x:,}"


def plot_ei_v1(series, series_name, yLabel):
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=series.index, y=series.values, mode='lines', name=series_name, showlegend=True))
    fig1.update_layout(yaxis=dict(title=yLabel))
    st.plotly_chart(fig1, use_container_width=True)


def plot_ei_v2(series_US, series_CAN, yLabel):
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=series_US.index, y=series_US.values, mode='lines', name='U.S.'))
    fig2.add_trace(go.Scatter(x=series_CAN.index, y=series_CAN.values, mode='lines', name='CAN'))
    fig2.update_layout(yaxis=dict(title=yLabel))
    st.plotly_chart(fig2, use_container_width=True)


def plot_ei_v3(series_US, series_CAN, series_MEX, yLabel):
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=series_US.index, y=series_US.values, mode='lines', name='U.S.'))
    fig3.add_trace(go.Scatter(x=series_CAN.index, y=series_CAN.values, mode='lines', name='CAN'))
    fig3.add_trace(go.Scatter(x=series_MEX.index, y=series_MEX.values, mode='lines', name='MEX'))
    fig3.update_layout(yaxis=dict(title=yLabel))
    st.plotly_chart(fig3, use_container_width=True)


# Load the Excel file into a DataFrame
df1 = pd.read_excel("info.xlsx", sheet_name='tickers_list', header=0)  # Your file has a header in the first row
dropdown_tickers = df1['List'].tolist()

APP_NAME = "Fluid Investing"
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="auto",
)
selected_tab = st.sidebar.selectbox("Select Tab", ["Dashboard", "Economic Indicators", "Forecasting"])

if selected_tab == "Dashboard":
    st.title('Simply because, making money should be free.')
    st.markdown(
        """
        What's up? Here is a new **open-source app** called **Fluid Investing** !

        - It was built specifically for Stock Investing across three exchanges : **NYSE, NASDAQ and TSX**. :chart_with_upwards_trend:

        - **Select a tab from the sidebar** to start investing. 👈
        ### Interested in a collab ?
        - You can reach out to me via [Linkedin](https://www.linkedin.com/in/samuel-bérubé-21b1a0127/).
        """
    )
    st.sidebar.title(selected_tab)
    # Select ticker
    selected_ticker = st.sidebar.selectbox("Start smooth, select a valid ticker below:", dropdown_tickers,
                                           placeholder='Selected Ticker')
    selected_ticker = selected_ticker.split(' (', 1)[0].strip()
    # Set start and end point to fetch data
    start_date = st.sidebar.date_input('Start date', datetime(2022, 1, 1))
    end_date = st.sidebar.date_input('End date', datetime.now().date())

    if selected_ticker != '':
        # Fetch the data for specified ticker
        df_ticker = yf.download(selected_ticker.upper(), start=start_date, end=end_date)
        st.header(f'Stock Price : {selected_ticker.upper()} ')
        if st.checkbox('Show raw data'):
            st.subheader('Raw data')
            st.write(df_ticker)

        # Create candlestick chart
        qf = cf.QuantFig(df_ticker, legend='top', name=selected_ticker.upper())
        # Add Relative Strength Indicator (RSI)
        qf.add_rsi(periods=20, color='java')
        # Add Bollinger Bands (BOLL)
        qf.add_bollinger_bands(periods=20, boll_std=2, colors=['magenta', 'grey'], fill=True)
        # Add Volume
        qf.add_volume()
        fig = qf.iplot(asFigure=True, dimensions=(1200, 700), datalegend='ok')
        # Render plot using plotly_chart
        st.plotly_chart(fig)

        t = yf.Ticker(selected_ticker)
        ticker_info = t.info

        # Additional Metrics
        st.write("**Today's Price (Close)**")
        st.write(f"{round(ticker_info['previousClose'], 2)} $")
        st.write("**Today's Volume**")
        st.write(f"{format_int_with_commas(ticker_info['volume'])} shares")
        st.write("**Average Volume (past 10 days)**")
        st.write(f"{format_int_with_commas(ticker_info['averageVolume10days'])} shares")
        st.write("**52wk high**")
        st.write(f"{round(ticker_info['fiftyTwoWeekHigh'], 3)} $")
        st.write("**52wk low**")
        st.write(f"{round(ticker_info['fiftyTwoWeekLow'], 3)} $")
        st.write("**Market Capitalization**")
        st.write(f"{format_int_with_commas(ticker_info['marketCap'])} $")
        st.write("**Dividend Yield**")
        dividend_yield = ticker_info.get('dividendYield',
                                         '')  # Get the dividendYield field or an empty string if it doesn't exist
        if dividend_yield:
            st.write(f"{round(dividend_yield, 2)}")
        else:
            st.write("N/A")
        st.write("**PEG Ratio** (Price per Earning divided by Growth)")
        peg_ratio = ticker_info.get('pegRatio',
                                    '')  # Get the pegRatio field or an empty string if it doesn't exist
        if dividend_yield:
            st.write(f"{peg_ratio}")
        else:
            st.write("N/A")
        st.write("**Last Dividend Date**")
        last_div_date = ticker_info.get('lastDividendDate',
                                        '')  # Get the pegRatio field or an empty string if it doesn't exist
        if dividend_yield:
            st.write(f"{date_format(ticker_info['lastDividendDate'])}")
        else:
            st.write("N/A")
        st.write("**Shares Outstanding**")
        st.write(f"{format_int_with_commas(ticker_info['sharesOutstanding'])} shares")

elif selected_tab == "Economic Indicators":
    # Credentials
    api_key = 'f2a895690fcdf11a9998ef3a21e3620f'
    fred = Fred(api_key=api_key)

    st.sidebar.title(selected_tab)
    st.write("## Economic Indicators")
    st.subheader("Gross Domestic Product in the U.S. (GDP)")
    st.markdown(
        'Gross domestic product (GDP), the featured measure of U.S. output, is the market value of the goods and services produced by labor and property located in the United States. For more information, see the Guide to the National Income and Product Accounts of the United States (NIPA) and the Bureau of Economic Analysis. :chart_with_upwards_trend: from : Federal Reserve Bank of Philadelphia, Leading Index for the United States [USSLIND], retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/USSLIND, January 14, 2024.')
    plot_ei_v1(fred.get_series('GDP'), 'U.S.', 'GDP (billions USD)')
    st.subheader("Gross Domestic Product in Canada (GDP)")
    plot_ei_v1(fred.get_series('NGDPRSAXDCCAQ'), 'CAN', 'GDP (CAD)')
    st.subheader("Inflation")
    plot_ei_v2(fred.get_series('FPCPITOTLZGUSA'), fred.get_series('FPCPITOTLZGCAN'), 'Inflation (%)')
    st.subheader("Consumer Price Index (CPI)")
    plot_ei_v2(fred.get_series('CPIAUCNS'), fred.get_series('CANCPALTT01CTGYM'), 'CPI')
    # st.subheader("Consumer Sentiment")
    # plot_ei_v1(fred.get_series('UMCSENT'), 'U.S.')
    # st.subheader("Employment Growth (This index reflects firms' expectations about the growth of their own employment levels over the next 12 months)")
    # plot_ei_v1(fred.get_series('ATLSBUEGEP'), 'U.S.')
    st.subheader("Unemployment Rates")
    plot_ei_v2(fred.get_series('UNRATE'), fred.get_series('LRHUTTTTCAM156S'), 'Unemployment (%)')
    st.subheader("Housing Prices")
    st.markdown("[Estimated using sales prices and appraisal data :house_buildings:]")
    plot_ei_v1(fred.get_series('USSTHPI'), 'U.S.', 'Housing Prices (USD)')
    st.subheader("Business Inventory")
    plot_ei_v1(fred.get_series('BUSINV'), 'U.S.', 'Business Inventory ($)')
    st.subheader("Real Median Household Income")
    plot_ei_v1(fred.get_series('MEHOINUSA672N'), 'U.S.', 'Real Median Household Income (USD)')
    st.subheader("Lead Economic Indicator (LEI)")
    st.markdown(
        "The leading index for each state predicts the six-month growth rate of the state's coincident index. In addition to the coincident index, the models include other variables that lead the economy: state-level housing permits (1 to 4 units), state initial unemployment insurance claims, delivery times from the Institute for Supply Management (ISM) manufacturing survey, and the interest rate spread between the 10-year Treasury bond and the 3-month Treasury bill.:bar_chart: from : Federal Reserve Bank of Philadelphia, Leading Index for the United States [USSLIND], retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/USSLIND, January 14, 2024.")
    plot_ei_v1(fred.get_series('USSLIND'), 'U.S.', 'LEI')

    st.write("## Interest Rates")
    st.subheader("U.S. Federal Funds Rate")
    st.subheader("Bank of Canada Key Interest Rate")
    st.subheader("Mexico Interbank Rate")
    plot_ei_v3(fred.get_series('DFF'), fred.get_series('IRSTCB01CAM156N'), fred.get_series('IRSTCI01MXM156N'),
               'Rates (%)')

    st.write("## Stock Market Indices")
    st.subheader("Dow Jones Industrial Average (DJIA)")
    plot_ei_v1(fred.get_series('DJIA'), 'DJIA', 'DJIA (unitless)')
    st.subheader("S&P500 Index")
    plot_ei_v1(fred.get_series('SP500'), 'S&P500', 'S&P500 (unitless)')
    st.subheader("NASDAQ Composite Index")
    plot_ei_v1(fred.get_series('NASDAQCOM'), 'NASDAQ Composite Index', 'NASDAQ Composite Index')

elif selected_tab == "Forecasting":
    st.sidebar.title('Work in progress ...')

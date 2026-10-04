import streamlit as st
import requests
import json
from anthropic import Anthropic

st.set_page_config(page_title="AI Equity Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Equity Analyst")
st.markdown("Professional stock analysis powered by Claude AI")

st.sidebar.header("⚙️ Setup")

alpha_vantage_key = st.sidebar.text_input("Alpha Vantage API Key", type="password", help="Get from: https://www.alphavantage.co/")
anthropic_key = st.sidebar.text_input("Anthropic API Key", type="password", help="Get from: https://console.anthropic.com/")

col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker", placeholder="e.g., AAPL, MSFT, TSLA").upper()
with col2:
    analyze_button = st.button("🔍 Analyze", use_container_width=True)

if analyze_button:
    if not ticker:
        st.error("❌ Please enter a stock ticker")
    elif not alpha_vantage_key or not anthropic_key:
        st.error("❌ Please add API keys in the sidebar")
    else:
        with st.spinner(f"📊 Fetching data for {ticker}..."):
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={alpha_vantage_key}"
            response = requests.get(url)
            financial_data = response.json()
        
        if "Error Message" in financial_data:
            st.error(f"❌ Error: {financial_data['Error Message']}")
        else:
            important_metrics = {
                "Company": financial_data.get("Name", "N/A"),
                "Ticker": ticker,
                "Market Cap": financial_data.get("MarketCapitalization", "N/A"),
                "PE Ratio": financial_data.get("PERatio", "N/A"),
                "Profit Margin": financial_data.get("ProfitMargin", "N/A"),
                "Revenue Growth YoY": financial_data.get("QuarterlyRevenueGrowthYoY", "N/A"),
                "Earnings Growth YoY": financial_data.get("QuarterlyEarningsGrowthYoY", "N/A"),
                "Analyst Target Price": financial_data.get("AnalystTargetPrice", "N/A"),
                "52 Week High": financial_data.get("52WeekHigh", "N/A"),
                "52 Week Low": financial_data.get("52WeekLow", "N/A"),
                "Dividend Yield": financial_data.get("DividendYield", "N/A"),
                "Beta": financial_data.get("Beta", "N/A"),
            }
            
            st.subheader(f"💰 Financial Metrics - {ticker}")
            cols = st.columns(4)
            metrics_list = list(important_metrics.items())[2:]
            
            for idx, (key, value) in enumerate(metrics_list):
                with cols[idx % 4]:
                    st.metric(label=key, value=value)
            
            with st.spinner("🤖 Claude is analyzing..."):
                prompt = f"""You are a professional equity analyst. Analyze {ticker} for investment potential.

FINANCIAL DATA:
{json.dumps(important_metrics, indent=2)}

ANALYZE THESE SPECIFIC POINTS:
1. GROWTH: Is revenue/earnings growth > 10% YoY?
2. VALUATION: Is PE ratio < 25?
3. PROFITABILITY: Is profit margin > 20%?
4. MOMENTUM: Are 52-week highs/lows showing strength?
5. RISK: What could go wrong?

FORMAT:
📊 SUMMARY: [1 sentence]
✅ STRENGTHS: [2-3 metrics]
⚠️ CONCERNS: [2-3 metrics]
💡 INVESTMENT THESIS: [Why buy/avoid]
🎯 RECOMMENDATION: [BUY/HOLD/SELL] with confidence

Cite exact numbers."""
                
                client = Anthropic(api_key=anthropic_key)
                message = client.messages.create(
                    model="claude-opus-5-5",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader(f"📋 Investment Analysis - {ticker}")
                for block in message.content:
                    if hasattr(block, 'text'):
                        st.markdown(block.text)
            
            st.success("✅ Analysis complete!")

st.divider()
st.markdown("Built with ❤️ using Claude AI + Streamlit")
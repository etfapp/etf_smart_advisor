import requests, pandas as pd, yfinance as yf, os, logging
AV_KEY = os.getenv("ALPHA_VANTAGE_KEY","")
if AV_KEY:
    from alpha_vantage.timeseries import TimeSeries
    ts = TimeSeries(key=AV_KEY, output_format="pandas")
else:
    ts = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_twse_etf_list():
    url = ("https://www.twse.com.tw/exchangeReport/MI_INDEX"
           "?response=json&reportType=ETF")
    js = requests.get(url, timeout=10).json()
    df = pd.DataFrame(js["data"], columns=js["fields"])
    code_col = "證券代號" if "證券代號" in df.columns else "代號"
    codes = df[code_col].astype(str).tolist()
    return [f"{c}.TW" for c in codes]

def fetch_history(ticker, period="1mo"):
    try:
        df = yf.Ticker(ticker).history(period=period)
        if df.empty:
            logger.warning(f"No data for {ticker}")
            return None
        return df
    except Exception as e:
        logger.warning(f"Yahoo fetch error {ticker}: {e}")
        return None

def fetch_with_fallback(ticker, period="1mo"):
    df = fetch_history(ticker, period)
    if df is not None:
        return df
    if ts:
        symbol = ticker.replace(".TW","")
        try:
            av_df, _ = ts.get_monthly_adjusted(symbol)
            if av_df.empty:
                logger.warning(f"No AV data for {ticker}")
                return None
            return av_df
        except Exception as e:
            logger.warning(f"AlphaVantage error {ticker}: {e}")
    return None

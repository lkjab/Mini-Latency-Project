import pandas as pd
import re
import plotly.express as px

import plotly.io as pio
pio.renderers.default = 'notebook' 

# 1. INPUT DATA (Replace with your actual raw text for all 5)
raw_results = {
    "us-east-1a | use1-az2": """Max rtt: 0.504ms | Min rtt: 0.455ms | Avg rtt: 0.481ms| Raw packets sent: 10 (400B) | Rcvd: 10 (460B) | Lost: 0 (0.00%)""",
    "us-east-1b | use1-az4": """Max rtt: 0.423ms | Min rtt: 0.314ms | Avg rtt: 0.341ms| Raw packets sent: 10 (400B) | Rcvd: 10 (460B) | Lost: 0 (0.00%)""",
    "us-east-1c | use1-az6": """Max rtt: 1.082ms | Min rtt: 0.985ms | Avg rtt: 1.018ms| Raw packets sent: 10 (400B) | Rcvd: 10 (460B) | Lost: 0 (0.00%)""",
    "us-east-1d | use1-az1": """Max rtt: 0.766ms | Min rtt: 0.645ms | Avg rtt: 0.690ms| Raw packets sent: 10 (400B) | Rcvd: 10 (460B) | Lost: 0 (0.00%)""",
    "us-east-1f | use1-az5": """Max rtt: 0.623ms | Min rtt: 0.504ms | Avg rtt: 0.542ms| Raw packets sent: 10 (400B) | Rcvd: 10 (460B) | Lost: 0 (0.00%)"""
}

# 2. PARSING LOGIC
def parse_metrics(az, text):
    # Regex to find numbers followed by 'ms'
    find_ms = lambda label: float(re.search(rf"{label} rtt: ([\d.]+)ms", text).group(1))
    
    return {
        "AZ": az,
        "Min_ms": find_ms("Min"),
        "Max_ms": find_ms("Max"),
        "Avg_ms": find_ms("Avg"),
        "Jitter_ms": round(find_ms("Max") - find_ms("Min"), 3)
    }

# 3. CREATE DATAFRAME
df = pd.DataFrame([parse_metrics(az, text) for az, text in raw_results.items()])

# 4. RANKING FOR HFT
# We want lowest Avg AND lowest Jitter
df['Score'] = df['Avg_ms'] + df['Jitter_ms'] 
df = df.sort_values('Score')

print("--- Latency Ranking (Top is best) ---")
print(df[['AZ', 'Avg_ms', 'Jitter_ms', 'Score']])

# Melt the data for a better Plotly range chart
fig = px.bar(df, x="AZ", y="Max_ms", 
             title="Latency Volatility (Min vs Max RTT)",
             labels={"Max_ms": "Latency (ms)"},
             color="Jitter_ms",
             color_continuous_scale="RdYlGn_r")

# Add the 'Min' as a baseline marker or overlay
fig.add_scatter(x=df["AZ"], y=df["Min_ms"], mode="markers", name="Min RTT", marker=dict(color="black", size=10))

fig.show()

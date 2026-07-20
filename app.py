import streamlit as st

st.set_page_config(
    page_title="Game Day NPV Calculator",
    page_icon="⚾",
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(36, 123, 255, 0.18), transparent 30%),
                radial-gradient(circle at 90% 15%, rgba(250, 185, 30, 0.14), transparent 28%),
                linear-gradient(145deg, #080b15, #0b1020);
            color: white;
        }

        .block-container {
            max-width: 1050px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, p, label {
            color: #f7f8fb !important;
        }

        .subtitle {
            color: #aeb7cb;
            font-size: 1.05rem;
            line-height: 1.6;
            margin-bottom: 2rem;
        }

        .result-card {
            border-radius: 22px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.28);
            min-height: 190px;
        }

        .result-label {
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.82;
        }

        .result-value {
            font-size: 3rem;
            font-weight: 850;
            line-height: 1;
            margin-top: 16px;
        }

        .result-note {
            font-size: 0.92rem;
            margin-top: 14px;
            opacity: 0.82;
        }

        .assumption-box {
            background: rgba(20, 29, 52, 0.82);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 18px;
            padding: 18px 20px;
            margin-top: 2rem;
        }

        div[data-testid="stSlider"] > div {
            padding-top: 0.25rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def heatmap_color(value: float, minimum: float = -100.0, maximum: float = 100.0) -> str:
    """
    Map a numeric value to a red-yellow-green heatmap color.
    """
    value = max(minimum, min(maximum, value))
    normalized = (value - minimum) / (maximum - minimum)

    if normalized < 0.5:
        # Red -> Yellow
        ratio = normalized / 0.5
        red = 220
        green = int(70 + (185 * ratio))
        blue = 70
    else:
        # Yellow -> Green
        ratio = (normalized - 0.5) / 0.5
        red = int(220 - (160 * ratio))
        green = int(255 - (45 * ratio))
        blue = int(70 + (25 * ratio))

    return f"rgb({red}, {green}, {blue})"


def slider_color(value: int) -> str:
    """
    Map a 0-100 slider value to a red-yellow-green color.
    """
    return heatmap_color(value, minimum=0, maximum=100)


# -----------------------------
# Header
# -----------------------------
st.title("Game Day NPV Calculator")

st.markdown(
    """
    <div class="subtitle">
        Compare the subjective net present value of watching the Yankees from
        behind home plate versus playing soccer with friends.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Inputs
# -----------------------------
rain_chance = st.slider(
    "Chance of rain",
    min_value=0,
    max_value=100,
    value=35,
    step=1,
    format="%d%%",
)

yankees_fun = st.slider(
    "How fun would the Yankees game be?",
    min_value=0,
    max_value=100,
    value=85,
    step=1,
)

soccer_fun = st.slider(
    "How fun would playing soccer with friends be?",
    min_value=0,
    max_value=100,
    value=75,
    step=1,
)

# -----------------------------
# NPV model
# -----------------------------
# You can change these assumptions to tune the calculator.
YANKEES_TICKET_VALUE = 180
YANKEES_OTHER_COSTS = 55
SOCCER_COST = 10

rain_probability = rain_chance / 100
yankees_fun_score = yankees_fun / 100
soccer_fun_score = soccer_fun / 100

# Yankees:
# - Higher fun increases value.
# - Rain reduces expected enjoyment, but less severely because the user is seated.
yankees_npv = (
    YANKEES_TICKET_VALUE * yankees_fun_score
    - YANKEES_OTHER_COSTS
    - 65 * rain_probability
)

# Soccer:
# - Higher fun increases value.
# - Rain has a larger negative effect because the activity is outdoors.
soccer_npv = (
    125 * soccer_fun_score
    - SOCCER_COST
    - 105 * rain_probability
)

yankees_color = heatmap_color(yankees_npv)
soccer_color = heatmap_color(soccer_npv)

# -----------------------------
# Results
# -----------------------------
left, right = st.columns(2)

with left:
    st.markdown(
        f"""
        <div class="result-card" style="background: {yankees_color}; color: #111;">
            <div class="result-label">Yankees game NPV</div>
            <div class="result-value">${yankees_npv:,.0f}</div>
            <div class="result-note">
                Includes ticket value, other costs, expected fun, and rain risk.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="result-card" style="background: {soccer_color}; color: #111;">
            <div class="result-label">Soccer NPV</div>
            <div class="result-value">${soccer_npv:,.0f}</div>
            <div class="result-note">
                Includes expected fun, a small activity cost, and stronger rain sensitivity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Recommendation
# -----------------------------
difference = yankees_npv - soccer_npv

if abs(difference) < 5:
    recommendation = "It is basically a tie."
elif difference > 0:
    recommendation = f"The Yankees game leads by about ${difference:,.0f}."
else:
    recommendation = f"Playing soccer leads by about ${abs(difference):,.0f}."

st.subheader("Recommendation")
st.write(recommendation)

# -----------------------------
# Slider heatmap legend
# -----------------------------
st.markdown(
    f"""
    <div class="assumption-box">
        <strong>Current heatmap readings</strong><br><br>
        <span style="color:{slider_color(rain_chance)};">●</span>
        Rain chance: {rain_chance}%<br>
        <span style="color:{slider_color(yankees_fun)};">●</span>
        Yankees fun: {yankees_fun}/100<br>
        <span style="color:{slider_color(soccer_fun)};">●</span>
        Soccer fun: {soccer_fun}/100
        <br><br>
        Red indicates low value, yellow indicates neutral value, and green indicates high value.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("View the calculation assumptions"):
    st.write(
        {
            "Yankees ticket value": YANKEES_TICKET_VALUE,
            "Yankees other costs": YANKEES_OTHER_COSTS,
            "Soccer cost": SOCCER_COST,
            "Yankees rain penalty at 100% rain": 65,
            "Soccer rain penalty at 100% rain": 105,
        }
    )

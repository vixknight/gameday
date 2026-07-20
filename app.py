import streamlit as st

st.set_page_config(
    page_title="Game Day NPV Calculator",
    page_icon="⚽",
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
                linear-gradient(145deg, #090433, #112040);
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

        .slider-heading {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 1.35rem 0 0.2rem;
            font-size: 1.02rem;
            font-weight: 750;
            color: #f7f8fb;
        }

        .slider-icon {
            font-size: 1.5rem;
            line-height: 1;
        }

        .slider-aura {
            position: relative;
            border-radius: 24px;
            padding: 0.25rem 1rem 0.1rem;
            margin-bottom: 0.6rem;
            border: 1px solid rgba(255, 255, 255, 0.07);
            overflow: visible;
        }

        .slider-aura::before {
            content: "";
            position: absolute;
            inset: -8px;
            z-index: -1;
            border-radius: 30px;
            background: var(--aura-gradient);
            filter: blur(var(--aura-blur));
            opacity: var(--aura-opacity);
            transform: scale(var(--aura-scale));
            transition:
                transform 180ms ease,
                filter 180ms ease,
                opacity 180ms ease;
        }

        .result-card {
            border-radius: 22px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.28);
            min-height: 215px;
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
            line-height: 1.5;
            margin-top: 14px;
            opacity: 0.84;
        }

        .match-card {
            margin: 1.25rem 0 1.75rem;
            padding: 18px 20px;
            border-radius: 18px;
            background:
                linear-gradient(120deg, rgba(65, 180, 105, 0.19), rgba(35, 123, 255, 0.13));
            border: 1px solid rgba(130, 255, 170, 0.20);
            color: #eaf8ee;
            line-height: 1.55;
        }

        .opportunity-card {
            margin: 0 0 1.75rem;
            padding: 18px 20px;
            border-radius: 18px;
            background:
                linear-gradient(120deg, rgba(250, 185, 30, 0.18), rgba(36, 123, 255, 0.12));
            border: 1px solid rgba(255, 214, 93, 0.21);
            color: #fff7d1;
            line-height: 1.55;
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
            padding-bottom: 0.9rem;
        }

        div[data-testid="stSlider"] [role="slider"] {
            box-shadow: 0 0 18px rgba(255, 255, 255, 0.20);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def heatmap_color(value: float, minimum: float = -100.0, maximum: float = 150.0) -> str:
    """Map a numeric value to a red-yellow-green heatmap color."""
    value = max(minimum, min(maximum, value))
    normalized = (value - minimum) / (maximum - minimum)

    if normalized < 0.5:
        ratio = normalized / 0.5
        red = 220
        green = int(70 + (185 * ratio))
        blue = 70
    else:
        ratio = (normalized - 0.5) / 0.5
        red = int(220 - (160 * ratio))
        green = int(255 - (45 * ratio))
        blue = int(70 + (25 * ratio))

    return f"rgb({red}, {green}, {blue})"


def slider_color(value: int) -> str:
    return heatmap_color(value, minimum=0, maximum=100)


def aura_style(value: int, start: str, end: str) -> str:
    """
    Build CSS variables for a glow that gets larger and stronger
    as the slider value approaches 100.
    """
    scale = 0.92 + (value / 100) * 0.22
    blur = 10 + int((value / 100) * 30)
    opacity = 0.16 + (value / 100) * 0.42

    return (
        f"--aura-scale:{scale:.2f};"
        f"--aura-blur:{blur}px;"
        f"--aura-opacity:{opacity:.2f};"
        f"--aura-gradient:linear-gradient(90deg, {start}, {end});"
    )


def slider_section(title: str, icon: str, key: str, value: int, start: str, end: str, percent: bool = False) -> int:
    st.markdown(
        f"""
        <div class="slider-heading">
            <span class="slider-icon">{icon}</span>
            <span>{title}</span>
        </div>
        <div class="slider-aura" style="{aura_style(value, start, end)}">
        """,
        unsafe_allow_html=True,
    )

    selected = st.slider(
        title,
        min_value=0,
        max_value=100,
        value=value,
        step=1,
        format="%d%%" if percent else "%d",
        key=key,
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)
    return selected


# -----------------------------
# Header
# -----------------------------
st.title("Game Day NPV Calculator")

st.markdown(
    """
    <div class="subtitle">
        Two elite opportunities enter.
        One involves free seats behind home plate.
        The other involves friendship, glory, and a deeply serious amateur rivalry.
    </div>
    """,
    unsafe_allow_html=True,
)

# st.markdown(
#     """
#     <div class="opportunity-card">
#         <strong>⚾ Yankees opportunity:</strong>
#         the tickets were <strong>FREE</strong>, which transforms this from “nice baseball outing”
#         into “financially irresponsible not to at least consider it.” Behind home plate is a
#         premium experience with essentially no ticket-cost downside.
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown(
#     """
#     <div class="match-card">
#         <strong>⚽ Group Stage Derby:</strong>
#         GIPP — <em>Good Intent, Poor Product</em> — takes on rival team
#         <strong>99c Fresh</strong> in the Group Stage league. It is the
#         <strong>Group Stage Derby</strong>: low transfer budgets, high emotional stakes,
#         and at least one player insisting the final pass was “definitely on.”
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# -----------------------------
# Inputs
# -----------------------------
rain_chance = slider_section(
    "Chance of rain",
    "",
    "rain_chance",
    35,
    "rgba(90, 120, 255, 0.55)",
    "rgba(50, 210, 255, 0.55)",
    percent=True,
)

yankees_fun = slider_section(
    "How fun would the Yankees game be?",
    "",
    "yankees_fun",
    85,
    "rgba(35, 123, 255, 0.55)",
    "rgba(250, 185, 30, 0.60)",
)

soccer_fun = slider_section(
    "How fun would playing for GIPP be?",
    "",
    "soccer_fun",
    82,
    "rgba(50, 210, 105, 0.55)",
    "rgba(230, 255, 90, 0.58)",
)

# -----------------------------
# NPV model
# -----------------------------
# Yankees tickets are free, so there is no ticket cost.
YANKEES_TICKET_COST = 0
YANKEES_SEAT_OPPORTUNITY_VALUE = 225
YANKEES_OTHER_COSTS = 40

# Soccer gets added value for friendship, rivalry, and the prestige
# of representing GIPP in the Group Stage Derby.
SOCCER_COST = 10
SOCCER_TEAM_BONUS = 30
SOCCER_DERBY_BONUS = 22

rain_probability = rain_chance / 100
yankees_fun_score = yankees_fun / 100
soccer_fun_score = soccer_fun / 100

yankees_npv = (
    YANKEES_SEAT_OPPORTUNITY_VALUE * yankees_fun_score
    - YANKEES_TICKET_COST
    - YANKEES_OTHER_COSTS
    - 55 * rain_probability
)

soccer_npv = (
    135 * soccer_fun_score
    + SOCCER_TEAM_BONUS
    + SOCCER_DERBY_BONUS
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
                Free tickets behind home plate create a major opportunity-value boost.
                This includes expected fun, incidental costs, and rain risk.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="result-card" style="background: {soccer_color}; color: #111;">
            <div class="result-label">GIPP soccer NPV</div>
            <div class="result-value">${soccer_npv:,.0f}</div>
            <div class="result-note">
                Includes expected fun, friendship value, team loyalty, and the unmatched
                prestige of defeating 99c Fresh in the Group Stage Derby.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Recommendation
# -----------------------------
difference = yankees_npv - soccer_npv

st.subheader("Recommendation")

if abs(difference) < 5:
    st.write(
        "It is effectively a tie. This may require a final qualitative adjustment for "
        "derby-day loyalty versus the rarity of free behind-home-plate seats."
    )
elif difference > 0:
    st.write(
        f"The Yankees game leads by about ${difference:,.0f}. Free premium tickets are doing "
        "exactly what free premium tickets are supposed to do: create an enormous opportunity."
    )
else:
    st.write(
        f"Playing for GIPP leads by about ${abs(difference):,.0f}. Apparently friendship, "
        "rivalry, and the chance to humble 99c Fresh are highly bankable assets."
    )

st.markdown(
    f"""
    <div class="assumption-box">
        <strong>Current heatmap readings</strong><br><br>
        <span style="color:{slider_color(rain_chance)};">●</span>
        Rain chance: {rain_chance}%<br>
        <span style="color:{slider_color(yankees_fun)};">●</span>
        Yankees fun: {yankees_fun}/100<br>
        <span style="color:{slider_color(soccer_fun)};">●</span>
        GIPP soccer fun: {soccer_fun}/100
        <br><br>
        Red indicates low value, yellow indicates neutral value, and green indicates high value.
        Each slider's aura becomes larger and brighter as its value increases.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("View the calculation assumptions"):
    st.write(
        {
            "Yankees ticket cost": YANKEES_TICKET_COST,
            "Behind-home-plate opportunity value": YANKEES_SEAT_OPPORTUNITY_VALUE,
            "Yankees incidental costs": YANKEES_OTHER_COSTS,
            "Soccer cost": SOCCER_COST,
            "GIPP team bonus": SOCCER_TEAM_BONUS,
            "Group Stage Derby bonus": SOCCER_DERBY_BONUS,
            "Yankees rain penalty at 100% rain": 55,
            "Soccer rain penalty at 100% rain": 105,
            "Emojis": "☂ ⚡︎ ⚽︎ ᯓ ⚾︎"
        }
    )

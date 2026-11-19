
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from fuzzy_engine import (
    evaluate_player_fuzzy,
    calculate_position_fit,
    calculate_budget_fit
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Football Scout AI",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# CUSTOM DASHBOARD STYLE
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0B1511;
    color: #E8F2EB;
}

[data-testid="stSidebar"] {
    background-color: #14241B;
}

.metric-card {
    background-color: #193326;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #294A35;
}

.section-title {
    color: #B5E4C1;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD DATASET
# ==========================================

@st.cache_data
def load_data():

    data = pd.read_csv("cleaned_players.csv")

    return data


df = load_data()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚽ FOOTBALL SCOUT AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Team Overview",
        "Player Scouting",
        "Player Comparison"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Intelligent Player Selection System"
)

st.sidebar.caption(
    "Powered by Mamdani Fuzzy Logic"
)


# ==========================================
# HEADER
# ==========================================

st.title("⚽ Football Scouting Dashboard")

st.markdown(
    "### Intelligent Player Selection & Recommendation System"
)

st.caption(
    "Analyze squads, discover weaknesses and identify suitable transfer targets."
)


# ==========================================
# POSITION GROUPS
# ==========================================

position_mapping = {

    "Goalkeeper": ["GK"],

    "Defender": [
        "CB", "LB", "RB", "LWB", "RWB"
    ],

    "Midfielder": [
        "CDM", "CM", "CAM", "LM", "RM"
    ],

    "Forward": [
        "ST", "CF", "LW", "RW"
    ]
}


# ==========================================
# TEAM STRENGTH
# ==========================================

def calculate_team_strength(team_name):

    team_data = df[df["club"] == team_name]

    strength = (
        team_data.groupby("position_group")["overall"]
        .mean()
        .round(2)
    )

    return strength


# ==========================================
# TEAM OVERVIEW PAGE
# ==========================================

if page == "Team Overview":

    st.header("Team Overview")

    clubs = sorted(df["club"].dropna().unique())

    selected_team = st.selectbox(
        "Select Football Club",
        clubs
    )

    team_data = df[df["club"] == selected_team].copy()

    # Statistics

    squad_size = len(team_data)

    avg_overall = round(team_data["overall"].mean(), 2)

    avg_potential = round(team_data["potential"].mean(), 2)

    avg_age = round(team_data["age"].mean(), 2)

    strength = calculate_team_strength(selected_team)

    weakest_position = strength.idxmin()

    # KPI Cards

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Squad Size", squad_size)

    col2.metric("Average Overall", avg_overall)

    col3.metric("Average Potential", avg_potential)

    col4.metric("Average Age", avg_age)

    st.markdown("---")

    # Position Strength

    st.subheader("Squad Strength by Position")

    strength_df = strength.reset_index()

    strength_df.columns = [
        "Position",
        "Average Overall"
    ]

    fig = px.bar(
        strength_df,
        x="Position",
        y="Average Overall",
        color="Position",
        text="Average Overall",
        template="plotly_dark"
    )

    fig.update_layout(
        plot_bgcolor="#0B1511",
        paper_bgcolor="#0B1511",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Weakness

    st.subheader("Squad Weakness Analysis")

    st.warning(
        f"Weakest Position Group: {weakest_position}"
    )

    # Player Table

    st.subheader("Squad Players")

    display_columns = [
        "short_name",
        "main_position",
        "overall",
        "potential",
        "age",
        "value_eur"
    ]

    squad_display = team_data.sort_values(
        "overall",
        ascending=False
    )

    st.dataframe(
        squad_display[display_columns],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# PLAYER SCOUTING PAGE - PLACEHOLDER
# ==========================================

elif page == "Player Scouting":

    st.header("Player Scouting")

    st.info(
        "Fuzzy-based player recommendations will be connected in the next step."
    )


# ==========================================
# PLAYER COMPARISON PAGE - PLACEHOLDER
# ==========================================

elif page == "Player Comparison":

    st.header("Player Comparison")

    st.info(
        "Interactive player comparison will be added in the next step."
    )


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
        "value_eur",
        "pace",
        "shooting",
        "passing",
        "dribbling",
        "defending",
        "physic"
    ]

    squad_display = team_data.sort_values(
        "overall",
        ascending=False
    )

    available_columns = [
        col for col in display_columns
        if col in squad_display.columns
    ]

    column_names = {
        "short_name": "Player",
        "main_position": "Position",
        "overall": "Overall",
        "potential": "Potential",
        "age": "Age",
        "value_eur": "Value (€)",
        "pace": "Pace",
        "shooting": "Shooting",
        "passing": "Passing",
        "dribbling": "Dribbling",
        "defending": "Defending",
        "physic": "Physical"
    }

    squad_table = squad_display[available_columns].rename(
        columns=column_names
    )

    st.dataframe(
        squad_table,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# PLAYER SCOUTING PAGE - PLACEHOLDER
# ==========================================


# ==========================================
# PLAYER SCOUTING PAGE
# ==========================================

elif page == "Player Scouting":

    st.header("🔎 Player Scouting")
    st.markdown(
        "Find suitable transfer targets using the Mamdani Fuzzy Logic system."
    )

    st.markdown("---")

    # --------------------------------------
    # SCOUTING INPUTS
    # --------------------------------------

    col1, col2, col3 = st.columns(3)

    clubs = sorted(df["club"].dropna().unique())

    with col1:
        target_club = st.selectbox(
            "Select Club",
            clubs,
            key="scouting_club"
        )

    with col2:
        selected_position = st.selectbox(
            "Required Position",
            ["Forward", "Midfielder", "Defender"],
            key="scouting_position"
        )

    with col3:
        budget = st.number_input(
            "Transfer Budget (€)",
            min_value=100000.0,
            max_value=500000000.0,
            value=50000000.0,
            step=1000000.0,
            format="%.0f",
            key="scouting_budget"
        )

    col4, col5 = st.columns(2)

    with col4:
        min_overall = st.slider(
            "Minimum Overall Rating",
            min_value=40,
            max_value=95,
            value=70,
            key="scouting_overall"
        )

    with col5:
        min_potential = st.slider(
            "Minimum Potential",
            min_value=40,
            max_value=99,
            value=75,
            key="scouting_potential"
        )

    st.markdown("---")

    # --------------------------------------
    # FIND CANDIDATE PLAYERS
    # --------------------------------------

    if st.button("🔍 Find Recommended Players", use_container_width=True):

        required_positions = position_mapping[selected_position]

        candidates = df[
            (df["main_position"].isin(required_positions)) &
            (df["overall"] >= min_overall) &
            (df["potential"] >= min_potential) &
            (df["value_eur"] <= budget) &
            (df["club"] != target_club)
        ].copy()

        if candidates.empty:

            st.warning(
                "No players found for these requirements. "
                "Try increasing the budget or lowering the rating filters."
            )

        else:

            # --------------------------------------
            # FUZZY SCORING
            # --------------------------------------

            scouting_results = []

            for _, player in candidates.iterrows():

                position_score = calculate_position_fit(
                    player,
                    selected_position
                )

                budget_score = calculate_budget_fit(
                    player["value_eur"],
                    budget
                )

                fuzzy_score = evaluate_player_fuzzy(
                    player["overall"],
                    player["potential"],
                    position_score,
                    budget_score
                )

                scouting_results.append({

                    "Player": player["short_name"],
                    "Club": player["club"],
                    "Position": player["main_position"],
                    "Overall": player["overall"],
                    "Potential": player["potential"],
                    "Age": player["age"],
                    "Value (€)": player["value_eur"],
                    "Position Fit": position_score,
                    "Budget Fit": budget_score,
                    "Fuzzy Suitability": fuzzy_score

                })

            # --------------------------------------
            # SORT RECOMMENDATIONS
            # --------------------------------------

            recommendations = pd.DataFrame(scouting_results)

            recommendations = recommendations.sort_values(
                "Fuzzy Suitability",
                ascending=False
            ).reset_index(drop=True)

            # Store results across Streamlit reruns
            st.session_state["scouting_results"] = recommendations
            st.session_state["scouting_target"] = target_club
            st.session_state["scouting_position"] = selected_position

    # --------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------

    if "scouting_results" in st.session_state:

        recommendations = st.session_state["scouting_results"]

        st.subheader("🏆 Recommended Players")

        # KPI metrics

        best_player = recommendations.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Players Found",
            len(recommendations)
        )

        col2.metric(
            "Best Recommendation",
            best_player["Player"]
        )

        col3.metric(
            "Best Fuzzy Score",
            f'{best_player["Fuzzy Suitability"]:.2f}/100'
        )

        st.markdown("---")

        # --------------------------------------
        # TOP 10 PLAYERS
        # --------------------------------------

        st.subheader("Top 10 Transfer Targets")

        top_10 = recommendations.head(10).copy()

        st.dataframe(
            top_10,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------
        # FUZZY SCORE CHART
        # --------------------------------------

        st.subheader("Player Suitability Comparison")

        chart_data = top_10.sort_values(
            "Fuzzy Suitability",
            ascending=True
        )

        fig = px.bar(
            chart_data,
            x="Fuzzy Suitability",
            y="Player",
            orientation="h",
            color="Fuzzy Suitability",
            text="Fuzzy Suitability",
            template="plotly_dark",
            title="Top 10 Players by Mamdani Fuzzy Score"
        )

        fig.update_layout(
            plot_bgcolor="#0B1511",
            paper_bgcolor="#0B1511",
            xaxis_title="Suitability Score",
            xaxis_range=[0, 100],
            yaxis_title="Player",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # --------------------------------------
        # DOWNLOAD RECOMMENDATIONS
        # --------------------------------------

        st.subheader("Export Recommendations")

        csv_data = recommendations.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download All Recommendations (CSV)",
            data=csv_data,
            file_name="football_scout_recommendations.csv",
            mime="text/csv"
        )


# ==========================================
# PLAYER COMPARISON PAGE - PLACEHOLDER
# ==========================================

elif page == "Player Comparison":

    st.header("Player Comparison")

    st.info(
        "Interactive player comparison will be added in the next step."
    )

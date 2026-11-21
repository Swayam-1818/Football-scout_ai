
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

def analyze_team_weakness(team_name):

    team_data = df[df["club"] == team_name].copy()

    position_strength = (
        team_data.groupby("position_group")["overall"]
        .mean()
        .round(2)
    )

    position_strength = position_strength.reindex(
        ["Defender", "Midfielder", "Forward"]
    ).dropna()

    if position_strength.empty:
        return position_strength, None

    weakest_position = position_strength.idxmin()

    return position_strength, weakest_position




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
        # TEAM WEAKNESS ANALYSIS
    position_strength, weakest_position = analyze_team_weakness(selected_team)

    st.subheader("🔍 Team Weakness Analysis")

    if weakest_position is not None:

        weakest_rating = position_strength[weakest_position]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Weakest Position",
            weakest_position
        )

        col2.metric(
            "Average Rating",
            weakest_rating
        )

        col3.metric(
            "Recommended Scouting",
            weakest_position
        )

        st.warning(
            f"⚠️ {selected_team} should consider strengthening "
            f"its {weakest_position} position."
        )

        st.markdown("### Position Strength")

        strength_chart = px.bar(
            position_strength.reset_index(),
            x="position_group",
            y="overall",
            color="overall",
            text="overall",
            title="Average Rating by Position"
        )

        strength_chart.update_layout(
            template="plotly_dark",
            yaxis_title="Average Overall Rating",
            xaxis_title="Position",
            yaxis_range=[0, 100]
        )

        st.plotly_chart(
            strength_chart,
            use_container_width=True
        )

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

    
    # Analyze selected club's weakest position
    scouting_strength, scouting_weakest = analyze_team_weakness(target_club)

    scouting_positions = ["Forward", "Midfielder", "Defender"]

    if scouting_weakest in scouting_positions:
        scouting_positions.remove(scouting_weakest)
        scouting_positions.insert(0, scouting_weakest)

    with col2:
        selected_position = st.selectbox(
            "Required Position",
            scouting_positions,
            index=0,
            key="scouting_position_auto"
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

    st.header("⚖️ Player Comparison")
    st.markdown("Compare two football players based on performance attributes.")

    st.markdown("---")

    # PLAYER SELECTION
    player_options = df.sort_values("short_name")[
        ["short_name", "club", "main_position"]
    ].drop_duplicates()

    player_options["label"] = (
        player_options["short_name"]
        + " | "
        + player_options["club"]
        + " | "
        + player_options["main_position"]
    )

    player_labels = player_options["label"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        player1_label = st.selectbox(
            "Select Player 1",
            player_labels,
            key="comparison_player1"
        )

    with col2:
        player2_label = st.selectbox(
            "Select Player 2",
            player_labels,
            index=1 if len(player_labels) > 1 else 0,
            key="comparison_player2"
        )

    player1 = player_options[
        player_options["label"] == player1_label
    ].iloc[0]

    player2 = player_options[
        player_options["label"] == player2_label
    ].iloc[0]

    player1_data = df[
        (df["short_name"] == player1["short_name"]) &
        (df["club"] == player1["club"]) &
        (df["main_position"] == player1["main_position"])
    ].iloc[0]

    player2_data = df[
        (df["short_name"] == player2["short_name"]) &
        (df["club"] == player2["club"]) &
        (df["main_position"] == player2["main_position"])
    ].iloc[0]

    st.markdown("---")

    # PLAYER PROFILE COMPARISON
    st.subheader("📊 Player Profile")

    comparison_metrics = {
        "Overall": "overall",
        "Potential": "potential",
        "Age": "age",
        "Market Value (€)": "value_eur"
    }

    for label, column in comparison_metrics.items():

        col1, col2, col3 = st.columns([2, 1, 1])

        col1.write(label)
        col2.metric(player1["short_name"], player1_data[column])
        col3.metric(player2["short_name"], player2_data[column])

    st.markdown("---")

    # PERFORMANCE ATTRIBUTES
    st.subheader("⚽ Performance Attributes")

    attributes = [
        "pace",
        "shooting",
        "passing",
        "dribbling",
        "defending",
        "physic"
    ]

    attribute_labels = [
        "Pace",
        "Shooting",
        "Passing",
        "Dribbling",
        "Defending",
        "Physical"
    ]

    comparison_data = pd.DataFrame({
        "Attribute": attribute_labels * 2,
        "Rating": (
            [player1_data[a] for a in attributes]
            + [player2_data[a] for a in attributes]
        ),
        "Player": (
            [player1["short_name"]] * len(attributes)
            + [player2["short_name"]] * len(attributes)
        )
    })

    # RADAR CHART
    radar_chart = px.line_polar(
        comparison_data,
        r="Rating",
        theta="Attribute",
        color="Player",
        line_close=True,
        markers=True,
        title="Player Attribute Comparison"
    )

    radar_chart.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(radar_chart, use_container_width=True)

    # ATTRIBUTE TABLE
    st.subheader("📋 Attribute Comparison")

    attribute_table = pd.DataFrame({
        "Attribute": attribute_labels,
        player1["short_name"]: [player1_data[a] for a in attributes],
        player2["short_name"]: [player2_data[a] for a in attributes]
    })

    st.dataframe(
        attribute_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # COMPARISON SUMMARY
    st.subheader("🏆 Comparison Summary")

    player1_score = player1_data["overall"]
    player2_score = player2_data["overall"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Player 1 Overall",
        player1_score
    )

    col2.metric(
        "Player 2 Overall",
        player2_score
    )

    if player1_score > player2_score:
        col3.success(
            f"⭐ {player1['short_name']} has the higher overall rating."
        )

    elif player2_score > player1_score:
        col3.success(
            f"⭐ {player2['short_name']} has the higher overall rating."
        )

    else:
        col3.info("Both players have the same overall rating.")


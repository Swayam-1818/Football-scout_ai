
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# -----------------------------
# 1. Define Input Variables
# -----------------------------

overall = ctrl.Antecedent(np.arange(0, 101, 1), 'overall')
potential = ctrl.Antecedent(np.arange(0, 101, 1), 'potential')
position_fit = ctrl.Antecedent(np.arange(0, 101, 1), 'position_fit')
budget_fit = ctrl.Antecedent(np.arange(0, 101, 1), 'budget_fit')

# -----------------------------
# 2. Define Output Variable
# -----------------------------

suitability = ctrl.Consequent(
    np.arange(0, 101, 1),
    'suitability'
)

# -----------------------------
# 3. Membership Functions
# -----------------------------

# Overall Rating
overall['low'] = fuzz.trapmf(overall.universe, [0, 0, 40, 60])
overall['medium'] = fuzz.trimf(overall.universe, [40, 65, 85])
overall['high'] = fuzz.trapmf(overall.universe, [70, 85, 100, 100])

# Potential
potential['low'] = fuzz.trapmf(potential.universe, [0, 0, 40, 60])
potential['medium'] = fuzz.trimf(potential.universe, [40, 65, 85])
potential['high'] = fuzz.trapmf(potential.universe, [70, 85, 100, 100])

# Position Fit
position_fit['poor'] = fuzz.trapmf(position_fit.universe, [0, 0, 25, 45])
position_fit['average'] = fuzz.trimf(position_fit.universe, [30, 55, 80])
position_fit['good'] = fuzz.trapmf(position_fit.universe, [65, 85, 100, 100])

# Budget Fit
budget_fit['poor'] = fuzz.trapmf(budget_fit.universe, [0, 0, 25, 45])
budget_fit['average'] = fuzz.trimf(budget_fit.universe, [30, 55, 80])
budget_fit['good'] = fuzz.trapmf(budget_fit.universe, [65, 85, 100, 100])

# Output Suitability
suitability['poor'] = fuzz.trapmf(suitability.universe, [0, 0, 10, 25])
suitability['low'] = fuzz.trimf(suitability.universe, [15, 30, 45])
suitability['moderate'] = fuzz.trimf(suitability.universe, [35, 50, 65])
suitability['good'] = fuzz.trimf(suitability.universe, [55, 72, 88])
suitability['excellent'] = fuzz.trapmf(suitability.universe, [75, 90, 100, 100])

# -----------------------------
# 4. Mamdani Fuzzy Rules
# -----------------------------

rules = [

    ctrl.Rule(
        overall['high'] & potential['high'] &
        position_fit['good'] & budget_fit['good'],
        suitability['excellent']
    ),

    ctrl.Rule(
        overall['high'] & potential['high'] &
        position_fit['good'] & budget_fit['average'],
        suitability['excellent']
    ),

    ctrl.Rule(
        overall['high'] & potential['high'] &
        position_fit['average'] & budget_fit['good'],
        suitability['good']
    ),

    ctrl.Rule(
        overall['high'] & potential['medium'] &
        position_fit['good'] & budget_fit['good'],
        suitability['good']
    ),

    ctrl.Rule(
        overall['high'] & position_fit['good'] &
        budget_fit['good'],
        suitability['good']
    ),

    ctrl.Rule(
        overall['medium'] & potential['high'] &
        position_fit['good'] & budget_fit['good'],
        suitability['good']
    ),

    ctrl.Rule(
        overall['medium'] & potential['medium'] &
        position_fit['good'] & budget_fit['good'],
        suitability['moderate']
    ),

    ctrl.Rule(
        overall['medium'] & position_fit['average'] &
        budget_fit['average'],
        suitability['moderate']
    ),

    ctrl.Rule(
        overall['high'] & position_fit['poor'],
        suitability['moderate']
    ),

    ctrl.Rule(
        overall['medium'] & position_fit['poor'],
        suitability['low']
    ),

    ctrl.Rule(
        overall['low'] & potential['low'],
        suitability['poor']
    ),

    ctrl.Rule(
        overall['low'] & position_fit['poor'] &
        budget_fit['poor'],
        suitability['poor']
    ),

    ctrl.Rule(
        potential['high'] & position_fit['good'] &
        budget_fit['average'],
        suitability['good']
    ),

    ctrl.Rule(
        potential['medium'] & position_fit['average'],
        suitability['moderate']
    ),

    ctrl.Rule(
        budget_fit['poor'] & position_fit['good'],
        suitability['moderate']
    ),

    ctrl.Rule(
        overall['low'] & potential['high'] &
        position_fit['good'],
        suitability['moderate']
    )
]

# -----------------------------
# 5. Create Fuzzy Control System
# -----------------------------

player_control_system = ctrl.ControlSystem(rules)

# -----------------------------
# 6. Fuzzy Evaluation Function
# -----------------------------

def evaluate_player_fuzzy(
    overall_score,
    potential_score,
    position_score,
    budget_score
):

    simulation = ctrl.ControlSystemSimulation(player_control_system)

    simulation.input['overall'] = overall_score
    simulation.input['potential'] = potential_score
    simulation.input['position_fit'] = position_score
    simulation.input['budget_fit'] = budget_score

    simulation.compute()

    return round(float(simulation.output['suitability']), 2)

# -----------------------------
# 7. Position Fit Calculation
# -----------------------------

def calculate_position_fit(player, position_group):

    if position_group == "Defender":

        score = (
            0.50 * player["defending"] +
            0.30 * player["physic"] +
            0.20 * player["pace"]
        )

    elif position_group == "Midfielder":

        score = (
            0.35 * player["passing"] +
            0.30 * player["dribbling"] +
            0.20 * player["physic"] +
            0.15 * player["defending"]
        )

    elif position_group == "Forward":

        score = (
            0.40 * player["shooting"] +
            0.25 * player["pace"] +
            0.25 * player["dribbling"] +
            0.10 * player["physic"]
        )

    else:
        return 0

    return round(float(score), 2)

# -----------------------------
# 8. Budget Fit Calculation
# -----------------------------

def calculate_budget_fit(player_value, budget):

    if budget <= 0:
        return 0

    fit = 100 * (1 - player_value / budget)

    fit = np.clip(fit, 0, 100)

    return round(float(fit), 2)

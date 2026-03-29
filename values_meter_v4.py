
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Values Meter v4", layout="wide")

st.title("Personal Values Meter v4")
st.caption("A detailed self-reflection dashboard with weighted scoring, cleaner Plotly visuals, dynamic thresholds, and a values risk view.")

DEFAULT_VALUES = [
    "Integrity",
    "Accountability",
    "Compassion",
    "Excellence",
    "Courage",
    "Fairness / Justice",
    "Growth",
    "Family / Relationships",
    "Health",
    "Contribution / Impact",
]

SHADOW_VALUES = [
    "Approval",
    "Status",
    "Control",
    "Comfort / Ease",
    "Avoiding conflict",
    "Speed / Efficiency",
    "Achievement",
    "Security",
    "Being right",
    "Independence",
    "Recognition",
    "Certainty",
]

CONFLICT_PAIRS = [
    "Family vs Achievement",
    "Integrity vs Loyalty",
    "Compassion vs Efficiency",
    "Excellence vs Sustainability",
    "Courage vs Harmony",
    "Justice vs Belonging",
    "Health vs Work output",
    "Growth vs Comfort",
    "Control vs Trust",
    "Contribution vs Security",
]

BEHAVIOUR_OPTIONS = [
    "Speak up earlier",
    "Protect time boundaries",
    "Follow through more consistently",
    "Pause before reacting",
    "Reduce overcommitment",
    "Choose honesty over harmony",
    "Make decisions faster",
    "Listen more before deciding",
    "Prioritise recovery and health",
    "Say no more clearly",
    "Escalate concerns sooner",
    "Stop rescuing other people’s avoidable problems",
]

TRIGGER_OPTIONS = [
    "Conflict with a colleague",
    "Fatigue / stress",
    "High workload",
    "Urgent deadline",
    "Family demand vs work demand",
    "Fear of disappointing others",
    "Ambiguity / uncertainty",
    "Desire to keep control",
    "Need for approval",
    "Pressure to be efficient",
    "Reputation risk",
    "Pressure from authority",
]

LENSES = [
    "Overall life",
    "Work / leadership",
    "Family / relationships",
    "Health / self-care",
    "Decision-making under pressure",
]

PROFILE_ARCHETYPES = {
    "Grounded / balanced": "Generally aligned across declared, lived, and pressure-tested values.",
    "Aspirational / stretched": "Strong ideals, but lived pattern has not fully caught up.",
    "High-functioning but brittle": "Strong normal performance, but values soften under pressure.",
    "Duty-driven": "Accountability, contribution, and discipline dominate identity and action.",
    "Harmony-protective": "Compassion and belonging matter, but may compete with candour and courage.",
    "Control-oriented": "Strong need for certainty, order, and personal agency may shape decisions.",
}

SCORE_HELP = """
1 = rarely true  
2 = sometimes true  
3 = mixed / inconsistent  
4 = mostly true  
5 = consistently true
"""

def classify_value(declared, lived, pressure, ideal):
    gap = declared - lived
    pressure_drop = lived - pressure
    ideal_gap = ideal - lived

    if gap <= 0.6 and pressure_drop <= 0.6 and ideal_gap <= 0.6:
        return "Embedded"
    if pressure_drop >= 1.0:
        return "Fragile under pressure"
    if gap >= 1.0 and ideal_gap >= 1.0:
        return "Aspirational"
    if gap >= 1.5 and lived < 3:
        return "Performative risk"
    if declared < 3.5 and lived >= 4:
        return "Hidden strength"
    return "Mixed"

def weighted_average(row, weights):
    total = sum(weights.values())
    if total == 0:
        return 0
    return sum(row[k] * weights[k] for k in weights) / total

def build_df(values, scores, weights):
    rows = []
    for v in values:
        row = {
            "Value": v,
            "Importance": scores[f"{v}_importance"],
            "Ideal Self": scores[f"{v}_ideal"],
            "Time & Energy": scores[f"{v}_time_energy"],
            "Decision Alignment": scores[f"{v}_decisions"],
            "Behavioural Evidence": scores[f"{v}_behaviour"],
            "Pressure Test": scores[f"{v}_pressure"],
            "Trade-off Integrity": scores[f"{v}_tradeoff"],
            "Recovery After Strain": scores[f"{v}_recovery"],
            "Consistency Across Contexts": scores[f"{v}_consistency"],
        }

        lived = weighted_average(
            {
                "Time & Energy": row["Time & Energy"],
                "Decision Alignment": row["Decision Alignment"],
                "Behavioural Evidence": row["Behavioural Evidence"],
                "Consistency Across Contexts": row["Consistency Across Contexts"],
            },
            {
                "Time & Energy": weights["Time & Energy"],
                "Decision Alignment": weights["Decision Alignment"],
                "Behavioural Evidence": weights["Behavioural Evidence"],
                "Consistency Across Contexts": weights["Consistency Across Contexts"],
            },
        )

        pressure = weighted_average(
            {
                "Pressure Test": row["Pressure Test"],
                "Trade-off Integrity": row["Trade-off Integrity"],
                "Recovery After Strain": row["Recovery After Strain"],
            },
            {
                "Pressure Test": weights["Pressure Test"],
                "Trade-off Integrity": weights["Trade-off Integrity"],
                "Recovery After Strain": weights["Recovery After Strain"],
            },
        )

        row["Declared"] = round(row["Importance"], 2)
        row["Lived"] = round(lived, 2)
        row["Pressure"] = round(pressure, 2)
        row["Declared Gap"] = round(row["Declared"] - row["Lived"], 2)
        row["Pressure Drop"] = round(row["Lived"] - row["Pressure"], 2)
        row["Ideal Gap"] = round(row["Ideal Self"] - row["Lived"], 2)
        row["Risk Score"] = round((row["Declared Gap"] * 0.45) + (row["Pressure Drop"] * 0.45) + max(row["Ideal Gap"], 0) * 0.10, 2)
        row["Type"] = classify_value(row["Declared"], row["Lived"], row["Pressure"], row["Ideal Self"])
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Risk Rank"] = df["Risk Score"].rank(method="dense", ascending=False).astype(int)
    return df.sort_values(["Risk Score", "Declared Gap", "Pressure Drop"], ascending=False).reset_index(drop=True)

def radar_chart(df):
    labels = df["Value"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df["Declared"].tolist(),
        theta=labels,
        fill='toself',
        name='Declared',
    ))
    fig.add_trace(go.Scatterpolar(
        r=df["Lived"].tolist(),
        theta=labels,
        fill='toself',
        name='Lived',
    ))
    fig.add_trace(go.Scatterpolar(
        r=df["Pressure"].tolist(),
        theta=labels,
        fill='toself',
        name='Pressure',
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        margin=dict(l=30, r=30, t=30, b=30),
    )
    return fig

def quadrant_chart(df):
    x_thresh = float(df["Declared Gap"].mean())
    y_thresh = float(df["Pressure Drop"].mean())

    fig = px.scatter(
        df,
        x="Declared Gap",
        y="Pressure Drop",
        size="Risk Score",
        color="Type",
        hover_name="Value",
        hover_data={
            "Lived": True,
            "Pressure": True,
            "Declared Gap": ':.2f',
            "Pressure Drop": ':.2f',
            "Risk Score": ':.2f',
            "Type": True,
        },
        size_max=40,
    )

    fig.add_vline(x=x_thresh, line_dash="dash", line_color="grey")
    fig.add_hline(y=y_thresh, line_dash="dash", line_color="grey")

    x_max = max(2.0, float(df["Declared Gap"].max()) + 0.4)
    y_max = max(2.0, float(df["Pressure Drop"].max()) + 0.4)
    x_min = min(-0.2, float(df["Declared Gap"].min()) - 0.1)
    y_min = min(-0.2, float(df["Pressure Drop"].min()) - 0.1)

    fig.update_xaxes(range=[x_min, x_max], title="Declared minus lived gap")
    fig.update_yaxes(range=[y_min, y_max], title="Lived minus pressure drop")

    fig.update_traces(
        marker=dict(opacity=0.72, line=dict(width=1, color="white"))
    )

    fig.add_annotation(x=x_min + 0.12, y=y_max - 0.12, text="Fragile values", showarrow=False)
    fig.add_annotation(x=x_max - 0.35, y=y_max - 0.12, text="Risk zone", showarrow=False)
    fig.add_annotation(x=x_min + 0.12, y=y_min + 0.12, text="Embedded values", showarrow=False)
    fig.add_annotation(x=x_max - 0.45, y=y_min + 0.12, text="Aspirational values", showarrow=False)

    fig.update_layout(
        margin=dict(l=30, r=30, t=30, b=30),
        legend_title_text="Type",
    )
    return fig

def component_bar_chart(df):
    components = df.melt(
        id_vars=["Value"],
        value_vars=[
            "Time & Energy",
            "Decision Alignment",
            "Behavioural Evidence",
            "Pressure Test",
            "Trade-off Integrity",
            "Recovery After Strain",
            "Consistency Across Contexts",
        ],
        var_name="Component",
        value_name="Score",
    )
    fig = px.bar(
        components,
        x="Value",
        y="Score",
        color="Component",
        barmode="group",
    )
    fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
    return fig

def risk_bar_chart(df):
    plot_df = df.sort_values("Risk Score", ascending=True)
    fig = px.bar(
        plot_df,
        x="Risk Score",
        y="Value",
        color="Type",
        orientation="h",
        text="Risk Rank",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Risk score",
        yaxis_title="",
        margin=dict(l=30, r=30, t=30, b=30),
    )
    return fig

def generate_recommendation(row):
    if row["Type"] == "Fragile under pressure":
        return "Build pressure safeguards: pre-commitment rules, pause points, and recovery habits."
    if row["Type"] == "Aspirational":
        return "Turn intention into visible routines, calendar choices, and clearer behavioural commitments."
    if row["Type"] == "Performative risk":
        return "Reduce rhetoric and define one concrete action that proves this value in practice."
    if row["Type"] == "Embedded":
        return "Protect this as a core strength and use it to stabilise weaker values."
    if row["Type"] == "Hidden strength":
        return "Acknowledge and deliberately leverage this underestimated strength."
    return "Clarify where this value matters most and define the smallest next behavioural proof point."

def generate_summary(df, lens, shadow_choice, conflict_pair, winning_side, growth_value, behaviour_change, trigger, archetype):
    top_strength = df.sort_values("Lived", ascending=False).iloc[0]
    top_gap = df.sort_values("Declared Gap", ascending=False).iloc[0]
    brittle = df.sort_values("Pressure Drop", ascending=False).iloc[0]
    closest_ideal = df.sort_values("Ideal Gap", ascending=True).iloc[0]
    top_risk = df.sort_values("Risk Score", ascending=False).iloc[0]

    lines = [
        f"Lens selected: **{lens}**.",
        f"Your strongest lived value is **{top_strength['Value']}**.",
        f"Your biggest declared-to-lived gap is **{top_gap['Value']}**.",
        f"Your most pressure-sensitive value is **{brittle['Value']}**.",
        f"Your closest value to your ideal self is **{closest_ideal['Value']}**.",
        f"Your highest current risk value is **{top_risk['Value']}**.",
        f"You identified your current pattern most closely with **{archetype}**.",
        PROFILE_ARCHETYPES[archetype],
    ]
    if shadow_choice:
        lines.append(f"Likely shadow drivers under strain: **{', '.join(shadow_choice)}**.")
    lines.append(f"Recurring conflict selected: **{conflict_pair}** with **{winning_side.lower()}**.")
    lines.append(
        f"Immediate development focus: **{growth_value}** through **{behaviour_change.lower()}** when facing **{trigger.lower()}**."
    )
    return lines

with st.sidebar:
    st.header("Setup")
    lens = st.selectbox("Reflection lens", LENSES, index=0)
    selected_values = st.multiselect(
        "Choose 5 to 10 values",
        DEFAULT_VALUES,
        default=DEFAULT_VALUES[:6],
    )
    archetype = st.selectbox("Which profile feels closest right now?", list(PROFILE_ARCHETYPES.keys()))
    st.markdown("### Scoring guide")
    st.markdown(SCORE_HELP)

    st.markdown("### Weight the lived-value model")
    w_time = st.slider("Weight: Time & Energy", 1, 5, 3)
    w_decisions = st.slider("Weight: Decision Alignment", 1, 5, 4)
    w_behaviour = st.slider("Weight: Behavioural Evidence", 1, 5, 4)
    w_consistency = st.slider("Weight: Consistency Across Contexts", 1, 5, 3)

    st.markdown("### Weight the pressure model")
    w_pressure = st.slider("Weight: Pressure Test", 1, 5, 5)
    w_tradeoff = st.slider("Weight: Trade-off Integrity", 1, 5, 4)
    w_recovery = st.slider("Weight: Recovery After Strain", 1, 5, 3)

weights = {
    "Time & Energy": w_time,
    "Decision Alignment": w_decisions,
    "Behavioural Evidence": w_behaviour,
    "Consistency Across Contexts": w_consistency,
    "Pressure Test": w_pressure,
    "Trade-off Integrity": w_tradeoff,
    "Recovery After Strain": w_recovery,
}

if len(selected_values) < 3:
    st.warning("Choose at least 3 values.")
    st.stop()

st.subheader("1) Detailed scoring")
st.markdown("Use the sliders to score both your current pattern and your ideal standard.")

scores = {}
for value in selected_values:
    with st.expander(value, expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            scores[f"{value}_importance"] = st.slider(f"{value}: Importance", 1, 5, 4, key=f"{value}_importance")
            scores[f"{value}_ideal"] = st.slider(f"{value}: Ideal self", 1, 5, 5, key=f"{value}_ideal")
        with c2:
            scores[f"{value}_time_energy"] = st.slider(f"{value}: Time & Energy", 1, 5, 3, key=f"{value}_time_energy")
            scores[f"{value}_decisions"] = st.slider(f"{value}: Decision Alignment", 1, 5, 3, key=f"{value}_decisions")
        with c3:
            scores[f"{value}_behaviour"] = st.slider(f"{value}: Behavioural Evidence", 1, 5, 3, key=f"{value}_behaviour")
            scores[f"{value}_consistency"] = st.slider(f"{value}: Consistency Across Contexts", 1, 5, 3, key=f"{value}_consistency")
        with c4:
            scores[f"{value}_pressure"] = st.slider(f"{value}: Pressure Test", 1, 5, 3, key=f"{value}_pressure")
            scores[f"{value}_tradeoff"] = st.slider(f"{value}: Trade-off Integrity", 1, 5, 3, key=f"{value}_tradeoff")
            scores[f"{value}_recovery"] = st.slider(f"{value}: Recovery After Strain", 1, 5, 3, key=f"{value}_recovery")

df = build_df(selected_values, scores, weights)
top_risks = df.head(3).copy()
top_risks["Recommendation"] = top_risks.apply(generate_recommendation, axis=1)

st.subheader("2) Dashboard overview")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Average Declared", f"{df['Declared'].mean():.2f}")
m2.metric("Average Lived", f"{df['Lived'].mean():.2f}")
m3.metric("Average Pressure", f"{df['Pressure'].mean():.2f}")
m4.metric("Average Declared Gap", f"{df['Declared Gap'].mean():.2f}")
m5.metric("Average Pressure Drop", f"{df['Pressure Drop'].mean():.2f}")
m6.metric("Highest Risk Score", f"{df['Risk Score'].max():.2f}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Plotly visuals", "Values risk dashboard", "Structured reflection", "Raw data"])

with tab1:
    left, right = st.columns([1.2, 1])
    with left:
        st.dataframe(
            df[["Risk Rank", "Value", "Declared", "Lived", "Pressure", "Declared Gap", "Pressure Drop", "Ideal Gap", "Risk Score", "Type"]],
            use_container_width=True,
            hide_index=True,
        )
    with right:
        st.markdown("### Top signals")
        top_lived = df.sort_values("Lived", ascending=False).head(3)
        top_gap = df.sort_values("Declared Gap", ascending=False).head(3)
        top_pressure = df.sort_values("Pressure Drop", ascending=False).head(3)

        st.markdown("**Strongest lived values**")
        for _, row in top_lived.iterrows():
            st.write(f"- {row['Value']} — {row['Lived']:.2f}")

        st.markdown("**Biggest declared gaps**")
        for _, row in top_gap.iterrows():
            st.write(f"- {row['Value']} — {row['Declared Gap']:.2f}")

        st.markdown("**Most fragile under pressure**")
        for _, row in top_pressure.iterrows():
            st.write(f"- {row['Value']} — {row['Pressure Drop']:.2f}")

with tab2:
    st.plotly_chart(radar_chart(df), use_container_width=True)
    st.plotly_chart(quadrant_chart(df), use_container_width=True)
    st.plotly_chart(component_bar_chart(df), use_container_width=True)

with tab3:
    st.markdown("### Ranked values risk view")
    st.plotly_chart(risk_bar_chart(df), use_container_width=True)

    st.markdown("### Top 3 risk values and recommendations")
    for _, row in top_risks.iterrows():
        st.markdown(f"**{row['Risk Rank']}. {row['Value']}**")
        st.write(f"Type: {row['Type']}")
        st.write(f"Risk score: {row['Risk Score']:.2f}")
        st.write(f"Why it is showing up: declared gap {row['Declared Gap']:.2f}, pressure drop {row['Pressure Drop']:.2f}, ideal gap {row['Ideal Gap']:.2f}.")
        st.write(f"Recommended next move: {row['Recommendation']}")
        st.markdown("---")

with tab4:
    shadow_choice = st.multiselect(
        "Select 1 to 4 shadow drivers that often influence you under pressure",
        SHADOW_VALUES,
        default=[],
    )
    conflict_pair = st.selectbox("Pick the most relevant recurring values conflict", CONFLICT_PAIRS)
    winning_side = st.radio(
        "Which side usually wins in practice?",
        ["Usually the first value", "About even", "Usually the second value"],
        horizontal=True,
    )
    strongest_value = st.selectbox(
        "Which of your strongest values feels most authentic?",
        df.sort_values("Lived", ascending=False)["Value"].tolist()
    )
    growth_value = st.selectbox(
        "Which value most needs development?",
        df.sort_values("Risk Score", ascending=False)["Value"].tolist()
    )
    behaviour_change = st.selectbox("Pick one behaviour change", BEHAVIOUR_OPTIONS)
    trigger = st.selectbox("What situation will test this?", TRIGGER_OPTIONS)

    st.markdown("### Auto-summary")
    summary_lines = generate_summary(
        df, lens, shadow_choice, conflict_pair, winning_side, growth_value, behaviour_change, trigger, archetype
    )
    for line in summary_lines:
        st.markdown(f"- {line}")

    st.markdown(f"**Most authentic strength selected:** {strongest_value}")

with tab5:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("3) Export")
scores_csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download scores CSV",
    data=scores_csv,
    file_name="values_meter_v4_scores.csv",
    mime="text/csv",
)

reflection_data = pd.DataFrame({
    "Field": [
        "Lens",
        "Archetype",
        "Strongest lived value",
        "Biggest declared gap",
        "Most fragile under pressure",
        "Highest risk value",
        "Closest to ideal self",
        "Shadow drivers",
        "Conflict pair",
        "Winning side",
        "Authentic strength selected",
        "Development focus",
        "Behaviour change",
        "Trigger",
    ],
    "Response": [
        lens,
        archetype,
        df.sort_values("Lived", ascending=False).iloc[0]["Value"],
        df.sort_values("Declared Gap", ascending=False).iloc[0]["Value"],
        df.sort_values("Pressure Drop", ascending=False).iloc[0]["Value"],
        df.sort_values("Risk Score", ascending=False).iloc[0]["Value"],
        df.sort_values("Ideal Gap", ascending=True).iloc[0]["Value"],
        ", ".join(shadow_choice) if 'shadow_choice' in locals() else "",
        conflict_pair if 'conflict_pair' in locals() else "",
        winning_side if 'winning_side' in locals() else "",
        strongest_value if 'strongest_value' in locals() else "",
        growth_value if 'growth_value' in locals() else "",
        behaviour_change if 'behaviour_change' in locals() else "",
        trigger if 'trigger' in locals() else "",
    ]
}).to_csv(index=False).encode("utf-8")

st.download_button(
    "Download reflection CSV",
    data=reflection_data,
    file_name="values_meter_v4_reflection.csv",
    mime="text/csv",
)

st.markdown("---")
st.markdown("This version is designed to surface not just what you value, but where your values are brittle, idealised, or highest risk across context and pressure.")

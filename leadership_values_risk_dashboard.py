
import io
import json
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

st.set_page_config(page_title="Leadership Values Risk Dashboard", layout="wide")

APP_TITLE = "Leadership Values Risk Dashboard"
APP_SUBTITLE = "A structured self-reflection and decision-quality dashboard for leaders."

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

DEFAULT_WEIGHTS = {
    "Time & Energy": 3,
    "Decision Alignment": 4,
    "Behavioural Evidence": 4,
    "Consistency Across Contexts": 3,
    "Pressure Test": 5,
    "Trade-off Integrity": 4,
    "Recovery After Strain": 3,
}

if "saved_sessions" not in st.session_state:
    st.session_state.saved_sessions = {}

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
    return 0 if total == 0 else sum(row[k] * weights[k] for k in weights) / total

def build_df(values, scores, weights, profile_name):
    rows = []
    for v in values:
        row = {
            "Profile": profile_name,
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
        row["Risk Score"] = round(
            (row["Declared Gap"] * 0.45) + (row["Pressure Drop"] * 0.45) + max(row["Ideal Gap"], 0) * 0.10,
            2,
        )
        row["Type"] = classify_value(row["Declared"], row["Lived"], row["Pressure"], row["Ideal Self"])
        rows.append(row)
    df = pd.DataFrame(rows)
    df["Risk Rank"] = df["Risk Score"].rank(method="dense", ascending=False).astype(int)
    return df.sort_values(["Risk Score", "Declared Gap", "Pressure Drop"], ascending=False).reset_index(drop=True)

def radar_chart(df):
    labels = df["Value"].tolist()
    fig = go.Figure()
    for metric in ["Declared", "Lived", "Pressure"]:
        fig.add_trace(go.Scatterpolar(r=df[metric].tolist(), theta=labels, fill="toself", name=metric))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, margin=dict(l=25, r=25, t=25, b=25))
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
        hover_data={"Lived": ':.2f', "Pressure": ':.2f', "Declared Gap": ':.2f', "Pressure Drop": ':.2f', "Risk Score": ':.2f', "Type": True},
        size_max=42,
    )
    fig.add_vline(x=x_thresh, line_dash="dash", line_color="grey")
    fig.add_hline(y=y_thresh, line_dash="dash", line_color="grey")
    x_max = max(2.0, float(df["Declared Gap"].max()) + 0.4)
    y_max = max(2.0, float(df["Pressure Drop"].max()) + 0.4)
    x_min = min(-0.2, float(df["Declared Gap"].min()) - 0.1)
    y_min = min(-0.2, float(df["Pressure Drop"].min()) - 0.1)
    fig.update_xaxes(range=[x_min, x_max], title="Declared minus lived gap")
    fig.update_yaxes(range=[y_min, y_max], title="Lived minus pressure drop")
    fig.update_traces(marker=dict(opacity=0.72, line=dict(width=1, color="white")))
    fig.add_annotation(x=x_min + 0.12, y=y_max - 0.12, text="Fragile values", showarrow=False)
    fig.add_annotation(x=x_max - 0.35, y=y_max - 0.12, text="Risk zone", showarrow=False)
    fig.add_annotation(x=x_min + 0.12, y=y_min + 0.12, text="Embedded values", showarrow=False)
    fig.add_annotation(x=x_max - 0.45, y=y_min + 0.12, text="Aspirational values", showarrow=False)
    fig.update_layout(margin=dict(l=25, r=25, t=25, b=25), legend_title_text="Type")
    return fig

def component_bar_chart(df):
    components = df.melt(
        id_vars=["Value"],
        value_vars=["Time & Energy", "Decision Alignment", "Behavioural Evidence", "Pressure Test", "Trade-off Integrity", "Recovery After Strain", "Consistency Across Contexts"],
        var_name="Component",
        value_name="Score",
    )
    fig = px.bar(components, x="Value", y="Score", color="Component", barmode="group")
    fig.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    return fig

def risk_bar_chart(df):
    plot_df = df.sort_values("Risk Score", ascending=True)
    fig = px.bar(plot_df, x="Risk Score", y="Value", color="Type", orientation="h", text="Risk Rank")
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Risk score", yaxis_title="", margin=dict(l=25, r=25, t=25, b=25))
    return fig

def compare_chart(current_df, comparison_df, metric):
    merged = current_df[["Value", metric]].merge(comparison_df[["Value", metric]], on="Value", suffixes=(" (Current)", " (Comparison)"))
    long_df = merged.melt(id_vars=["Value"], var_name="Profile", value_name="Score")
    fig = px.bar(long_df, x="Value", y="Score", color="Profile", barmode="group")
    fig.update_layout(margin=dict(l=25, r=25, t=25, b=25))
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

def generate_executive_language(df):
    highest_risk = df.sort_values("Risk Score", ascending=False).iloc[0]
    strongest = df.sort_values("Lived", ascending=False).iloc[0]
    pressure_sensitive = df.sort_values("Pressure Drop", ascending=False).iloc[0]
    return [
        f"The current profile suggests that **{strongest['Value']}** is the strongest operational value. It is not just endorsed in principle; it appears more consistently reflected in behaviour and day-to-day choices.",
        f"The principal leadership risk sits in **{highest_risk['Value']}**, where the gap between stated importance, lived pattern, and pressure performance is most pronounced. This is the value most likely to generate internal dissonance or inconsistent decision-making.",
        f"The most pressure-sensitive value appears to be **{pressure_sensitive['Value']}**. In practice, this suggests the value may be credible in stable conditions but less reliable under workload, fatigue, urgency, or reputational pressure.",
    ]

def generate_summary(df, lens, shadow_choice, conflict_pair, winning_side, growth_value, behaviour_change, trigger, archetype):
    top_strength = df.sort_values("Lived", ascending=False).iloc[0]
    top_gap = df.sort_values("Declared Gap", ascending=False).iloc[0]
    brittle = df.sort_values("Pressure Drop", ascending=False).iloc[0]
    closest_ideal = df.sort_values("Ideal Gap", ascending=True).iloc[0]
    top_risk = df.sort_values("Risk Score", ascending=False).iloc[0]
    lines = [
        f"Lens selected: **{lens}**.",
        f"Strongest lived value: **{top_strength['Value']}**.",
        f"Biggest declared-to-lived gap: **{top_gap['Value']}**.",
        f"Most pressure-sensitive value: **{brittle['Value']}**.",
        f"Closest value to ideal self: **{closest_ideal['Value']}**.",
        f"Highest current risk value: **{top_risk['Value']}**.",
        f"Overall pattern selected: **{archetype}**.",
        PROFILE_ARCHETYPES[archetype],
    ]
    if shadow_choice:
        lines.append(f"Likely shadow drivers under strain: **{', '.join(shadow_choice)}**.")
    lines.append(f"Recurring conflict selected: **{conflict_pair}** with **{winning_side.lower()}**.")
    lines.append(f"Immediate development focus: **{growth_value}** through **{behaviour_change.lower()}** when facing **{trigger.lower()}**.")
    return lines

def make_pdf(df, summary_lines, executive_paragraphs, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    for para in executive_paragraphs:
        story.append(Paragraph(para, styles["BodyText"]))
        story.append(Spacer(1, 8))
    story.append(Paragraph("Structured Summary", styles["Heading2"]))
    for line in summary_lines:
        story.append(Paragraph(f"• {line.replace('**', '')}", styles["BodyText"]))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Top Risk Values", styles["Heading2"]))
    top_df = df.sort_values("Risk Score", ascending=False).head(5)
    for _, row in top_df.iterrows():
        text = f"{int(row['Risk Rank'])}. {row['Value']} — type: {row['Type']}; risk score: {row['Risk Score']:.2f}; declared gap: {row['Declared Gap']:.2f}; pressure drop: {row['Pressure Drop']:.2f}; recommendation: {generate_recommendation(row)}"
        story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 6))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_profile_scores(values, prefix):
    scores = {}
    for value in values:
        with st.expander(f"{prefix}: {value}", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                scores[f"{value}_importance"] = st.slider(f"{value}: Importance ({prefix})", 1, 5, 4, key=f"{prefix}_{value}_importance")
                scores[f"{value}_ideal"] = st.slider(f"{value}: Ideal self ({prefix})", 1, 5, 5, key=f"{prefix}_{value}_ideal")
            with c2:
                scores[f"{value}_time_energy"] = st.slider(f"{value}: Time & Energy ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_time_energy")
                scores[f"{value}_decisions"] = st.slider(f"{value}: Decision Alignment ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_decisions")
            with c3:
                scores[f"{value}_behaviour"] = st.slider(f"{value}: Behavioural Evidence ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_behaviour")
                scores[f"{value}_consistency"] = st.slider(f"{value}: Consistency Across Contexts ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_consistency")
            with c4:
                scores[f"{value}_pressure"] = st.slider(f"{value}: Pressure Test ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_pressure")
                scores[f"{value}_tradeoff"] = st.slider(f"{value}: Trade-off Integrity ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_tradeoff")
                scores[f"{value}_recovery"] = st.slider(f"{value}: Recovery After Strain ({prefix})", 1, 5, 3, key=f"{prefix}_{value}_recovery")
    return scores

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

with st.sidebar:
    st.header("Setup")
    lens = st.selectbox("Reflection lens", LENSES, index=0)
    selected_values = st.multiselect("Choose 5 to 10 values", DEFAULT_VALUES, default=DEFAULT_VALUES[:6])
    archetype = st.selectbox("Which profile feels closest right now?", list(PROFILE_ARCHETYPES.keys()))
    mode = st.radio("Mode", ["Single profile", "Compare profiles"])
    comparison_label = st.selectbox("Compare current profile against", ["Ideal self", "Role demands"], index=0) if mode == "Compare profiles" else None
    st.markdown("### Scoring guide")
    st.markdown(SCORE_HELP)
    st.markdown("### Weight the lived-value model")
    w_time = st.slider("Weight: Time & Energy", 1, 5, DEFAULT_WEIGHTS["Time & Energy"])
    w_decisions = st.slider("Weight: Decision Alignment", 1, 5, DEFAULT_WEIGHTS["Decision Alignment"])
    w_behaviour = st.slider("Weight: Behavioural Evidence", 1, 5, DEFAULT_WEIGHTS["Behavioural Evidence"])
    w_consistency = st.slider("Weight: Consistency Across Contexts", 1, 5, DEFAULT_WEIGHTS["Consistency Across Contexts"])
    st.markdown("### Weight the pressure model")
    w_pressure = st.slider("Weight: Pressure Test", 1, 5, DEFAULT_WEIGHTS["Pressure Test"])
    w_tradeoff = st.slider("Weight: Trade-off Integrity", 1, 5, DEFAULT_WEIGHTS["Trade-off Integrity"])
    w_recovery = st.slider("Weight: Recovery After Strain", 1, 5, DEFAULT_WEIGHTS["Recovery After Strain"])

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
current_scores = create_profile_scores(selected_values, "Current")
comparison_df = None
if mode == "Compare profiles":
    st.subheader("2) Comparison scoring")
    comparison_scores = create_profile_scores(selected_values, comparison_label)
    comparison_df = build_df(selected_values, comparison_scores, weights, comparison_label)

current_df = build_df(selected_values, current_scores, weights, "Current")
top_risks = current_df.head(3).copy()
top_risks["Recommendation"] = top_risks.apply(generate_recommendation, axis=1)

st.subheader("Dashboard overview")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Average Declared", f"{current_df['Declared'].mean():.2f}")
m2.metric("Average Lived", f"{current_df['Lived'].mean():.2f}")
m3.metric("Average Pressure", f"{current_df['Pressure'].mean():.2f}")
m4.metric("Average Declared Gap", f"{current_df['Declared Gap'].mean():.2f}")
m5.metric("Average Pressure Drop", f"{current_df['Pressure Drop'].mean():.2f}")
m6.metric("Highest Risk Score", f"{current_df['Risk Score'].max():.2f}")

tab_names = ["Summary", "Visuals", "Risk dashboard", "Structured reflection", "Export & save", "Raw data"]
if mode == "Compare profiles":
    tab_names.insert(2, "Compare mode")
tabs = st.tabs(tab_names)
tab_index = {name: i for i, name in enumerate(tab_names)}

with tabs[tab_index["Summary"]]:
    left, right = st.columns([1.2, 1])
    with left:
        st.dataframe(current_df[["Risk Rank", "Value", "Declared", "Lived", "Pressure", "Declared Gap", "Pressure Drop", "Ideal Gap", "Risk Score", "Type"]], use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Executive interpretation")
        for para in generate_executive_language(current_df):
            st.write(para)
        st.markdown("### Top signals")
        for title, sort_col, display_col in [
            ("Strongest lived values", "Lived", "Lived"),
            ("Biggest declared gaps", "Declared Gap", "Declared Gap"),
            ("Most fragile under pressure", "Pressure Drop", "Pressure Drop"),
        ]:
            st.markdown(f"**{title}**")
            temp_df = current_df.sort_values(sort_col, ascending=False).head(3)
            for _, row in temp_df.iterrows():
                st.write(f"- {row['Value']} — {row[display_col]:.2f}")

with tabs[tab_index["Visuals"]]:
    st.plotly_chart(radar_chart(current_df), use_container_width=True)
    st.plotly_chart(quadrant_chart(current_df), use_container_width=True)
    st.plotly_chart(component_bar_chart(current_df), use_container_width=True)

if mode == "Compare profiles":
    with tabs[tab_index["Compare mode"]]:
        st.markdown(f"### Current profile vs {comparison_label}")
        delta_df = current_df[["Value", "Lived", "Pressure", "Risk Score"]].merge(
            comparison_df[["Value", "Lived", "Pressure", "Risk Score"]],
            on="Value",
            suffixes=(" (Current)", f" ({comparison_label})"),
        )
        delta_df["Lived Delta"] = delta_df[f"Lived ({comparison_label})"] - delta_df["Lived (Current)"]
        delta_df["Pressure Delta"] = delta_df[f"Pressure ({comparison_label})"] - delta_df["Pressure (Current)"]
        delta_df["Risk Delta"] = delta_df[f"Risk Score ({comparison_label})"] - delta_df["Risk Score (Current)"]
        st.dataframe(delta_df, use_container_width=True, hide_index=True)
        metric_choice = st.selectbox("Comparison chart metric", ["Lived", "Pressure", "Risk Score"])
        st.plotly_chart(compare_chart(current_df, comparison_df, metric_choice), use_container_width=True)

with tabs[tab_index["Risk dashboard"]]:
    st.markdown("### Ranked values risk view")
    st.plotly_chart(risk_bar_chart(current_df), use_container_width=True)
    st.markdown("### Top 3 risk values and recommendations")
    for _, row in top_risks.iterrows():
        st.markdown(f"**{row['Risk Rank']}. {row['Value']}**")
        st.write(f"Type: {row['Type']}")
        st.write(f"Risk score: {row['Risk Score']:.2f}")
        st.write(f"Why it is showing up: declared gap {row['Declared Gap']:.2f}, pressure drop {row['Pressure Drop']:.2f}, ideal gap {row['Ideal Gap']:.2f}.")
        st.write(f"Recommended next move: {row['Recommendation']}")
        st.markdown("---")

with tabs[tab_index["Structured reflection"]]:
    shadow_choice = st.multiselect("Select 1 to 4 shadow drivers that often influence you under pressure", SHADOW_VALUES, default=[])
    conflict_pair = st.selectbox("Pick the most relevant recurring values conflict", CONFLICT_PAIRS)
    winning_side = st.radio("Which side usually wins in practice?", ["Usually the first value", "About even", "Usually the second value"], horizontal=True)
    strongest_value = st.selectbox("Which of your strongest values feels most authentic?", current_df.sort_values("Lived", ascending=False)["Value"].tolist())
    growth_value = st.selectbox("Which value most needs development?", current_df.sort_values("Risk Score", ascending=False)["Value"].tolist())
    behaviour_change = st.selectbox("Pick one behaviour change", BEHAVIOUR_OPTIONS)
    trigger = st.selectbox("What situation will test this?", TRIGGER_OPTIONS)
    st.markdown("### Auto-summary")
    summary_lines = generate_summary(current_df, lens, shadow_choice, conflict_pair, winning_side, growth_value, behaviour_change, trigger, archetype)
    for line in summary_lines:
        st.markdown(f"- {line}")
    st.markdown(f"**Most authentic strength selected:** {strongest_value}")

with tabs[tab_index["Export & save"]]:
    summary_lines = generate_summary(
        current_df,
        lens,
        shadow_choice if "shadow_choice" in locals() else [],
        conflict_pair if "conflict_pair" in locals() else CONFLICT_PAIRS[0],
        winning_side if "winning_side" in locals() else "About even",
        growth_value if "growth_value" in locals() else current_df.iloc[0]["Value"],
        behaviour_change if "behaviour_change" in locals() else BEHAVIOUR_OPTIONS[0],
        trigger if "trigger" in locals() else TRIGGER_OPTIONS[0],
        archetype,
    )
    executive_paragraphs = generate_executive_language(current_df)
    st.markdown("### Export")
    st.download_button("Download scores CSV", data=current_df.to_csv(index=False).encode("utf-8"), file_name="leadership_values_dashboard_scores.csv", mime="text/csv")
    reflection_df = pd.DataFrame({
        "Field": ["Lens", "Archetype", "Strongest lived value", "Highest risk value", "Most fragile value", "Shadow drivers", "Conflict pair", "Winning side", "Development focus", "Behaviour change", "Trigger"],
        "Response": [
            lens,
            archetype,
            current_df.sort_values("Lived", ascending=False).iloc[0]["Value"],
            current_df.sort_values("Risk Score", ascending=False).iloc[0]["Value"],
            current_df.sort_values("Pressure Drop", ascending=False).iloc[0]["Value"],
            ", ".join(shadow_choice) if "shadow_choice" in locals() else "",
            conflict_pair if "conflict_pair" in locals() else "",
            winning_side if "winning_side" in locals() else "",
            growth_value if "growth_value" in locals() else "",
            behaviour_change if "behaviour_change" in locals() else "",
            trigger if "trigger" in locals() else "",
        ],
    })
    st.download_button("Download reflection CSV", data=reflection_df.to_csv(index=False).encode("utf-8"), file_name="leadership_values_dashboard_reflection.csv", mime="text/csv")
    st.download_button("Download PDF report", data=make_pdf(current_df, summary_lines, executive_paragraphs, APP_TITLE), file_name="leadership_values_dashboard_report.pdf", mime="application/pdf")
    st.markdown("### Save session")
    session_name = st.text_input("Session name", value=f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if st.button("Save current session"):
        st.session_state.saved_sessions[session_name] = {
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "selected_values": selected_values,
            "lens": lens,
            "archetype": archetype,
            "mode": mode,
            "comparison_label": comparison_label,
            "current_df": current_df.to_dict(orient="records"),
            "comparison_df": comparison_df.to_dict(orient="records") if comparison_df is not None else None,
            "summary_lines": summary_lines,
            "reflection": reflection_df.to_dict(orient="records"),
        }
        st.success(f"Saved session: {session_name}")
    if st.session_state.saved_sessions:
        chosen = st.selectbox("Saved sessions", list(st.session_state.saved_sessions.keys()))
        saved = st.session_state.saved_sessions[chosen]
        st.json(saved)
        st.download_button("Download saved session JSON", data=json.dumps(saved, indent=2).encode("utf-8"), file_name=f"{chosen.replace(' ', '_').lower()}.json", mime="application/json")

with tabs[tab_index["Raw data"]]:
    st.dataframe(current_df, use_container_width=True, hide_index=True)
    if comparison_df is not None:
        st.markdown(f"### {comparison_label} raw data")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("This renamed version is designed as a leadership diagnostic: not just what you value, but where your values are strongest, brittle, idealised, or operationally misaligned.")

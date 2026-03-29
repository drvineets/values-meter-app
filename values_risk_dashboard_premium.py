import io
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(page_title="Leadership Values Risk Index", layout="wide")

st.markdown("""
<style>
:root {
  --bg: #0b1020;
  --panel: #11182d;
  --panel-2: #16203a;
  --text: #eef2ff;
  --muted: #a7b0c7;
  --accent: #c6a96b;
  --accent-2: #6ea8fe;
  --line: rgba(255,255,255,0.08);
  --success: #7fd1ae;
  --warn: #f0c36b;
  --danger: #ef8f8f;
}
html, body, [class*="css"]  {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}
.stApp {
  background:
    radial-gradient(circle at top right, rgba(110,168,254,0.10), transparent 25%),
    radial-gradient(circle at top left, rgba(198,169,107,0.10), transparent 25%),
    linear-gradient(180deg, #0b1020 0%, #0f1427 100%);
  color: var(--text);
}
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1400px;
}
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d1427 0%, #11182d 100%);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * {
  color: #eef2ff !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
  background-color: rgba(17,24,45,0.92) !important;
  border-color: rgba(255,255,255,0.10) !important;
}
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="tag"] {
  background: rgba(198,169,107,0.15) !important;
  border: 1px solid rgba(198,169,107,0.40) !important;
  color: #f7e7c4 !important;
}
section[data-testid="stSidebar"] .stMultiSelect svg,
section[data-testid="stSidebar"] .stSelectbox svg {
  fill: #eef2ff !important;
}
h1, h2, h3 {
  letter-spacing: -0.02em;
}
.hero {
  padding: 1.2rem 1.35rem 1.1rem 1.35rem;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(17,24,45,0.95) 0%, rgba(22,32,58,0.92) 100%);
  box-shadow: 0 18px 45px rgba(0,0,0,0.22);
  margin-bottom: 1rem;
}
.hero-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.2rem;
}
.hero-sub {
  color: var(--muted);
  font-size: 0.98rem;
}
.pill-row {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin-top: 0.9rem;
}
.pill {
  font-size: 0.82rem;
  padding: 0.38rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(198,169,107,0.22);
  color: #f7e7c4;
  background: rgba(198,169,107,0.10);
}
.metric-card {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(17,24,45,0.95), rgba(17,24,45,0.75));
  padding: 0.9rem 1rem;
  box-shadow: 0 12px 28px rgba(0,0,0,0.16);
}
.metric-label {
  color: var(--muted);
  font-size: 0.82rem;
  margin-bottom: 0.25rem;
}
.metric-value {
  color: var(--text);
  font-size: 1.55rem;
  font-weight: 700;
}
.metric-note {
  color: var(--accent);
  font-size: 0.77rem;
  margin-top: 0.18rem;
}
.section-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(17,24,45,0.95), rgba(17,24,45,0.80));
  padding: 1rem 1.05rem;
  box-shadow: 0 12px 28px rgba(0,0,0,0.16);
}
.small-muted {
  color: var(--muted);
  font-size: 0.86rem;
}
div[data-testid="stMetric"] {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(17,24,45,0.95), rgba(17,24,45,0.75));
  padding: 0.5rem 0.7rem;
}
div[data-testid="stDataFrame"] {
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
}
div[data-testid="stExpander"] {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(17,24,45,0.72);
  transition: all 0.2s ease;
}
div[data-testid="stExpander"]:hover {
  border-color: rgba(198,169,107,0.4);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}
button[kind="primary"] {
  border-radius: 999px !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 0.55rem;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 999px !important;
  border: 1px solid var(--line) !important;
  background: rgba(17,24,45,0.72) !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
}
hr {
  border-color: var(--line);
}
</style>
""", unsafe_allow_html=True)

APP_TITLE = "Leadership Values Risk Index"
APP_SUBTITLE = "A decision-quality diagnostic for alignment, pressure behaviour, and value execution."

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
    "Approval", "Status", "Control", "Comfort / Ease", "Avoiding conflict",
    "Speed / Efficiency", "Achievement", "Security", "Being right",
    "Independence", "Recognition", "Certainty",
]

CONFLICT_PAIRS = [
    "Family vs Achievement", "Integrity vs Loyalty", "Compassion vs Efficiency",
    "Excellence vs Sustainability", "Courage vs Harmony", "Justice vs Belonging",
    "Health vs Work output", "Growth vs Comfort", "Control vs Trust",
    "Contribution vs Security",
]

BEHAVIOUR_OPTIONS = [
    "Speak up earlier", "Protect time boundaries", "Follow through more consistently",
    "Pause before reacting", "Reduce overcommitment", "Choose honesty over harmony",
    "Make decisions faster", "Listen more before deciding",
    "Prioritise recovery and health", "Say no more clearly",
    "Escalate concerns sooner", "Stop rescuing other people’s avoidable problems",
]

TRIGGER_OPTIONS = [
    "Conflict with a colleague", "Fatigue / stress", "High workload",
    "Urgent deadline", "Family demand vs work demand",
    "Fear of disappointing others", "Ambiguity / uncertainty",
    "Desire to keep control", "Need for approval",
    "Pressure to be efficient", "Reputation risk", "Pressure from authority",
]

LENSES = [
    "Overall life", "Work / leadership", "Family / relationships",
    "Health / self-care", "Decision-making under pressure",
]

PROFILE_ARCHETYPES = {
    "Grounded / balanced": "Generally aligned across declared, lived, and pressure-tested values.",
    "Aspirational / stretched": "Strong ideals, but lived pattern has not fully caught up.",
    "High-functioning but brittle": "Strong normal performance, but values soften under pressure.",
    "Duty-driven": "Accountability, contribution, and discipline dominate identity and action.",
    "Harmony-protective": "Compassion and belonging matter, but may compete with candour and courage.",
    "Control-oriented": "Strong need for certainty, order, and personal agency may shape decisions.",
}

DEFAULT_WEIGHTS = {
    "Time & Energy": 3,
    "Decision Alignment": 4,
    "Behavioural Evidence": 4,
    "Consistency Across Contexts": 3,
    "Pressure Test": 5,
    "Trade-off Integrity": 4,
    "Recovery After Strain": 3,
}

if "loaded_session" not in st.session_state:
    st.session_state.loaded_session = None

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

def weighted_average(values, weights):
    total = sum(weights.values())
    return 0 if total == 0 else sum(values[k] * weights[k] for k in weights) / total

def build_df(values, scores, weights):
    rows = []
    for value in values:
        row = {
            "Value": value,
            "Importance": scores[f"{value}_importance"],
            "Ideal Self": scores[f"{value}_ideal"],
            "Time & Energy": scores[f"{value}_time_energy"],
            "Decision Alignment": scores[f"{value}_decisions"],
            "Behavioural Evidence": scores[f"{value}_behaviour"],
            "Consistency Across Contexts": scores[f"{value}_consistency"],
            "Pressure Test": scores[f"{value}_pressure"],
            "Trade-off Integrity": scores[f"{value}_tradeoff"],
            "Recovery After Strain": scores[f"{value}_recovery"],
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

def collect_scores(values, prefix, defaults=None):
    defaults = defaults or {}
    scores = {}
    for value in values:
        with st.expander(value, expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                scores[f"{value}_importance"] = st.slider(
                    f"{value}: Importance", 1, 5,
                    int(defaults.get(f"{value}_importance", 4)),
                    key=f"{prefix}_{value}_importance"
                )
                scores[f"{value}_ideal"] = st.slider(
                    f"{value}: Ideal self", 1, 5,
                    int(defaults.get(f"{value}_ideal", 5)),
                    key=f"{prefix}_{value}_ideal"
                )
            with c2:
                scores[f"{value}_time_energy"] = st.slider(
                    f"{value}: Time & Energy", 1, 5,
                    int(defaults.get(f"{value}_time_energy", 3)),
                    key=f"{prefix}_{value}_time_energy"
                )
                scores[f"{value}_decisions"] = st.slider(
                    f"{value}: Decision Alignment", 1, 5,
                    int(defaults.get(f"{value}_decisions", 3)),
                    key=f"{prefix}_{value}_decisions"
                )
            with c3:
                scores[f"{value}_behaviour"] = st.slider(
                    f"{value}: Behavioural Evidence", 1, 5,
                    int(defaults.get(f"{value}_behaviour", 3)),
                    key=f"{prefix}_{value}_behaviour"
                )
                scores[f"{value}_consistency"] = st.slider(
                    f"{value}: Consistency Across Contexts", 1, 5,
                    int(defaults.get(f"{value}_consistency", 3)),
                    key=f"{prefix}_{value}_consistency"
                )
            with c4:
                scores[f"{value}_pressure"] = st.slider(
                    f"{value}: Pressure Test", 1, 5,
                    int(defaults.get(f"{value}_pressure", 3)),
                    key=f"{prefix}_{value}_pressure"
                )
                scores[f"{value}_tradeoff"] = st.slider(
                    f"{value}: Trade-off Integrity", 1, 5,
                    int(defaults.get(f"{value}_tradeoff", 3)),
                    key=f"{prefix}_{value}_tradeoff"
                )
                scores[f"{value}_recovery"] = st.slider(
                    f"{value}: Recovery After Strain", 1, 5,
                    int(defaults.get(f"{value}_recovery", 3)),
                    key=f"{prefix}_{value}_recovery"
                )
    return scores

def theme_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef2ff"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=30, r=30, t=35, b=30),
    )
    return fig

def radar_chart(df_a, df_b=None, label_a="Current", label_b="Comparison"):
    labels = df_a["Value"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=df_a["Declared"].tolist(), theta=labels, fill="toself", name=f"{label_a} Declared"))
    fig.add_trace(go.Scatterpolar(r=df_a["Lived"].tolist(), theta=labels, fill="toself", name=f"{label_a} Lived"))
    fig.add_trace(go.Scatterpolar(r=df_a["Pressure"].tolist(), theta=labels, fill="toself", name=f"{label_a} Pressure"))
    if df_b is not None:
        fig.add_trace(go.Scatterpolar(r=df_b["Lived"].tolist(), theta=labels, name=f"{label_b} Lived"))
        fig.add_trace(go.Scatterpolar(r=df_b["Pressure"].tolist(), theta=labels, name=f"{label_b} Pressure"))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="rgba(255,255,255,0.12)", linecolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.15)")
        ),
        showlegend=True,
    )
    return theme_fig(fig)

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
            "Type": True
        },
        size_max=42,
    )
    fig.add_vline(x=x_thresh, line_dash="dash", line_color="rgba(255,255,255,0.4)")
    fig.add_hline(y=y_thresh, line_dash="dash", line_color="rgba(255,255,255,0.4)")
    x_max = max(2.0, float(df["Declared Gap"].max()) + 0.4)
    y_max = max(2.0, float(df["Pressure Drop"].max()) + 0.4)
    x_min = min(-0.2, float(df["Declared Gap"].min()) - 0.1)
    y_min = min(-0.2, float(df["Pressure Drop"].min()) - 0.1)
    fig.update_xaxes(range=[x_min, x_max], title="Declared minus lived gap", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(range=[y_min, y_max], title="Lived minus pressure drop", gridcolor="rgba(255,255,255,0.08)")
    fig.update_traces(marker=dict(opacity=0.78, line=dict(width=1, color="white")))
    fig.add_annotation(x=x_min + 0.12, y=y_max - 0.12, text="Fragile values", showarrow=False, font=dict(color="#eef2ff"))
    fig.add_annotation(x=x_max - 0.35, y=y_max - 0.12, text="Risk zone", showarrow=False, font=dict(color="#eef2ff"))
    fig.add_annotation(x=x_min + 0.12, y=y_min + 0.12, text="Embedded values", showarrow=False, font=dict(color="#eef2ff"))
    fig.add_annotation(x=x_max - 0.45, y=y_min + 0.12, text="Aspirational values", showarrow=False, font=dict(color="#eef2ff"))
    return theme_fig(fig)

def component_bar_chart(df):
    melted = df.melt(
        id_vars=["Value"],
        value_vars=[
            "Time & Energy", "Decision Alignment", "Behavioural Evidence",
            "Pressure Test", "Trade-off Integrity", "Recovery After Strain",
            "Consistency Across Contexts"
        ],
        var_name="Component",
        value_name="Score",
    )
    fig = px.bar(melted, x="Value", y="Score", color="Component", barmode="group")
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return theme_fig(fig)

def risk_bar_chart(df):
    plot_df = df.sort_values("Risk Score", ascending=True)
    fig = px.bar(plot_df, x="Risk Score", y="Value", color="Type", orientation="h", text="Risk Rank")
    fig.update_traces(textposition="outside")
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_layout(xaxis_title="Risk score", yaxis_title="")
    return theme_fig(fig)

def compare_delta_table(df_a, df_b):
    merged = df_a[["Value", "Lived", "Pressure", "Risk Score"]].merge(
        df_b[["Value", "Lived", "Pressure", "Risk Score"]],
        on="Value",
        suffixes=(" A", " B")
    )
    merged["Lived Delta"] = (merged["Lived A"] - merged["Lived B"]).round(2)
    merged["Pressure Delta"] = (merged["Pressure A"] - merged["Pressure B"]).round(2)
    merged["Risk Delta"] = (merged["Risk Score A"] - merged["Risk Score B"]).round(2)
    return merged.sort_values("Risk Delta", ascending=False)

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

def leadership_integrity_score(df):
    lived_component = df["Lived"].mean() / 5
    pressure_component = df["Pressure"].mean() / 5
    gap_penalty = min(df["Declared Gap"].mean() / 2.5, 1)
    drop_penalty = min(df["Pressure Drop"].mean() / 2.5, 1)
    score = ((lived_component * 0.4) + (pressure_component * 0.35) + ((1 - gap_penalty) * 0.15) + ((1 - drop_penalty) * 0.10)) * 100
    return round(max(0, min(score, 100)), 0)

def score_band(score):
    if score >= 85:
        return "high alignment"
    if score >= 70:
        return "good alignment"
    if score >= 55:
        return "mixed alignment"
    return "fragile alignment"

def executive_summary_lines(df, lens, shadow_choice, conflict_pair, winning_side, growth_value, behaviour_change, trigger, archetype):
    top_strength = df.sort_values("Lived", ascending=False).iloc[0]
    top_gap = df.sort_values("Declared Gap", ascending=False).iloc[0]
    brittle = df.sort_values("Pressure Drop", ascending=False).iloc[0]
    closest_ideal = df.sort_values("Ideal Gap", ascending=True).iloc[0]
    top_risk = df.sort_values("Risk Score", ascending=False).iloc[0]
    lines = [
        f"Assessment lens: {lens}.",
        f"Primary strength: {top_strength['Value']} demonstrates the highest lived consistency.",
        f"Highest declared-to-lived gap: {top_gap['Value']}.",
        f"Primary pressure vulnerability: {brittle['Value']}.",
        f"Closest alignment to ideal self: {closest_ideal['Value']}.",
        f"Highest current risk signal: {top_risk['Value']}.",
        f"Pattern selected: {archetype}. {PROFILE_ARCHETYPES[archetype]}",
    ]
    if shadow_choice:
        lines.append(f"Likely shadow drivers under strain: {', '.join(shadow_choice)}.")
    lines.append(f"Recurring values conflict: {conflict_pair}; operational winner: {winning_side.lower()}.")
    lines.append(f"Immediate development focus: {growth_value}.")
    lines.append(f"Selected behaviour shift: {behaviour_change}.")
    lines.append(f"Likely trigger context: {trigger}.")
    return lines

def compare_summary_lines(df_a, df_b, label_a, label_b):
    delta = compare_delta_table(df_a, df_b)
    best = delta.sort_values("Lived Delta", ascending=False).iloc[0]
    worst = delta.sort_values("Lived Delta", ascending=True).iloc[0]
    risk_gap = delta.sort_values("Risk Delta", ascending=False).iloc[0]
    return [
        f"Comparison set: {label_a} versus {label_b}.",
        f"Strongest positive lived delta for {label_a}: {best['Value']} ({best['Lived Delta']:+.2f}).",
        f"Largest shortfall for {label_a}: {worst['Value']} ({worst['Lived Delta']:+.2f}).",
        f"Greatest risk separation: {risk_gap['Value']} ({risk_gap['Risk Delta']:+.2f}).",
    ]

def build_session_payload(mode, selected_values, weights, lens, archetype, scores_a, scores_b=None, label_a="Current", label_b="Ideal / Role"):
    return {
        "mode": mode,
        "selected_values": selected_values,
        "weights": weights,
        "lens": lens,
        "archetype": archetype,
        "label_a": label_a,
        "label_b": label_b,
        "scores_a": scores_a,
        "scores_b": scores_b or {},
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }

def pdf_bytes(title, summary_lines, top_table_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=13)
    story = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 6),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body),
        Spacer(1, 10),
    ]
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    for line in summary_lines:
        story.append(Paragraph(f"• {line}", body))
    story += [Spacer(1, 8), Paragraph("Top Risk Values", styles["Heading2"])]
    table_data = [top_table_df.columns.tolist()] + top_table_df.astype(str).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-title">{title}</div>
          <div class="hero-sub">{subtitle}</div>
          <div class="pill-row">
            <div class="pill">Executive-style output</div>
            <div class="pill">Risk-ranked values</div>
            <div class="pill">Pressure diagnostics</div>
            <div class="pill">Compare mode</div>
            <div class="pill">PDF + JSON export</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def premium_metric(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

hero(APP_TITLE, APP_SUBTITLE)

with st.sidebar:
    st.header("Configuration")
    mode = st.radio("Mode", ["Single profile", "Compare mode"], index=0)
    lens = st.selectbox("Assessment lens", LENSES, index=0)
    selected_values = st.multiselect("Choose 5 to 10 values", DEFAULT_VALUES, default=DEFAULT_VALUES[:6])
    archetype = st.selectbox("Current pattern", list(PROFILE_ARCHETYPES.keys()))

    st.markdown("### Weighting model")
    w_time = st.slider("Time & Energy", 1, 5, DEFAULT_WEIGHTS["Time & Energy"])
    w_decisions = st.slider("Decision Alignment", 1, 5, DEFAULT_WEIGHTS["Decision Alignment"])
    w_behaviour = st.slider("Behavioural Evidence", 1, 5, DEFAULT_WEIGHTS["Behavioural Evidence"])
    w_consistency = st.slider("Consistency Across Contexts", 1, 5, DEFAULT_WEIGHTS["Consistency Across Contexts"])
    w_pressure = st.slider("Pressure Test", 1, 5, DEFAULT_WEIGHTS["Pressure Test"])
    w_tradeoff = st.slider("Trade-off Integrity", 1, 5, DEFAULT_WEIGHTS["Trade-off Integrity"])
    w_recovery = st.slider("Recovery After Strain", 1, 5, DEFAULT_WEIGHTS["Recovery After Strain"])

    uploaded_session = st.file_uploader("Load saved session", type="json")
    if uploaded_session is not None:
        try:
            st.session_state.loaded_session = json.load(uploaded_session)
            st.success("Session loaded.")
        except Exception:
            st.error("Could not read that JSON file.")

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

loaded = st.session_state.loaded_session or {}
defaults_a = loaded.get("scores_a", {})
defaults_b = loaded.get("scores_b", {}) if mode == "Compare mode" else {}

label_a = "Current"
label_b = "Comparison"
if mode == "Compare mode":
    c1, c2 = st.columns(2)
    with c1:
        label_a = st.text_input("Label for Profile A", value=loaded.get("label_a", "Current"))
    with c2:
        label_b = st.text_input("Label for Profile B", value=loaded.get("label_b", "Ideal / Role"))

st.subheader("Detailed scoring")
if mode == "Single profile":
    st.markdown(
        '<div class="small-muted">Score your current profile across declared, lived, and pressure-tested dimensions.</div>',
        unsafe_allow_html=True,
    )
    scores_a = collect_scores(selected_values, "single", defaults_a)
    scores_b = {}
    df_a = build_df(selected_values, scores_a, weights)
    df_b = None
else:
    left, right = st.columns(2)
    with left:
        st.markdown(f"### {label_a}")
        scores_a = collect_scores(selected_values, "a", defaults_a)
    with right:
        st.markdown(f"### {label_b}")
        scores_b = collect_scores(selected_values, "b", defaults_b)
    df_a = build_df(selected_values, scores_a, weights)
    df_b = build_df(selected_values, scores_b, weights)

top_risks = df_a.head(3).copy()
top_risks["Recommendation"] = top_risks.apply(generate_recommendation, axis=1)

integrity_score = leadership_integrity_score(df_a)
integrity_band = score_band(integrity_score)

st.subheader("Dashboard overview")
m0, m1, m2, m3, m4, m5, m6 = st.columns(7)
with m0:
    premium_metric("Leadership Integrity Score", f"{int(integrity_score)}/100", integrity_band)
with m1:
    premium_metric("Average Declared", f"{df_a['Declared'].mean():.2f}", "what you say matters")
with m2:
    premium_metric("Average Lived", f"{df_a['Lived'].mean():.2f}", "behavioural reality")
with m3:
    premium_metric("Average Pressure", f"{df_a['Pressure'].mean():.2f}", "stress resilience")
with m4:
    premium_metric("Declared Gap", f"{df_a['Declared Gap'].mean():.2f}", "aspiration gap")
with m5:
    premium_metric("Pressure Drop", f"{df_a['Pressure Drop'].mean():.2f}", "brittleness signal")
with m6:
    premium_metric("Highest Risk", f"{df_a['Risk Score'].max():.2f}", "top concern")

tab_summary, tab_visuals, tab_risk, tab_reflect, tab_export, tab_raw = st.tabs(
    ["Summary", "Visuals", "Risk Dashboard", "Reflection", "Export", "Raw Data"]
)

with tab_summary:
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Ranked values table")
        st.dataframe(
            df_a[["Risk Rank", "Value", "Declared", "Lived", "Pressure", "Declared Gap", "Pressure Drop", "Ideal Gap", "Risk Score", "Type"]],
            use_container_width=True,
            hide_index=True,
        )
        if df_b is not None:
            st.markdown("#### Comparison deltas")
            st.dataframe(compare_delta_table(df_a, df_b), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Executive signals")
        st.write(f"**Leadership Integrity Score**: {int(integrity_score)}/100 ({integrity_band})")
        st.write(f"**Primary strength**: {df_a.sort_values('Lived', ascending=False).iloc[0]['Value']}")
        st.write(f"**Highest current risk**: {df_a.sort_values('Risk Score', ascending=False).iloc[0]['Value']}")
        st.write(f"**Primary pressure vulnerability**: {df_a.sort_values('Pressure Drop', ascending=False).iloc[0]['Value']}")
        st.write(f"**Closest to ideal self**: {df_a.sort_values('Ideal Gap', ascending=True).iloc[0]['Value']}")
        if df_b is not None:
            st.markdown("#### Comparison readout")
            for line in compare_summary_lines(df_a, df_b, label_a, label_b):
                st.write(f"- {line}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_visuals:
    st.plotly_chart(radar_chart(df_a, df_b, label_a, label_b), use_container_width=True)
    st.plotly_chart(quadrant_chart(df_a), use_container_width=True)
    st.plotly_chart(component_bar_chart(df_a), use_container_width=True)

with tab_risk:
    st.plotly_chart(risk_bar_chart(df_a), use_container_width=True)
    c1, c2, c3 = st.columns(3)
    for col, (_, row) in zip([c1, c2, c3], top_risks.iterrows()):
        with col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"#### {int(row['Risk Rank'])}. {row['Value']}")
            st.write(f"**Category**: {row['Type']}")
            st.write(f"**Risk score**: {row['Risk Score']:.2f}")
            st.write(f"Declared gap {row['Declared Gap']:.2f}, pressure drop {row['Pressure Drop']:.2f}, ideal gap {row['Ideal Gap']:.2f}.")
            st.write(f"**Next move**: {row['Recommendation']}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab_reflect:
    shadow_choice = st.multiselect(
        "Select 1 to 4 shadow drivers that often influence you under pressure",
        SHADOW_VALUES,
        default=[]
    )
    conflict_pair = st.selectbox("Pick the most relevant recurring values conflict", CONFLICT_PAIRS)
    winning_side = st.radio(
        "Which side usually wins in practice?",
        ["Usually the first value", "About even", "Usually the second value"],
        horizontal=True
    )
    strongest_value = st.selectbox(
        "Which of your strongest values feels most authentic?",
        df_a.sort_values("Lived", ascending=False)["Value"].tolist()
    )
    growth_value = st.selectbox(
        "Which value most needs development?",
        df_a.sort_values("Risk Score", ascending=False)["Value"].tolist()
    )
    behaviour_change = st.selectbox("Pick one behaviour change", BEHAVIOUR_OPTIONS)
    trigger = st.selectbox("What situation will test this?", TRIGGER_OPTIONS)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("#### Executive summary")
    summary_lines = executive_summary_lines(
        df_a, lens, shadow_choice, conflict_pair, winning_side,
        growth_value, behaviour_change, trigger, archetype
    )
    for line in summary_lines:
        st.markdown(f"- {line}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_export:
    summary_lines = executive_summary_lines(
        df_a,
        lens,
        shadow_choice if "shadow_choice" in locals() else [],
        conflict_pair if "conflict_pair" in locals() else CONFLICT_PAIRS[0],
        winning_side if "winning_side" in locals() else "About even",
        growth_value if "growth_value" in locals() else df_a.sort_values("Risk Score", ascending=False).iloc[0]["Value"],
        behaviour_change if "behaviour_change" in locals() else BEHAVIOUR_OPTIONS[0],
        trigger if "trigger" in locals() else TRIGGER_OPTIONS[0],
        archetype,
    )
    session_payload = build_session_payload(
        mode, selected_values, weights, lens, archetype,
        scores_a, scores_b, label_a, label_b
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download session JSON",
            data=json.dumps(session_payload, indent=2),
            file_name="leadership_values_risk_index_session.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "Download scores CSV",
            data=df_a.to_csv(index=False).encode("utf-8"),
            file_name="leadership_values_risk_index_scores.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col3:
        pdf_table = top_risks[["Risk Rank", "Value", "Risk Score", "Type"]]
        st.download_button(
            "Download executive PDF",
            data=pdf_bytes("Leadership Values Risk Index Report", summary_lines, pdf_table),
            file_name="leadership_values_risk_index_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if df_b is not None:
        st.download_button(
            "Download comparison deltas CSV",
            data=compare_delta_table(df_a, df_b).to_csv(index=False).encode("utf-8"),
            file_name="leadership_values_risk_index_compare.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab_raw:
    st.dataframe(df_a, use_container_width=True, hide_index=True)
    if df_b is not None:
        st.markdown("#### Comparison profile raw data")
        st.dataframe(df_b, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    '<div class="small-muted">Premium theme update: improved sidebar contrast, refined interaction states, upgraded naming, and a top-line executive score.</div>',
    unsafe_allow_html=True,
)
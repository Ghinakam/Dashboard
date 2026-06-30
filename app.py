import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sleep Health Dashboard", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("sleep_health_master.csv")

df = load_data()

# Sleep Health Score
df["sleep_score_5"] = 0
df.loc[df["sleep_duration"].isin(["Less than 4 hours", "4-6 hours"]), "sleep_score_5"] += 1
df.loc[df["sleep_latency"].isin(["31-60 minutes", "More than 60 minutes"]), "sleep_score_5"] += 1
df.loc[df["fall_asleep_diff"].isin(["Often", "Always"]), "sleep_score_5"] += 1
df.loc[df["breathing_diff"].isin(["Often", "Always"]), "sleep_score_5"] += 1
df.loc[df["restless_legs"].isin(["Often", "Always"]), "sleep_score_5"] += 1

def classify_sleep(score):
    if score <= 1:
        return "Good Sleep Health"
    elif score <= 3:
        return "Moderate Sleep Risk"
    else:
        return "High Sleep Risk"

df["sleep_group_5"] = df["sleep_score_5"].apply(classify_sleep)

age_order = ["Under 18", "18-30", "31-50", "Above 50"]
gender_order = ["Male", "Female", "Prefer not to say"]
occupation_order = ["Student", "Working Professional", "Freelancing", "Unemployment", "Housewife", "Others"]
bmi_order = ["Underweight", "Normal", "Overweight", "Obese"]
sleep_duration_order = ["Less than 4 hours", "4-6 hours", "6-8 hours", "More than 8 hours"]
sleep_latency_order = ["Less than 15 minutes", "15-30 minutes", "31-60 minutes", "More than 60 minutes"]
frequency_order = ["Never", "Rarely", "Sometimes", "Often", "Always"]
sleep_group_order = ["Good Sleep Health", "Moderate Sleep Risk", "High Sleep Risk"]

COLORS = {
    "blue": "#2F6F9F",
    "teal": "#68A691",
    "orange": "#F4A261",
    "red": "#D96C75",
    "gray": "#6C757D"
}

RISK_COLORS = {
    "Good Sleep Health": "#68A691",
    "Moderate Sleep Risk": "#F4A261",
    "High Sleep Risk": "#D96C75"
}

st.title("🏥 Sleep Health Analytics Dashboard")
st.markdown("""
### An interactive dashboard for exploring sleep health patterns, associated risk factors, reported consequences, and coping strategies.

This dashboard evaluates sleep health using five indicators and identifies demographic groups at greater risk of poor sleep health.
""")

# Sidebar
st.sidebar.title("🔎 Dashboard Filters")
st.sidebar.markdown("Use the filters below to drill down into specific respondent groups.")

with st.sidebar.expander("👤 Age Group"):
    age_filter = st.multiselect("Select age group(s)", age_order, default=age_order)

with st.sidebar.expander("🚻 Gender"):
    gender_filter = st.multiselect("Select gender(s)", gender_order, default=gender_order)

with st.sidebar.expander("💼 Occupation"):
    occupation_filter = st.multiselect("Select occupation(s)", occupation_order, default=occupation_order)

with st.sidebar.expander("⚖️ BMI Category"):
    bmi_filter = st.multiselect("Select BMI category/categories", bmi_order, default=bmi_order)

with st.sidebar.expander("😴 Sleep Health Group"):
    risk_filter = st.multiselect("Select sleep health group(s)", sleep_group_order, default=sleep_group_order)

filtered = df[
    df["age"].isin(age_filter)
    & df["gender"].isin(gender_filter)
    & df["occupation"].isin(occupation_filter)
    & df["bmi_category"].isin(bmi_filter)
    & df["sleep_group_5"].isin(risk_filter)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# KPIs
total = len(filtered)
avg_score = filtered["sleep_score_5"].mean()
good_pct = filtered["sleep_group_5"].eq("Good Sleep Health").mean() * 100
moderate_pct = filtered["sleep_group_5"].eq("Moderate Sleep Risk").mean() * 100
high_pct = filtered["sleep_group_5"].eq("High Sleep Risk").mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("👥 Total Respondents", f"{total:,}")
k2.metric("😴 Average Sleep Score", f"{avg_score:.2f} / 5")
k3.metric("🟢 Good Sleep", f"{good_pct:.1f}%")
k4.metric("🟠 Moderate Risk", f"{moderate_pct:.1f}%")
k5.metric("🔴 High Risk", f"{high_pct:.1f}%")

st.divider()

# Helper functions
def ordered_count_data(data, column, order=None):
    temp = data[column].value_counts().reset_index()
    temp.columns = [column, "count"]
    if order:
        temp[column] = pd.Categorical(temp[column], categories=order, ordered=True)
        temp = temp.sort_values(column)
    return temp

def count_bar(data, column, title, order=None, color=COLORS["blue"]):
    chart_data = ordered_count_data(data, column, order)
    fig = px.bar(chart_data, x=column, y="count", text="count", title=title, color_discrete_sequence=[color])
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="", yaxis_title="Respondents", title_x=0.02, height=420, margin=dict(t=60, b=40))
    return fig

def count_bar_horizontal(data, column, title, order=None, color=COLORS["blue"]):
    chart_data = ordered_count_data(data, column, order)
    if order:
        chart_data = chart_data.sort_values(column, ascending=False)
    fig = px.bar(chart_data, x="count", y=column, text="count", orientation="h", title=title, color_discrete_sequence=[color])
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Respondents", yaxis_title="", title_x=0.02, height=420, margin=dict(t=60, b=40))
    return fig

def avg_score_bar(data, column, title, order=None, horizontal=False):
    chart_data = data.groupby(column)["sleep_score_5"].mean().reset_index()
    if order:
        chart_data[column] = pd.Categorical(chart_data[column], categories=order, ordered=True)
        chart_data = chart_data.sort_values(column)

    if horizontal:
        chart_data = chart_data.sort_values("sleep_score_5", ascending=True)
        fig = px.bar(chart_data, x="sleep_score_5", y=column, text=chart_data["sleep_score_5"].round(2),
                     orientation="h", title=title, color_discrete_sequence=[COLORS["red"]])
        fig.update_layout(xaxis_title="Average Sleep Health Score", yaxis_title="")
    else:
        fig = px.bar(chart_data, x=column, y="sleep_score_5", text=chart_data["sleep_score_5"].round(2),
                     title=title, color_discrete_sequence=[COLORS["red"]])
        fig.update_layout(xaxis_title="", yaxis_title="Average Sleep Health Score")

    fig.update_traces(textposition="outside")
    fig.update_layout(title_x=0.02, height=420, margin=dict(t=60, b=40))
    return fig

def horizontal_dummy_bar(data, columns, title, prefix):
    numeric_data = data[columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    chart_data = numeric_data.sum().sort_values(ascending=True).reset_index()
    chart_data.columns = ["category", "count"]
    chart_data["category"] = chart_data["category"].str.replace(prefix, "", regex=False).str.replace("_", " ").str.title()

    fig = px.bar(chart_data, x="count", y="category", orientation="h", text="count",
                 title=title, color_discrete_sequence=[COLORS["teal"]])
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Respondents", yaxis_title="", title_x=0.02, height=430, margin=dict(t=60, b=40))
    return fig

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "😴 Sleep Health",
    "⚠️ Risk Factors",
    "🧠 Consequences & Coping",
    "📋 Recommendations"
])

with tab1:
    st.header("Population Overview")
    st.caption("Objective: Describe the demographic characteristics of the study population.")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(count_bar(filtered, "age", "Age Distribution", age_order), use_container_width=True)
    with c2:
        st.plotly_chart(count_bar(filtered, "gender", "Gender Distribution", gender_order), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(count_bar_horizontal(filtered, "occupation", "Occupation Distribution", occupation_order), use_container_width=True)
    with c4:
        st.plotly_chart(count_bar(filtered, "bmi_category", "BMI Category Distribution", bmi_order), use_container_width=True)

with tab2:
    st.header("Sleep Health Indicators")
    st.caption("Objective: Present the five indicators used to assess sleep health.")

    with st.expander("Sleep Health Assessment Criteria", expanded=True):
        st.markdown("""
        Each respondent received **1 point** for each of the following poor sleep indicators:

        - **Sleep duration** below 6 hours  
        - **Sleep latency** greater than 30 minutes  
        - **Difficulty falling asleep** reported as Often or Always  
        - **Breathing difficulties during sleep** reported as Often or Always  
        - **Restless legs or involuntary movements** reported as Often or Always  

        The final Sleep Health Score ranges from **0 to 5**, where higher scores indicate poorer sleep health.
        """)

    s1, s2 = st.columns(2)
    with s1:
        st.plotly_chart(count_bar(filtered, "sleep_duration", "Sleep Duration", sleep_duration_order), use_container_width=True)
    with s2:
        st.plotly_chart(count_bar(filtered, "sleep_latency", "Sleep Latency", sleep_latency_order), use_container_width=True)

    s3, s4 = st.columns(2)
    with s3:
        st.plotly_chart(count_bar(filtered, "fall_asleep_diff", "Difficulty Falling Asleep", frequency_order), use_container_width=True)
    with s4:
        st.plotly_chart(count_bar(filtered, "breathing_diff", "Breathing Difficulties While Sleeping", frequency_order), use_container_width=True)

    st.plotly_chart(count_bar(filtered, "restless_legs", "Restless Legs / Involuntary Movements", frequency_order), use_container_width=True)

    st.subheader("Sleep Health Risk Classification")
    r1, r2 = st.columns(2)

    with r1:
        st.plotly_chart(count_bar(filtered, "sleep_score_5", "Distribution of Sleep Health Scores", [0, 1, 2, 3, 4, 5]), use_container_width=True)

    with r2:
        group_data = ordered_count_data(filtered, "sleep_group_5", sleep_group_order)
        fig = px.pie(
            group_data,
            names="sleep_group_5",
            values="count",
            title="Sleep Health Groups",
            hole=0.45,
            category_orders={"sleep_group_5": sleep_group_order},
            color="sleep_group_5",
            color_discrete_map=RISK_COLORS
        )
        fig.update_layout(title_x=0.02, height=420)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Risk Factors")
    st.caption("Objective: Explore how sleep health risk varies across demographic groups.")

    a1, a2 = st.columns(2)
    with a1:
        st.plotly_chart(avg_score_bar(filtered, "age", "Average Sleep Health Score by Age", age_order), use_container_width=True)
    with a2:
        st.plotly_chart(avg_score_bar(filtered, "gender", "Average Sleep Health Score by Gender", gender_order), use_container_width=True)

    a3, a4 = st.columns(2)
    with a3:
        st.plotly_chart(avg_score_bar(filtered, "occupation", "Average Sleep Health Score by Occupation", occupation_order, horizontal=True), use_container_width=True)
    with a4:
        st.plotly_chart(avg_score_bar(filtered, "bmi_category", "Average Sleep Health Score by BMI Category", bmi_order), use_container_width=True)

with tab4:
    st.header("Consequences & Coping")
    st.caption("Objective: Examine how sleep health risk is reflected in daily functioning and coping behaviors.")

    impact_df = filtered.copy()
    impact_df["concentration_grouped"] = impact_df["concentration_diff"].replace({
        "Never": "Low/None",
        "Rarely": "Low/None",
        "Sometimes": "Sometimes",
        "Often": "Frequent",
        "Always": "Frequent",
        "Unknown": "Unknown"
    })

    concentration_order = ["Low/None", "Sometimes", "Frequent", "Unknown"]

    impact = pd.crosstab(
        impact_df["sleep_group_5"],
        impact_df["concentration_grouped"],
        normalize="index"
    ) * 100

    impact = impact.reset_index().melt(
        id_vars="sleep_group_5",
        var_name="Concentration Difficulty",
        value_name="Percent"
    )

    impact["sleep_group_5"] = pd.Categorical(impact["sleep_group_5"], categories=sleep_group_order, ordered=True)
    impact["Concentration Difficulty"] = pd.Categorical(impact["Concentration Difficulty"], categories=concentration_order, ordered=True)
    impact = impact.sort_values(["sleep_group_5", "Concentration Difficulty"])

    fig = px.bar(
        impact,
        x="sleep_group_5",
        y="Percent",
        color="Concentration Difficulty",
        barmode="group",
        title="Concentration Difficulty by Sleep Health Group",
        category_orders={
            "sleep_group_5": sleep_group_order,
            "Concentration Difficulty": concentration_order
        },
        color_discrete_sequence=[COLORS["teal"], COLORS["orange"], COLORS["red"], COLORS["gray"]]
    )
    fig.update_layout(xaxis_title="", yaxis_title="Percent of respondents", title_x=0.02, height=450)
    st.plotly_chart(fig, use_container_width=True)

    high_risk = filtered[filtered["sleep_group_5"] == "High Sleep Risk"]

    st.subheader("Side Effects Among High Sleep Risk Respondents")

    effect_cols = [
        "effect_back_pain",
        "effect_difficulty_concentrating",
        "effect_fatigue",
        "effect_health_issues",
        "effect_mood_swings_irritability",
        "effect_others",
        "effect_professional_work"
    ]

    existing_effect_cols = [c for c in effect_cols if c in high_risk.columns]

    if existing_effect_cols:
        st.plotly_chart(
            horizontal_dummy_bar(
                high_risk,
                existing_effect_cols,
                "Reported Side Effects Among High Sleep Risk Respondents",
                "effect_"
            ),
            use_container_width=True
        )

    st.subheader("Coping Strategies Among High Sleep Risk Respondents")

    coping_cols = [
        "coping_caffeine_stimulants",
        "coping_exercise",
        "coping_naps_during_the_day",
        "coping_others",
        "coping_relaxation_techniques"
    ]

    existing_coping_cols = [c for c in coping_cols if c in high_risk.columns]

    if existing_coping_cols:
        st.plotly_chart(
            horizontal_dummy_bar(
                high_risk,
                existing_coping_cols,
                "Coping Strategies Among High Sleep Risk Respondents",
                "coping_"
            ),
            use_container_width=True
        )

with tab5:
    st.header("Recommendations for Healthcare Stakeholders")
    st.caption("Objective: Provide evidence-informed recommendations based on dashboard findings.")

    st.markdown("""
    1. **Target sleep health education** toward groups with higher average sleep health scores.
    2. **Develop university and workplace awareness programs** addressing late sleeping, concentration difficulty, and fatigue.
    3. **Promote sleep hygiene practices** such as consistent bedtime routines and improved sleeping environments.
    4. **Encourage healthier coping strategies** such as relaxation techniques, structured rest, and exercise.
    5. **Recommend screening or referral** for respondents reporting frequent breathing difficulties, restless legs, or persistent difficulty falling asleep.
    """)
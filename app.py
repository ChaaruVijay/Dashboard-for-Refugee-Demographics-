import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- Page Config ---
st.set_page_config(page_title="Sri Lankan Refugee Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data

def load_data():
    time.sleep(1)
    return pd.read_csv("clean_refugee_data.csv")

with st.spinner("Loading data..."):
    df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/ChaaruVijay/Dashboard-for-Refugee-Demographics-/main/image_3711c2fd4e.jpg", caption="Sri Lankan Diaspora", width=200)
    st.title("The Refugee Footprint")
    page = st.radio("Go to", ["🏠 Home", "📈 Dashboard"])
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/640px-Flag_of_Sri_Lanka.svg.png", width=150)

# --- HOME PAGE ---
if page == "🏠 Home":
    st.title("🌍 Across Borders: The Sri Lankan Refugee Movement")
    st.markdown("---")

    st.subheader("Following their footprints...")
    st.write("""
    This dashboard maps the journeys of Sri Lankan refugees — across borders and through time.
    With data on demographics, destinations, and year-by-year trends, it reveals where they fled,
    who they were, and what patterns emerged.
    """)

    st.markdown(" <br><br>", unsafe_allow_html=True)

    st.subheader("📈 Snapshot Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Years Covered", f"{df['year'].nunique()}")
    with col2:
        st.metric("Unique Destinations", f"{df['asylum_country_name'].nunique()}")
    with col3:
        peak_year = df.groupby("year")["total"].sum().idxmax()
        st.metric("Peak Year", f"{peak_year}")

    st.markdown(" <br><br>", unsafe_allow_html=True)

    st.subheader("📜 Timeline of Key Events Affecting Sri Lankan Refugees")
    st.markdown("""
    - 1983: 📌 Black July Riots — Triggered the beginning of the civil war.
    - 1990: 📌 Escalation of Civil Conflict — Jaffna conflict displaced thousands.
    - 2002: 📌 Ceasefire Agreement — Brief decline in refugee outflows.
    - 2009: 📌 End of Civil War — Sharp change in migration trends.
    - 2019: 📌 Easter Sunday Attacks — Renewed political tension.
    - 2022: 📌 Economic Crisis — Led to a new wave of migration.
    """)

    st.markdown("---")
    st.markdown(
        "> ❝ Refugees are not numbers. They are people who have faces, names, and stories. ❞ – António Guterres"
    )

# --- DASHBOARD PAGE ---
elif page == "📈 Dashboard":
    st.title("📈 Sri Lankan Refugees: Data Dashboard")

    # --- Filters ---
    year_range = st.slider("Select Year Range:", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

    # --- KPIs ---
    st.subheader("📌 Key Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Refugees", f"{int(filtered_df['total'].sum()):,}")
    with col2:
        children = filtered_df['female_children'].sum() + filtered_df['male_children'].sum()
        adults = filtered_df['female_adult'].sum() + filtered_df['male_adult'].sum()
        ratio = children / adults if adults > 0 else 0
        st.metric("Children to Adult Ratio", f"{ratio:.2f}" if adults > 0 else "N/A")
    with col3:
        dest_df = filtered_df[filtered_df['asylum_country_name'].str.lower() != "sri lanka"]
        if not dest_df.empty:
            top_country = dest_df.groupby("asylum_country_name")["total"].sum().idxmax()
            st.metric("Top Destination", top_country)
        else:
            st.metric("Top Destination", "N/A")

    st.markdown("---")

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧬 Demographics", "👫 Gender & Age"])

    # --- Tab 1: Overview ---
    with tab1:
        st.subheader("📊 Total Refugees Over Time")
        yearly = filtered_df.groupby('year')['total'].sum().reset_index()
        fig_line = px.line(yearly, x='year', y='total', markers=True, title="Total Refugees per Year")
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("🌍 Top 10 Asylum Countries")
        top_countries = dest_df.groupby("asylum_country_name")["total"].sum().nlargest(10).reset_index()
        fig_bar = px.bar(top_countries, x="total", y="asylum_country_name", orientation="h", color="total", color_continuous_scale="viridis")
        fig_bar.update_layout(yaxis_categoryorder='total ascending')
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("🌐 Global Refugee Flow Map")
        map_df = dest_df.groupby('asylum_country_name')["total"].sum().reset_index()
        map_df.rename(columns={"asylum_country_name": "country"}, inplace=True)
        fig_map = px.choropleth(map_df, locations="country", locationmode="country names", color="total", color_continuous_scale="Oranges")
        st.plotly_chart(fig_map, use_container_width=True)

    # --- Tab 2: Demographics ---
    with tab2:
        st.subheader("🧬 Population Type Breakdown")
        pop_counts = filtered_df['population_type'].value_counts().reset_index()
        pop_counts.columns = ['Population Type', 'Count']
        fig_demo = px.bar(pop_counts, x='Population Type', y='Count', color='Count', color_continuous_scale='deep')
        st.plotly_chart(fig_demo, use_container_width=True)

    # --- Tab 3: Gender & Age ---
    with tab3:
        st.subheader("👫 Treemap by Gender and Age Group")
        gender_age_cols = ['female_adolescent', 'female_adult', 'female_elderly', 'female_children',
                           'male_adolescent', 'male_adult', 'male_elderly', 'male_children']
        melted_df = df.melt(id_vars=['year'], value_vars=gender_age_cols, var_name='gender_age', value_name='count')
        melted_df['gender'] = melted_df['gender_age'].str.extract(r'^(female|male)')
        melted_df['age_group'] = melted_df['gender_age'].str.extract(r'_(adolescent|adult|elderly|children)')
        melted_df.drop(columns='gender_age', inplace=True)
        fig_treemap = px.treemap(melted_df, path=['year', 'gender', 'age_group'], values='count', color='age_group')
        st.plotly_chart(fig_treemap, use_container_width=True)

        st.subheader("📊 Gender Distribution Over Time")
        gender_df = filtered_df.groupby('year')[['male_total', 'female_total']].sum().reset_index()
        fig_gender = px.bar(gender_df, x='year', y=['male_total', 'female_total'], barmode='stack',
                            labels={"value": "Refugee Count", "variable": "Gender"})
        st.plotly_chart(fig_gender, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("<center>Developed by <b>Charuny Vijayaraj</b> | Module: 5DATA004W | 📅 2025 | Data Source: UNHCR Refugee Database</center>", unsafe_allow_html=True)

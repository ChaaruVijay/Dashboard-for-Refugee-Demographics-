import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- Page Config ---
st.set_page_config(page_title="Sri Lankan Refugee Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    time.sleep(1)  # Simulate delay
    return pd.read_csv("clean_refugee_data.csv")

with st.spinner("Loading data..."):
    df = load_data()
    df['asylum_country_name'] = df['asylum_country_name'].str.lower().str.strip()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/ChaaruVijay/Dashboard-for-Refugee-Demographics-/main/image_3711c2fd4e.jpg", caption="Sri Lankan Diaspora", width=200)
    st.title("The Refugee Footprint")
    page = st.radio("Go to", ["🏠 Home", "📈 Dashboard"])
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/640px-Flag_of_Sri_Lanka.svg.png", width=150)
    st.image("https://raw.githubusercontent.com/ChaaruVijay/Dashboard-for-Refugee-Demographics-/main/MSF223413(High).jpg", caption="Migration Patterns from Sri Lanka", width=200)

# --- HOME PAGE ---
if page == "🏠 Home":
    st.title("🌍 Across Borders: The Sri Lankan Refugee Movement")
    st.markdown("---")
    st.subheader("Following their footprints...")
    st.write("""
    This dashboard maps the journeys of Sri Lankan refugees — across borders and through time.
    With data on demographics, destinations, and year by year trends, it reveals where they fled, who they were, and what patterns emerged.
    Beneath the numbers lie stories of movement shaped by age, gender, politics, and place. Their stories tell about political, economical
    and cultural changes overtime.

    **Developed by Charuny Vijayaraj** | *University of Westminster* | *Module: 5DATA004W*
    """)
    st.markdown("---")

# --- DASHBOARD PAGE ---
elif page == "📈 Dashboard":
    st.title("📈 Sri Lankan Refugees: Data Dashboard")

    # --- Filters ---
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())

    year_range = st.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

    # --- KPIs ---
    st.subheader("📌 Key Stats")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_refugees = filtered_df['total'].sum()
        st.metric("Total Refugees", f"{int(total_refugees):,}")

    with col2:
        total_children = filtered_df['female_children'].sum() + filtered_df['male_children'].sum()
        total_adults = filtered_df['female_adult'].sum() + filtered_df['male_adult'].sum()
        if total_adults > 0:
            ratio = total_children / total_adults
            st.metric("Children to Adult Ratio", f"{ratio:.2f}")
        else:
            st.metric("Children to Adult Ratio", "N/A")

    with col3:
        valid_dest = filtered_df[
            (filtered_df['asylum_country_name'] != "sri lanka") &
            (filtered_df['asylum_country_name'].notna())
        ]
        if not valid_dest.empty:
            top_country = (
                valid_dest
                .groupby("asylum_country_name")["total"]
                .sum()
                .idxmax()
                .title()
            )
            st.metric("Top Destination", top_country)
        else:
            st.metric("Top Destination", "N/A")

    st.markdown("---")

    # --- Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧬 Demographics", "🧒 Age Ratio", "👫 Gender Over Time"])

    # --- Tab 1: Overview ---
    with tab1:
        st.subheader("📊 Total Refugees Over Time")
        df_total = (
            filtered_df.groupby('year')['total']
            .sum()
            .reset_index()
        )

        fig_line = px.line(
            df_total,
            x="year",
            y="total",
            markers=True,
            title="Total Refugees per Year",
            labels={"total": "Refugee Count"},
            color_discrete_sequence=["royalblue"]
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("🌍 Top 10 Asylum Countries")
        top_countries = (
            filtered_df[
                (filtered_df['asylum_country_name'] != "sri lanka") &
                (filtered_df['asylum_country_name'].notna())
            ]
            .groupby("asylum_country_name")["total"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig_bar = px.bar(
            top_countries,
            x="total",
            y="asylum_country_name",
            orientation="h",
            labels={"total": "Refugees", "asylum_country_name": "Country"},
            color="total",
            color_continuous_scale="viridis"
        )
        fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Tab 2: Demographics ---
    with tab2:
        st.subheader("🧬 Population Type Breakdown")
        pop_counts = filtered_df['population_type'].value_counts().reset_index()
        pop_counts.columns = ['Population Type', 'Count']

        fig_demo = px.bar(
            pop_counts,
            x='Population Type',
            y='Count',
            color='Count',
            title="Refugee Population Types",
            color_continuous_scale='deep'
        )
        st.plotly_chart(fig_demo, use_container_width=True)

    # --- Tab 3: Age Ratio ---
    with tab3:
        st.subheader("🧒 Children to Adults Over Time")
        age_df = (
            filtered_df.groupby('year')[['female_children', 'male_children', 'female_adult', 'male_adult']]
            .sum()
            .reset_index()
        )
        age_df['Children'] = age_df['female_children'] + age_df['male_children']
        age_df['Adults'] = age_df['female_adult'] + age_df['male_adult']
        age_df['Ratio'] = age_df['Children'] / age_df['Adults'].replace(0, pd.NA)

        fig_age = px.line(
            age_df,
            x='year',
            y='Ratio',
            title="Children to Adult Ratio (Yearly)",
            markers=True
        )
        st.plotly_chart(fig_age, use_container_width=True)

    # --- Tab 4: Gender Breakdown ---
    with tab4:
        st.subheader("👫 Gender Breakdown Over Time")
        gender_df = (
            filtered_df.groupby('year')[['male_total', 'female_total']]
            .sum()
            .reset_index()
        )

        fig_gender = px.bar(
            gender_df,
            x='year',
            y=['male_total', 'female_total'],
            barmode='stack',
            title="Gender Distribution by Year",
            labels={"value": "Refugee Count", "year": "Year", "variable": "Gender"},
            color_discrete_map={'male_total': '#1f77b4', 'female_total': '#ff69b4'}
        )
        st.plotly_chart(fig_gender, use_container_width=True)


    
# --- Footer ---
st.markdown("---")
st.markdown(
    "<center>Developed by <b>Charuny Vijayaraj</b> | Module: 5DATA004W | 📅 2025 | Data Source: UNHCR Refugee Database</center>",
    unsafe_allow_html=True
)

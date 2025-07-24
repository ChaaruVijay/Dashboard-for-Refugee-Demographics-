import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup page config
st.set_page_config(page_title="Sri Lankan Refugee Dashboard", layout="wide", page_icon="🌍")

# Load data and clean columns
df = pd.read_csv('clean_refugee_data.csv')
df.columns = df.columns.str.strip().str.lower()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Top Asylum Countries", "Demographics"])

# Title
st.title("🌍 Sri Lankan Refugee Data Dashboard")

# Debug columns to make sure all good
# st.write("Columns in dataset:", df.columns.tolist())

# Check year column exists early
if 'year' not in df.columns:
    st.error("❌ No 'year' column found! Check your CSV and column names.")
    st.stop()

# Prepare some common aggregations for reuse
df['total_children'] = df['female_children'] + df['male_children']
df['total_adults'] = df['female_adult'] + df['male_adult']
df_gender = df.groupby('year')[['male_total', 'female_total']].sum()
df_age_ratio = df.groupby('year')[['total_children', 'total_adults']].sum()
df_age_ratio['children_to_adults_ratio'] = df_age_ratio['total_children'] / df_age_ratio['total_adults']

# ----------- PAGE VIEWS -----------

if page == "Overview":
    st.header("📈 Refugees Over Time")
    fig, ax = plt.subplots(figsize=(8, 4))
    df.groupby('year')['total'].sum().plot(kind='line', ax=ax, color='royalblue', marker='o', linewidth=2)
    ax.set_ylabel("Total Refugees")
    ax.set_xlabel("Year")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

elif page == "Top Asylum Countries":
    st.header("🌏 Top 10 Asylum Countries (Excluding Sri Lanka)")
    top_asylum = (
        df[df['asylum_country_name'] != 'sri lanka']
        .groupby('asylum_country_name')['total']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    top_asylum.plot(kind='barh', ax=ax, color='teal')
    ax.set_xlabel("Number of Refugees")
    ax.set_ylabel("Country")
    ax.invert_yaxis()  # best practice for horizontal bars
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)

elif page == "Demographics":
    st.header("👥 Population Type Breakdown")
    fig, ax = plt.subplots(figsize=(6, 4))
    df['population_type'].value_counts().plot(kind='bar', ax=ax, color='coral', edgecolor='black')
    ax.set

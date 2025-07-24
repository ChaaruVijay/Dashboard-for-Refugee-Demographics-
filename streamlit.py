import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset (make sure the CSV path is correct)
df = pd.read_csv(r'C:\Users\USER\Desktop\DSPL ICW\demographics_originating_lka.csv', skiprows=1)

# Rename columns for clarity
df.rename(columns={
    'Year': 'year',
    'Country of Origin Code': 'origin_country_code',
    'Country of Asylum Code': 'asylum_country_code',
    'Country of Origin Name': 'origin_country_name',
    'Country of Asylum Name': 'asylum_country_name',
    'Population Type': 'population_type',
    'location': 'location',
    'urbanRural': 'urban_rural',
    'accommodationType': 'accommodation_type',
    'Female 0-4': 'female_age_0_4',
    'Female 5-11': 'female_age_5_11',
    'Female 12-17': 'female_age_12_17',
    'Female 18-59': 'female_age_18_59',
    'Female 60 or more': 'female_age_60_plus',
    'Female Unknown': 'female_age_unknown',
    'Female Total': 'female_total',
    'Male 0-4': 'male_age_0_4',
    'Male 5-11': 'male_age_5_11',
    'Male 12-17': 'male_age_12_17',
    'Male 18-59': 'male_age_18_59',
    'Male 60 or more': 'male_age_60_plus',
    'Male Unknown': 'male_age_unknown',
    'Male Total': 'male_total',
    'Total': 'total'
}, inplace=True)

if 'origin_country_code' in df.columns:
    df.drop(columns=['origin_country_code'], inplace=True)


# Create new grouped columns for children
df['female_children'] = df['female_age_0_4'] + df['female_age_5_11']
df['male_children'] = df['male_age_0_4'] + df['male_age_5_11']

# Rename other age groups
df.rename(columns={
    'female_age_12_17': 'female_adolescent',
    'male_age_12_17': 'male_adolescent',
    'female_age_18_59': 'female_adult',
    'male_age_18_59': 'male_adult',
    'female_age_60_plus': 'female_elderly',
    'male_age_60_plus': 'male_elderly'
}, inplace=True)

# Drop original children columns
df.drop(columns=['female_age_0_4', 'female_age_5_11', 'male_age_0_4', 'male_age_5_11'], inplace=True)

# Streamlit UI starts here
st.title("Sri Lankan Refugee Data Dashboard")

# Show raw dataframe option
if st.checkbox('Show raw data'):
    st.dataframe(df)

# Plot 1: Refugees Over Time
st.header("Sri Lankan Refugees Over Time")
fig1, ax1 = plt.subplots()
df.groupby('year')['total'].sum().plot(kind='line', ax=ax1)
ax1.set_ylabel('Total Refugees')
ax1.set_xlabel('Year')
st.pyplot(fig1)

# Plot 2: Top 10 Asylum Countries (excluding Sri Lanka)
st.header("Top 10 Asylum Countries")
top_asylum = df[df['asylum_country_name'] != 'Sri Lanka'].groupby('asylum_country_name')['total'].sum().sort_values(ascending=False).head(10)
fig2, ax2 = plt.subplots()
top_asylum.plot(kind='barh', ax=ax2, color='teal')
ax2.set_xlabel('Number of Refugees')
ax2.set_ylabel('Country')
st.pyplot(fig2)

# Plot 3: Population Type Breakdown
st.header("Population Type Breakdown")
fig3, ax3 = plt.subplots()
df['population_type'].value_counts().plot(kind='bar', ax=ax3, color='coral')
ax3.set_ylabel('Count')
st.pyplot(fig3)

# Plot 4: Children to Adult Ratio Over Time
st.header("Children to Adult Ratio Over Time")
df['total_children'] = df['female_children'] + df['male_children']
df['total_adults'] = df['female_adult'] + df['male_adult']
df_age_ratio = df.groupby('year')[['total_children', 'total_adults']].sum()
df_age_ratio['children_to_adults_ratio'] = df_age_ratio['total_children'] / df_age_ratio['total_adults']
fig4, ax4 = plt.subplots()
df_age_ratio['children_to_adults_ratio'].plot(kind='line', marker='o', ax=ax4, color='purple')
ax4.set_ylabel('Ratio')
ax4.set_xlabel('Year')
st.pyplot(fig4)

# Plot 5: Male vs Female Refugees Over Time (stacked)
st.header("Male vs Female Refugees Over Time")
df_gender = df.groupby('year')[['male_total', 'female_total']].sum()
fig5, ax5 = plt.subplots(figsize=(12,6))
df_gender.plot(kind='bar', stacked=True, ax=ax5, color=['#1f77b4', '#ff69b4'])
ax5.set_ylabel('Number of Refugees')
ax5.set_xlabel('Year')
st.pyplot(fig5)

# Plot 6: Female Ratio Over Time
st.header("Female Ratio Over Time")
df_gender_ratio = df_gender.copy()
df_gender_ratio['female_ratio'] = df_gender_ratio['female_total'] / (df_gender_ratio['female_total'] + df_gender_ratio['male_total'])
fig6, ax6 = plt.subplots()
df_gender_ratio['female_ratio'].plot(kind='line', ax=ax6, color='hotpink')
ax6.set_ylabel('Female Ratio')
ax6.set_xlabel('Year')
st.pyplot(fig6)

# Additional demographic visualizations...

st.markdown("### Total Dispersed Population by Gender")
total_female = df['female_total'].sum()
total_male = df['male_total'].sum()
gender_df = pd.DataFrame({
    'Gender': ['Female', 'Male'],
    'Total Dispersed': [total_female, total_male]
})
fig7, ax7 = plt.subplots()
sns.barplot(x='Gender', y='Total Dispersed', data=gender_df, palette='pastel', ax=ax7)
st.pyplot(fig7)

# Age Group totals
st.markdown("### Total Migrated by Age Group")
age_groups = {
    'Children (0-11)': df['female_children'] + df['male_children'],
    'Adolescents (12-17)': df['female_adolescent'] + df['male_adolescent'],
    'Adults (18-59)': df['female_adult'] + df['male_adult'],
    'Elderly (60+)': df['female_elderly'] + df['male_elderly']
}
age_totals = {group: values.sum() for group, values in age_groups.items()}
age_df = pd.DataFrame(list(age_totals.items()), columns=['Age Group', 'Total Migrated'])
fig8, ax8 = plt.subplots()
ax8.bar(age_df['Age Group'], age_df['Total Migrated'], color=['#F7B2B7','#FFD97D','#6BCB77','#4D96FF'])
st.pyplot(fig8)

# Accommodation type distribution
st.markdown("### Gender Distribution by Accommodation Type")
acc_demo = df.groupby('accommodation_type')[['female_total', 'male_total', 'total']].sum().sort_values('total', ascending=False)
fig9, ax9 = plt.subplots(figsize=(10,6))
acc_demo[['female_total', 'male_total']].plot(kind='barh', stacked=True, ax=ax9, colormap='coolwarm')
st.pyplot(fig9)

# Urban vs Rural distribution
st.markdown("### Refugees: Urban vs Rural Origins")
urban_rural_demo = df.groupby('urban_rural')[['female_total', 'male_total', 'total']].sum()
fig10, ax10 = plt.subplots()
urban_rural_demo.plot(kind='bar', stacked=True, colormap='viridis', ax=ax10)
ax10.set_xticklabels(urban_rural_demo.index, rotation=0)
st.pyplot(fig10)

# Families vs Individuals
st.markdown("### Families vs Individuals Seeking Asylum")
df['family_total'] = df['female_children'] + df['male_children'] + df['female_elderly'] + df['male_elderly']
df['adult_total'] = df['female_adult'] + df['male_adult']
fam_vs_ind = df[['family_total', 'adult_total']].sum()
fig11, ax11 = plt.subplots()
fam_vs_ind.plot(kind='bar', color=['#9b59b6', '#3498db'], ax=ax11)
ax11.set_xticklabels(['Families', 'Individuals'], rotation=0)
ax11.set_ylabel('Total Number of People')
st.pyplot(fig11)

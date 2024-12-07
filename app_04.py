##Marketing Campaign Analysis

import streamlit as st  
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from scipy import stats

# Load the data
df = pd.read_csv(r"C:\Users\Lenovo\Desktop\my_projects\marketing.csv")

# Sidebar for selection
st.sidebar.title("Options")
analysis_type = st.sidebar.selectbox("Choose Analysis Type", ["Conversion Rate", "Retention Rate", "A/B Testing"])
quantity = st.sidebar.radio("Select the category quantity", ["One", "Two"])

# Dynamically update category selection based on chosen quantity
if quantity == "One":
    categories = st.sidebar.selectbox("Select category", df.columns.tolist())
elif quantity == "Two":
    categories = st.sidebar.multiselect("Select up to two categories", df.columns.tolist(), max_selections=2)

calculate_button = st.sidebar.button("Calculate")

# Conversion Rate Analysis
if analysis_type == "Conversion Rate" and calculate_button:
    conversion_window = 30
    df['date_served'] = pd.to_datetime(df['date_served'])
    df['date_subscribed'] = pd.to_datetime(df['date_subscribed'])
    df['days_to_subscribe'] = (df['date_subscribed'] - df['date_served']).dt.days
    df['converted_within_window'] = df['days_to_subscribe'].apply(lambda x: x is not None and x <= conversion_window)

    total_served = len(df)
    total_converted = df['converted_within_window'].sum()
    conversion_rate = (total_converted / total_served) * 100

    st.write("### Conversion Rate Results")
    st.write(f"Total served: {total_served}")
    st.write(f"Total converted within {conversion_window} days: {total_converted}")
    st.write(f"Conversion rate: {conversion_rate:.2f}%")

    # Group by selected categories and calculate conversion rate
    if quantity == "One":
        conversion_data = df.groupby(categories).apply(lambda x: pd.Series({
            'Total Exposed': x['date_served'].count(),
            'Total Converted': x['date_subscribed'].count(),
            'Conversion Rate': x['date_subscribed'].count() / x['date_served'].count() if x['date_served'].count() > 0 else 0
        })).reset_index()
        
        # Display table and plot
        st.write(f"### Conversion Rate by {categories}")
        st.dataframe(conversion_data)

        # Plot
        fig, ax = plt.subplots()
        ax.bar(conversion_data[categories], conversion_data['Conversion Rate'], color='skyblue')
        ax.set_title(f"Conversion Rate by {categories}")
        ax.set_ylabel("Conversion Rate (%)")
        st.pyplot(fig)
    elif quantity == "Two" and len(categories) == 2:
        conversion_data = df.groupby(categories).apply(lambda x: pd.Series({
            'Total Exposed': x['date_served'].count(),
            'Total Converted': x['date_subscribed'].count(),
            'Conversion Rate': x['date_subscribed'].count() / x['date_served'].count() if x['date_served'].count() > 0 else 0
        })).reset_index()

        st.write(f"### Conversion Rate by {categories}")
        st.dataframe(conversion_data)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=conversion_data, x=categories[0], y='Conversion Rate', hue=categories[1], ax=ax)
        ax.set_title(f"Conversion Rate by {categories}")
        ax.set_ylabel("Conversion Rate (%)")
        st.pyplot(fig)

# Retention Rate Analysis
elif analysis_type == "Retention Rate" and calculate_button:
    retention_period = 30
    df['date_canceled'] = pd.to_datetime(df['date_canceled'], errors='coerce')
    df['date_subscribed'] = pd.to_datetime(df['date_subscribed'], errors='coerce')
    valid_rows = df.dropna(subset=['date_canceled', 'date_subscribed'])
    valid_rows['retention_days'] = (valid_rows['date_canceled'] - valid_rows['date_subscribed']).dt.days
    valid_rows['retained'] = valid_rows['retention_days'] >= retention_period

    total_users = len(valid_rows)
    retained_users = valid_rows['retained'].sum()
    retention_rate = (retained_users / total_users) * 100 if total_users > 0 else 0

    st.write("### Retention Rate Results")
    st.write(f"Total users: {total_users}")
    st.write(f"Users retained for at least {retention_period} days: {retained_users}")
    st.write(f"Retention rate: {retention_rate:.2f}%")

    # Group by selected categories and calculate retention rate
    if quantity == "One":
        retention_data = valid_rows.groupby(categories).apply(lambda x: pd.Series({
            'Total Exposed': x['date_canceled'].count(),
            'Total Retained': (x['date_canceled'] >= x['date_subscribed'] + pd.Timedelta(days=30)).sum(),
            'Retention Rate': (x['date_canceled'] >= x['date_subscribed'] + pd.Timedelta(days=30)).sum() / x['date_canceled'].count() if x['date_canceled'].count() > 0 else 0
        })).reset_index()

        st.write(f"### Retention Rate by {categories}")
        st.dataframe(retention_data)

        fig, ax = plt.subplots()
        ax.bar(retention_data[categories], retention_data['Retention Rate'], color='teal')
        ax.set_title(f"Retention Rate by {categories}")
        ax.set_ylabel("Retention Rate (%)")
        st.pyplot(fig)
    elif quantity == "Two" and len(categories) == 2:
        retention_data = valid_rows.groupby(categories).apply(lambda x: pd.Series({
            'Total Exposed': x['date_canceled'].count(),
            'Total Retained': (x['date_canceled'] >= x['date_subscribed'] + pd.Timedelta(days=30)).sum(),
            'Retention Rate': (x['date_canceled'] >= x['date_subscribed'] + pd.Timedelta(days=30)).sum() / x['date_canceled'].count() if x['date_canceled'].count() > 0 else 0
        })).reset_index()

        st.write(f"### Retention Rate by {categories}")
        st.dataframe(retention_data)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=retention_data, x=categories[0], y='Retention Rate', hue=categories[1], ax=ax)
        ax.set_title(f"Retention Rate by {categories}")
        ax.set_ylabel("Retention Rate (%)")
        st.pyplot(fig)

        
    # A/B Testing Analysis
# elif analysis_type == "A/B Testing" and calculate_button:
#     group_a = df[df['variant'] == 'personalization'].copy()
#     group_b = df[df['variant'] == 'control'].copy()
#     group_a['converted'] = pd.to_numeric(group_a['converted'], errors='coerce')
#     group_b['converted'] = pd.to_numeric(group_b['converted'], errors='coerce')
#     group_a['is_retained'] = pd.to_numeric(group_a['is_retained'], errors='coerce')
#     group_b['is_retained'] = pd.to_numeric(group_b['is_retained'], errors='coerce')
#     group_a = group_a.dropna(subset=['converted', 'is_retained'])
#     group_b = group_b.dropna(subset=['converted', 'is_retained'])

#     conversion_rate_a = group_a['converted'].mean()
#     conversion_rate_b = group_b['converted'].mean()
#     retention_rate_a = group_a['is_retained'].mean()
#     retention_rate_b = group_b['is_retained'].mean()

#     t_stat_conversion, p_val_conversion = stats.ttest_ind(group_a['converted'], group_b['converted'])
#     t_stat_retention, p_val_retention = stats.ttest_ind(group_a['is_retained'], group_b['is_retained'])

#     st.write("### A/B Testing Results")
#     st.write(f"Conversion Rate (Personalization): {conversion_rate_a:.2%}")
#     st.write(f"Conversion Rate (Control): {conversion_rate_b:.2%}")
#     st.write(f"T-statistic (Conversion Rate): {t_stat_conversion:.4f}, P-value: {p_val_conversion:.4f}")
#     st.write(f"Retention Rate (Personalization): {retention_rate_a:.2%}")
#     st.write(f"Retention Rate (Control): {retention_rate_b:.2%}")
#     st.write(f"T-statistic (Retention Rate): {t_stat_retention:.4f}, P-value: {p_val_retention:.4f}")


# A/B Testing Analysis
elif analysis_type == "A/B Testing" and calculate_button:
    group_a = df[df['variant'] == 'personalization'].copy()
    group_b = df[df['variant'] == 'control'].copy()

    # Convert boolean columns to numeric
    group_a['converted'] = pd.to_numeric(group_a['converted'], errors='coerce').astype(float)
    group_b['converted'] = pd.to_numeric(group_b['converted'], errors='coerce').astype(float)
    group_a['is_retained'] = pd.to_numeric(group_a['is_retained'], errors='coerce').astype(float)
    group_b['is_retained'] = pd.to_numeric(group_b['is_retained'], errors='coerce').astype(float)

    group_a = group_a.dropna(subset=['converted', 'is_retained'])
    group_b = group_b.dropna(subset=['converted', 'is_retained'])

    conversion_rate_a = group_a['converted'].mean()
    conversion_rate_b = group_b['converted'].mean()
    retention_rate_a = group_a['is_retained'].mean()
    retention_rate_b = group_b['is_retained'].mean()

    t_stat_conversion, p_val_conversion = stats.ttest_ind(group_a['converted'], group_b['converted'])
    t_stat_retention, p_val_retention = stats.ttest_ind(group_a['is_retained'], group_b['is_retained'])

    st.write("### A/B Testing Results")
    st.write(f"Conversion Rate (Personalization): {conversion_rate_a:.2%}")
    st.write(f"Conversion Rate (Control): {conversion_rate_b:.2%}")
    st.write(f"T-statistic (Conversion Rate): {t_stat_conversion:.4f}, P-value: {p_val_conversion:.4f}")
    st.write(f"Retention Rate (Personalization): {retention_rate_a:.2%}")
    st.write(f"Retention Rate (Control): {retention_rate_b:.2%}")
    st.write(f"T-statistic (Retention Rate): {t_stat_retention:.4f}, P-value: {p_val_retention:.4f}")




    # Plot
    if quantity == "One":
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        sns.barplot(x=['Personalization', 'Control'], y=[conversion_rate_a, conversion_rate_b], ax=axes[0], palette=['seagreen', 'tomato'])
        axes[0].set_title("Conversion Rates")
        axes[0].set_ylabel("Conversion Rate")
        
        sns.barplot(x=['Personalization', 'Control'], y=[retention_rate_a, retention_rate_b], ax=axes[1], palette=['seagreen', 'tomato'])
        axes[1].set_title("Retention Rates")
        axes[1].set_ylabel("Retention Rate")
        
        st.pyplot(fig)

    elif quantity == "Two" and len(categories) == 2:
        # Group by both selected categories
        ab_test_data = df.groupby(categories + ['variant']).apply(lambda x: pd.Series({
            'Conversion Rate': x['converted'].mean(),
            'Retention Rate': x['is_retained'].mean()
        })).reset_index()

        st.write(f"### A/B Testing by {categories}")
        st.dataframe(ab_test_data)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        sns.barplot(data=ab_test_data, x=categories[0], y='Conversion Rate', hue=categories[1], ci=None, ax=axes[0])
        axes[0].set_title(f"Conversion Rate by {categories}")
        axes[0].set_ylabel("Conversion Rate (%)")
        
        sns.barplot(data=ab_test_data, x=categories[0], y='Retention Rate', hue=categories[1], ci=None, ax=axes[1])
        axes[1].set_title(f"Retention Rate by {categories}")
        axes[1].set_ylabel("Retention Rate (%)")

        st.pyplot(fig)
    



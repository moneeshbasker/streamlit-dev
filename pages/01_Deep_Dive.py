import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
import streamlit as st

# st.markdown("""
# <style>
# .css-nqowgj.e1ewe7hr3
# {
#     visibility: hidden;
# }
# .css-h5rgaw.e1g8pov61
# {
#     visibility: hidden;
# }
# </style>
# """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Deep Dive</h1>", unsafe_allow_html=True)

table = pq.read_table(r'Input_Sales_Data_v2.parquet')
df = table.to_pandas()
st.write('---')

# Set up the layout using Streamlit columns
col1, col2, col3 = st.columns([1, 1, 1])

# Create select boxes for category, manufacturer, and brand in the second row
with col1:
    selected_category = st.selectbox('Category', df['Category'].unique())
with col2:
    selected_manufacturer = st.selectbox('Manufacturer', df['Manufacturer'].unique())
with col3:
    selected_brand = st.selectbox('Brand', df['Brand'].unique())

# Filter the DataFrame based on the selected values
filtered_df = df[(df['Category'] == selected_category) &
                 (df['Manufacturer'] == selected_manufacturer) &
                 (df['Brand'] == selected_brand)]

# Remove duplicate values in the 'Date' column
filtered_df = filtered_df[~filtered_df['Date'].duplicated()]

# Convert 'Date' column to datetime and set it as the index
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
filtered_df.set_index('Date', inplace=True)

# Calculate YTD volume sales, YTD $ sales, YTD Market share, and #SKUs
ytd_volume_sales = filtered_df['Volume'].sum()
ytd_sales = filtered_df['Value'].sum()
ytd_market_share = ytd_sales / df['Value'].sum()
num_skus = filtered_df['SKU Name'].nunique()

# Display YTD statistics
st.write('---')
col5, col6, col7, col8 = st.columns([1, 1, 1, 1])
with col5:
    st.metric("YTD Volume Sales", f"{ytd_volume_sales:,}")
with col6:
    st.metric("YTD $ Sales", f"${ytd_sales:,.2f}")
with col7:
    st.metric("YTD Market Share", f"{ytd_market_share:.2%}")
with col8:
    st.metric("# SKUs", num_skus)

st.write('---')

# Set up the layout for plots using Streamlit columns
col9, col10 = st.columns(2)
col11, col12 = st.columns(2)

# Weekly Volume Sales and Value Sales Line Chart
with col9:
    st.subheader('Weekly Volume Sales and Value Sales')
    weekly_sales = filtered_df.resample('W-Mon').sum()
    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Volume', color='blue', ax=ax1, label='Volume Sales')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume Sales')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Value', color='red', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='red')
    ax2.tick_params('y', colors='red')


    plt.title('Weekly Volume Sales and Value Sales for Selected SKUs')
    plt.xticks(rotation=45)
    st.pyplot(fig)


# Pie Chart - Percentage of Value Sales of Top 10 SKUs within the Brand
with col10:
    st.subheader('Percentage of Value Sales of Top 10 SKUs within the Brand')
    top_10_sku_sales = filtered_df.groupby('SKU Name')['Value'].sum().nlargest(10)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(top_10_sku_sales, labels=top_10_sku_sales.index, autopct='%1.1f%%')
    plt.title('Percentage of Value Sales of Top 10 SKUs within the Brand')
    plt.xticks(rotation=45)
    st.pyplot(fig)



st.write('---')

# Trend Line - Price and Volume Sales
with col11:
    st.subheader('Trend Line - Price and Volume Sales')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Price', color='blue', ax=ax1, label='Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Volume', color='red', ax=ax2, label='Volume Sales')
    ax2.set_ylabel('Volume Sales', color='red')
    ax2.tick_params('y', colors='red')

    plt.title('Trend Line - Price and Volume Sales')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Trend Line - Price and Value Sales
with col12:
    st.subheader('Trend Line - Price and Value Sales')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Price', color='blue', ax=ax1, label='Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Value', color='red', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='red')
    ax2.tick_params('y', colors='red')

    plt.title('Trend Line - Price and Value Sales')
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.markdown("<h1 style='text-align: center;'>SKU Multi Select</h1>", unsafe_allow_html=True)

# Multiselect SKU Block
selected_skus = st.multiselect('Select SKUs', filtered_df['SKU Name'].unique())

# Filter the DataFrame based on selected SKUs
filtered_skus_df = filtered_df[filtered_df['SKU Name'].isin(selected_skus)]

# Calculate average $ value sales per month for selected SKUs
average_value_sales_per_month = filtered_skus_df.resample('M').mean()['Value']

# Set up the layout for the line chart and bar chart using Streamlit columns
col13, col14 = st.columns(2)

# Line chart - Weekly Volume Sales and Value Sales for Selected SKUs
with col13:
    st.subheader('Weekly Volume Sales and Value Sales for Selected SKUs')
    weekly_sales = filtered_skus_df.resample('W-Mon').sum()
    fig, ax1 = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Volume', color='blue', ax=ax1, label='Volume Sales')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume Sales')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Value', color='red', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='red')
    ax2.tick_params('y', colors='red')


    plt.title('Weekly Volume Sales and Value Sales for Selected SKUs')
    plt.xticks(rotation=45)
    st.pyplot(fig)


# Bar chart - Average $ Value Sales per Month for Selected SKUs
with col14:
    st.subheader('Average $ Value Sales per Month for Selected SKUs')
    fig, ax = plt.subplots(figsize=(10, 6))
    average_value_sales_per_month = filtered_skus_df.resample('M').mean()['Value']
    month_labels = average_value_sales_per_month.index.strftime('%b %Y')
    ax.bar(range(len(average_value_sales_per_month)), average_value_sales_per_month, color='green')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average $ Value Sales')
    ax.set_xticks(range(len(average_value_sales_per_month)))
    ax.set_xticklabels(month_labels, rotation=45)
    plt.title('Average $ Value Sales per Month for Selected SKUs')
    st.pyplot(fig)


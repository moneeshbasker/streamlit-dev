import warnings

import matplotlib.colors as colors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
import streamlit as st

# import streamlit.components.v1 as components
from matplotlib.cbook import boxplot_stats

warnings.filterwarnings("ignore")

# Set the Streamlit app layout
st.set_page_config(layout="wide")

# Set the CSS style to position the logo at the top of the sidebar
# st.markdown("""
# <style>
# .css-nqowgj.e1ewe7hr3 {
#     visibility: hidden;
# }
# .css-h5rgaw.e1g8pov61 {
#     visibility: hidden;
# }
# </style>
# """, unsafe_allow_html=True)

# Load the logo image
logo_image = "tiger_logo.png"

st.sidebar.image(logo_image, use_column_width=True)
st.sidebar.markdown("---")

table = pq.read_table('Input_Sales_Data_v2.parquet')
df = table.to_pandas()

# Convert the 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# Set the color palette
colors = sns.color_palette("colorblind")

# Set the Streamlit app title
# st.title("SALES ANALYSIS")
st.markdown("<h1 style='text-align: center;'>SALES ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown("---")

# Get the minimum and maximum dates from the dataframe
min_date = df['Date'].min().to_pydatetime()
max_date = df['Date'].max().to_pydatetime()

# Set up the layout using Streamlit columns
col1, col2 = st.columns(2)

# Define the date range slider in the first column
with col1:
    st.subheader("Date Range Selection")
    selected_dates = st.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# Define the category selection dropdown in the second column
with col2:
    st.subheader("Category Selection")
    selected_category = st.selectbox("Select Category", df['Category'].unique())

st.markdown("---")

# Filter the dataframe based on the selected date range and category
filtered_df = df[(df['Date'] >= pd.to_datetime(selected_dates[0])) & (df['Date'] <= pd.to_datetime(selected_dates[1])) & (df['Category'] == selected_category)]



# Sort the dataframe by Value Sales in descending order
sorted_df = filtered_df.sort_values(by='Value', ascending=False)

# Display the total volume and value sales at the manufacturer level
manufacturer_sales = sorted_df.groupby('Manufacturer')[['Volume', 'Value']].sum().sort_values(by='Value', ascending=False)

# Calculate market share based on value
total_value = manufacturer_sales['Value'].sum()
manufacturer_sales['Market Share'] = (manufacturer_sales['Value'] / total_value) * 100
manufacturer_sales.rename(columns={"Volume":"Total Sales Volume","Value":"Total Sales Value"}, inplace=True)
manufacturer_sales = manufacturer_sales.style.format({
    'Total Sales Volume': '{:,.0f}',
    'Total Sales Value': '{:,.0f}',
    'Total Market Share': '{:.2f}%'
})

cmap = sns.color_palette("crest_r", as_cmap=True)
background_gradient = manufacturer_sales.background_gradient(subset=['Market Share'], cmap=cmap)

st.dataframe(manufacturer_sales, width=800)
st.markdown("---")


# Get the top 5 manufacturers for the selected period
top_manufacturers = sorted_df.groupby('Manufacturer')['Value'].sum().nlargest(5).index.tolist()

# Group the data by manufacturer and date to calculate the total sales over time
manufacturer_sales = sorted_df.groupby(['Manufacturer', 'Date'], as_index=False)['Value'].sum()

# Sort each manufacturer's data by date in ascending order
sorted_manufacturer_sales = manufacturer_sales.groupby('Manufacturer', group_keys=False).apply(lambda x: x.sort_values('Date')).reset_index(drop=True)

# Create a checkbox for removing outliers
remove_outliers = st.sidebar.checkbox("Remove Outliers")
st.sidebar.markdown("---")

# Create a line plot for each manufacturer
plt.figure(figsize=(12, 8))
for manufacturer in top_manufacturers:
    manufacturer_data = sorted_manufacturer_sales[sorted_manufacturer_sales['Manufacturer'] == manufacturer]

    # Check if removing outliers is enabled
    if remove_outliers:
        # Calculate the outlier threshold
        stats = boxplot_stats(manufacturer_data['Value'])
        threshold = stats[0]['whishi']

        # Filter out outlier points
        manufacturer_data = manufacturer_data[manufacturer_data['Value'] <= threshold]

    # Plot the filtered data
    plt.plot(manufacturer_data['Date'], manufacturer_data['Value'], label=manufacturer)

# Set the x-axis label
plt.xlabel('Date')

# Format the x-axis tick labels as months
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

# Rotate the x-axis tick labels for better readability
plt.xticks(rotation=45)

# Set the y-axis label
plt.ylabel('Value Sales')

# Set the plot title
plt.title('Top 5 Manufacturers Sales Trends')

# Move the legend outside the plot
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

# Display the plot
st.pyplot(plt)


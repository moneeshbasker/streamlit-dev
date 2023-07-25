import pickle
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_authenticator import Authenticate

st.set_page_config(page_title="Bacardi Demand Forecasting", page_icon=":bar_chart:", layout="wide")

names = ["Moneesh B", "Komal"]
usernames = ["moneesh", "komal"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {
    'usernames': {username: {'name': name, 'password': hashed_password} for username, name, hashed_password in zip(usernames, names, hashed_passwords)}
}

cookie_name = "dashboard"
cookie_key = "abcdef"

authenticator = Authenticate(credentials, cookie_name, cookie_key, cookie_expiry_days=0)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")


if authentication_status:
    css = """
    <style>
    h1 {
        color: black;
        text-align: center;
        background-color: red;
        padding: 10px;
        border-radius: 10px; /* Rounded corners */
    }
    h2 { color: black; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    def set_custom_css():
        st.markdown(css, unsafe_allow_html=True)

    def render_custom_title(title):
        st.markdown("<h1>{}</h1>".format(title), unsafe_allow_html=True)

    @st.cache_data
    def data_upload():
        df = pd.read_csv("scenarios.csv")
        return df

    df = data_upload()
    cols = ["Name", "Created Date", "Created by", "revenue", "cost", "profit"]
    df = df[cols]

    set_custom_css()

    render_custom_title("Bacardi Demand Forecasting")

    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)

    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gridoptions = gd.build()
    grid_return = AgGrid(df,
                        gridOptions=gridoptions,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        height=300,
                        allow_unsafe_jscode=True,
                        theme='streamlit')

    selected_rows = grid_return["selected_rows"]

    if selected_rows:
        new_df = pd.DataFrame(selected_rows)

        columns_to_select = ["Name", "revenue", "cost", "profit"]
        new_df = new_df[columns_to_select]

        numeric_columns = ["revenue", "cost", "profit"]
        new_df[numeric_columns] = new_df[numeric_columns].apply(pd.to_numeric)

        melted_df = new_df.melt(id_vars="Name", value_vars=numeric_columns, var_name="Category", value_name="Amount")

        st.markdown("Comparison of Selected Scenarios")

        fig = go.Figure()
        for category in numeric_columns:
            fig.add_trace(go.Bar(
                x=melted_df['Name'],
                y=melted_df['Amount'][melted_df['Category'] == category],
                name=category
            ))

        fig.update_layout(
            xaxis_title="Name",
            yaxis_title="Amount",
            title="Scenario Comparison",
            barmode='group',
            xaxis_tickangle=-45,
            autosize=True,
        )

        st.plotly_chart(fig)
    else:
        st.write("Please select rows in the table above to display the plot.")

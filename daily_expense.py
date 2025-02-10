import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Define the file name
FILE_NAME = "daily_expenses.xlsx"
LIMIT_FILE = "expense_limit.txt"

def load_data():
    """Load expense data from an Excel file or create an empty DataFrame if file doesn't exist."""
    if os.path.exists(FILE_NAME):
        return pd.read_excel(FILE_NAME)
    else:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Notes"])

def save_data(df):
    """Save the DataFrame to an Excel file."""
    df.to_excel(FILE_NAME, index=False)

def load_limit():
    """Load the monthly expense limit from a file."""
    if os.path.exists(LIMIT_FILE):
        with open(LIMIT_FILE, "r") as file:
            return float(file.read().strip())
    return 0.0

def save_limit(limit):
    """Save the monthly expense limit to a file."""
    with open(LIMIT_FILE, "w") as file:
        file.write(str(limit))

def calculate_remaining_limit():
    """Calculate the remaining limit for the month."""
    df = load_data()
    df["Date"] = pd.to_datetime(df["Date"])
    current_month = datetime.today().month
    monthly_expense = df[df["Date"].dt.month == current_month]["Amount"].sum()
    return load_limit() - monthly_expense

# Streamlit UI
st.title("Daily Expense Tracker")

# Set Monthly Expense Limit
st.sidebar.header("Set Monthly Expense Limit")
monthly_limit = st.sidebar.number_input("Enter Monthly Limit (₹)", min_value=0.0, value=load_limit(), format="%.2f")
if st.sidebar.button("Save Limit"):
    save_limit(monthly_limit)
    st.sidebar.success("Monthly limit saved successfully!")

remaining_limit = calculate_remaining_limit()
st.sidebar.metric("Remaining Limit (₹)", f"{remaining_limit:.2f}")

# Tabs for entering and viewing expenses
tab1, tab2 = st.tabs(["Enter Expense", "View Expenses"])

with tab1:
    st.header("Add New Expense")
    
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food", "Transport", "Bills", "Shopping", "Miscellaneous"])
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    notes = st.text_area("Notes (Optional)")
    
    if st.button("Save Expense"):
        df = load_data()
        new_entry = pd.DataFrame([[date, category, amount, notes]], columns=["Date", "Category", "Amount", "Notes"])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.success("Expense saved successfully!")
        st.rerun()

with tab2:
    st.header("Daily Expenses")
    df = load_data()
    
    # Filter by date range
    start_date = st.date_input("Start Date", df["Date"].min() if not df.empty else datetime.today())
    end_date = st.date_input("End Date", df["Date"].max() if not df.empty else datetime.today())
    
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        filtered_df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))]
        
        st.dataframe(filtered_df)
        
        # Download filtered data
        if st.button("Download as Excel"):
            filtered_df.to_excel("filtered_expenses.xlsx", index=False)
            with open("filtered_expenses.xlsx", "rb") as file:
                st.download_button(label="Download Excel", data=file, file_name="filtered_expenses.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No expenses recorded yet.")

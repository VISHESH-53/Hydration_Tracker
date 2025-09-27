import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import random

# --- App Configuration ---
st.set_page_config(
    page_title="Hydration Helper",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Storage ---
DATA_FILE = "water_intake_log.csv"

def load_data():
    """Load water intake data from a CSV file. If the file doesn't exist, create it."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Amount (ml)"])
        df.to_csv(DATA_FILE, index=False)
        return df
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Timestamp"])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["Timestamp", "Amount (ml)"])

def save_data(df):
    """Save the DataFrame to the CSV file."""
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# --- Hydration Tips ---
TIPS = [
    "Carry a reusable water bottle with you throughout the day.",
    "Feeling tired? You might just be dehydrated. Drink a glass of water.",
    "Set reminders on your phone to drink water every hour.",
    "Drink a glass of water before every meal.",
    "Add a slice of lemon or cucumber to your water for a refreshing taste.",
    "Keep a large bottle of water on your desk while studying.",
    "If you exercise, remember to drink water before, during, and after your workout.",
    "Don't wait until you're thirsty. Sip water steadily throughout the day.",
]

# --- Main App ---

# Load data at the start
log_df = load_data()

# --- Sidebar ---
st.sidebar.title("Hydration Helper 💧")
st.sidebar.markdown("Your personal assistant to stay hydrated and healthy.")

# Sidebar: Set Daily Goal
st.sidebar.header("Set Your Goal")
daily_goal = st.sidebar.number_input(
    "Your Daily Water Goal (in ml):",
    min_value=500,
    max_value=10000,
    value=2500,  # Default goal
    step=100,
    help="A common recommendation is around 2-3 liters (2000-3000 ml) per day."
)

# Sidebar: Log Water Intake
st.sidebar.header("Log Your Water Intake")
amount_to_add = st.sidebar.number_input(
    "Enter amount (in ml):",
    min_value=50,
    max_value=2000,
    step=50,
    key="water_amount_input"
)

if st.sidebar.button("Log Water 💧", use_container_width=True):
    if amount_to_add > 0:
        # Create a new entry
        new_entry = pd.DataFrame({
            "Timestamp": [datetime.now()],
            "Amount (ml)": [amount_to_add]
        })
        # Append to the main dataframe
        log_df = pd.concat([log_df, new_entry], ignore_index=True)
        # Save the updated data
        save_data(log_df)
        st.sidebar.success(f"Successfully logged {amount_to_add} ml of water!")
        # Clear the input box by rerunning the script
        st.rerun()
    else:
        st.sidebar.warning("Please enter a positive amount.")


# --- Main Dashboard ---
st.title("🌊 Your Hydration Dashboard")
st.markdown("Track your progress, visualize your habits, and get tips to stay on top of your hydration game!")

# Filter data for today
today = date.today()
today_df = log_df[log_df["Timestamp"].dt.date == today]
total_today = today_df["Amount (ml)"].sum()
progress_percent = (total_today / daily_goal) * 100 if daily_goal > 0 else 0

# --- Key Metrics and Progress Bar ---
st.header(f"Today's Progress ({today.strftime('%B %d, %Y')})")
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Total Water Consumed Today",
        value=f"{int(total_today)} ml",
        delta=f"{int(daily_goal - total_today)} ml remaining" if total_today < daily_goal else "Goal Achieved! 🎉"
    )

with col2:
    st.metric(
        label="Daily Goal",
        value=f"{int(daily_goal)} ml"
    )

# Progress Bar
st.progress(min(1.0, progress_percent / 100))
if progress_percent >= 100:
    st.success("Congratulations! You've reached your daily hydration goal. Keep it up!")
else:
    st.info(f"You are at {progress_percent:.0f}% of your daily goal.")

st.markdown("---") # Visual separator

# --- Visualizations ---
col_charts1, col_charts2 = st.columns(2)

with col_charts1:
    # Daily Intake Visualization (using st.bar_chart)
    st.subheader("Today's Intake Log")
    if not today_df.empty:
        # Prepare data for st.bar_chart
        today_df_copy = today_df.copy()
        today_df_copy['Time'] = today_df_copy['Timestamp'].dt.strftime('%I:%M %p')
        chart_data = today_df_copy.set_index('Time')[['Amount (ml)']]
        
        st.bar_chart(chart_data)
    else:
        st.info("No water logged yet for today. Let's get started!")

with col_charts2:
    # Weekly Progress Visualization (using st.bar_chart)
    st.subheader("Your Weekly Progress")
    if not log_df.empty:
        # Group by date
        log_df['Date'] = log_df['Timestamp'].dt.date
        weekly_summary = log_df.groupby('Date')['Amount (ml)'].sum().reset_index()
        
        # Ensure all of the last 7 days are present
        last_7_days = pd.to_datetime(pd.date_range(end=today, periods=7)).date
        weekly_df = pd.DataFrame({'Date': last_7_days}).merge(weekly_summary, on='Date', how='left').fillna(0)
        
        weekly_df['Day'] = pd.to_datetime(weekly_df['Date']).dt.strftime('%a, %b %d')
        chart_data_weekly = weekly_df.set_index('Day')[['Amount (ml)']]

        st.bar_chart(chart_data_weekly)
        st.caption(f"A red line on the chart would indicate your daily goal of {daily_goal} ml.")

    else:
        st.info("Log some water to see your weekly progress chart.")

st.markdown("---")

# --- Hydration Tip of the Day ---
st.subheader("💡 Hydration Tip of the Day")
tip_of_the_day = random.choice(TIPS)
st.info(f"**Tip:** {tip_of_the_day}")

# --- View Raw Data ---
with st.expander("View Full Water Intake Log"):
    if not log_df.empty:
        st.dataframe(log_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    else:
        st.write("Your log is empty.")


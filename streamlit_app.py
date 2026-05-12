import streamlit as st
import threading
import logging
from monitoring.metrics import MetricsPlugin
from plugins.stop_loss import StopLossPlugin
from plugins.notifier import EmailNotifier, SlackNotifier

# Configure logging
logging.basicConfig(filename="trading_bot.log", level=logging.INFO)

# Initialize session state safely
if "positions" not in st.session_state:
    st.session_state["positions"] = []
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "trading_active" not in st.session_state:
    st.session_state["trading_active"] = False

# Risk plugins
stop_loss = StopLossPlugin(threshold=0.05)  # FIXED: closed parenthesis
metrics = MetricsPlugin()

# Notifiers
email_notifier = EmailNotifier()
slack_notifier = SlackNotifier()

def trading_loop():
    while st.session_state["trading_active"]:
        try:
            # Simulated trade execution
            trade = {"price": 100, "qty": 1}
            st.session_state["positions"].append(trade)
            logging.info(f"Executed trade: {trade}")

            # Risk management
            stop_loss.check(trade)
            metrics.record_trade(trade)

            # Notifications
            email_notifier.notify("Trade executed", trade)
            slack_notifier.notify("Trade executed", trade)

        except Exception as e:
            logging.error(f"Error in trading loop: {e}")
            st.session_state["last_result"] = str(e)

def dashboard_tab():
    st.title("Trading Bot Dashboard")
    st.write("Live trading loop with metrics and risk management.")

    if st.button("Start Trading"):
        st.session_state["trading_active"] = True
        threading.Thread(target=trading_loop, daemon=True).start()

    if st.button("Stop Trading"):
        st.session_state["trading_active"] = False

    st.write("Positions:", st.session_state["positions"])
    st.write("Last Result:", st.session_state["last_result"])

def strategy_tab():
    st.title("Strategy Config")
    st.write("This tab will later support strategy plugins, parameters, and model selection.")

def logs_tab():
    st.title("Logs")
    with open("trading_bot.log", "r") as f:
        st.text(f.read())

def model_testing_tab():
    st.title("Model Testing")
    st.write("Placeholder for model backtesting and evaluation.")

def debug_tab():
    st.title("Debug")
    st.write("Session State:", st.session_state)

def main():
    st.sidebar.title("Navigation")
    tab = st.sidebar.radio("Go to", ["Dashboard", "Strategy Config", "Logs", "Model Testing", "Debug"])

    if tab == "Dashboard":
        dashboard_tab()
    elif tab == "Strategy Config":
        strategy_tab()
    elif tab == "Logs":
        logs_tab()
    elif tab == "Model Testing":
        model_testing_tab()
    elif tab == "Debug":
        debug_tab()

if __name__ == "__main__":
    main()

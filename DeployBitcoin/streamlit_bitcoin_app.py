import streamlit as st
import requests
import urllib.parse

# --- App Configuration ---
APP_TITLE = "💰 Crypto Insights: Price & News"
BASE_API_URL = "http://127.0.0.1:8084"
TEAM_NAME = "CryptoNewsAndPrice"
GPT4O_API_KEY = "YOUR_API_KEY_HERE"

# --- Streamlit UI Setup ---
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)

st.markdown("""
Stay updated on your favorite cryptocurrency!  
Enter a crypto name like `bitcoin`, `ethereum`, or `solana`, and our AI team will fetch:
- 💹 Real-time price metrics  
- 📰 Latest crypto news  
""")

# Session state
if 'api_result' not in st.session_state:
    st.session_state.api_result = None
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'show_full_response' not in st.session_state:
    st.session_state.show_full_response = False

# --- Input ---
crypto_name = st.text_input("Enter cryptocurrency name (e.g., bitcoin):", "")

if st.button("🚀 Fetch Insights"):
    if not crypto_name.strip():
        st.warning("Please enter a valid cryptocurrency name.")
    else:
        st.session_state.is_generating = True
        st.session_state.api_result = None
        try:
            with st.spinner("Gathering crypto data from the AI team..."):
                encoded_task = urllib.parse.quote(crypto_name.strip())
                request_url = f"{BASE_API_URL}/predict/{encoded_task}"


                # Add the hardcoded API key in the header
                headers = {
                    "Authorization": f"Bearer {GPT4O_API_KEY}"
                }

                response = requests.get(request_url, headers=headers, timeout=90)
                response.raise_for_status()
                st.session_state.api_result = response.json()
                st.success("✅ Data fetched successfully!")
        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Could not reach the API. Details: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
        finally:
            st.session_state.is_generating = False

# --- Display Result ---
import json
from datetime import datetime

# Extract messages
api_result = st.session_state.api_result
if api_result and api_result.get("status") is True:
    messages = api_result.get("data", {}).get("task_result", {}).get("messages", [])

    # Initialize
    price_data = {}
    news_items = []

    # Parse messages
    for msg in messages:
        source = msg.get("source", "")
        msg_type = msg.get("type", "")
        content = msg.get("content", "")

        # Handle price summary
        if source == "price_retriever" and msg_type == "ToolCallSummaryMessage":
            if isinstance(content, str):
                try:
                    price_data = eval(content)
                except Exception as e:
                    st.warning(f"❗ Failed to parse price data: {e}")

        # Handle news results
        elif source == "news_retriever" and msg_type == "ToolCallExecutionEvent":
            if isinstance(content, list) and len(content) > 0:
                raw_news = content[0].get("content")
                if isinstance(raw_news, str):
                    try:
                        parsed_news = eval(raw_news)
                        if isinstance(parsed_news, list):
                            news_items.extend(parsed_news)
                    except Exception as e:
                        st.warning(f"❗ Failed to parse news data: {e}")

    # --- Display Results ---

    if price_data:
        st.subheader("📈 Bitcoin Price Metrics")
        for key, val in price_data.items():
            if key == "last_updated_at":
                try:
                    val = datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            st.markdown(f"- **{key.replace('_', ' ').title()}**: {val}")

    if news_items:
        st.subheader("📰 Latest Bitcoin News")
        for item in news_items:
            title = item.get("title", "Untitled")
            desc = item.get("description", "")
            published = item.get("published_at", "")
            url = item.get("url") or "#"

            st.markdown(f"**{title}**  \n"
                        f"{desc}  \n"
                        f"*Published:* `{published}`  \n"
                        f"{'[Link]' if url != '#' else ''} {f'({url})' if url != '#' else ''}")
            st.markdown("---")

    # Optional: Show full response
    if st.button("🔎 Show/Hide Full JSON Response"):
        st.session_state.show_full_response = not st.session_state.show_full_response
    if st.session_state.show_full_response:
        st.caption("Full API response:")
        st.json(api_result)

elif api_result:
    st.error("⚠️ Failed to retrieve valid data. Please try again or check input.")

    if st.button("🔎 Show/Hide Full JSON Response"):
        st.session_state.show_full_response = not st.session_state.show_full_response
    if st.session_state.show_full_response:
        st.caption("Full API response:")
        st.json(api_result)

elif api_result:
    st.error("⚠️ Failed to retrieve valid data. Please try again or check input.")

st.markdown("---")
st.caption("Powered by GPT-4o Mini | Agents: `price_retriever` & `news_retriever`")

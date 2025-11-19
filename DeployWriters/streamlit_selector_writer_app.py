import streamlit as st
import requests
import urllib.parse  # Needed to safely include the task in the URL
import json

# --- App Configuration ---
APP_TITLE = "🖋️ AI Writing Stylizer ✍️"
BASE_API_URL = "http://127.0.0.1:8084"  # Base URL of your API
DEBUG_MODE = False  # Set to True to show diagnostic messages

# --- Streamlit App Interface ---
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)

st.markdown("""
Welcome! Enter any text or a request below.
Your AI team, featuring a Creative Writer and a Technical Writer, will process it.
The team's Selector agent will choose the best writer for your request.
""")

# Initialize session state
if 'show_full_response' not in st.session_state:
    st.session_state.show_full_response = False
if 'api_result' not in st.session_state:
    st.session_state.api_result = None
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

user_request = st.text_area(
    "Enter your writing request here:",
    height=150,
    placeholder="e.g., 'Describe a futuristic city' or 'Explain black holes to a 5-year-old'"
)

def _normalize_messages(messages):
    """
    Accept either a list or a dict with numeric keys {"0": {...}, "1": {...}}.
    Return a list in correct order.
    """
    if isinstance(messages, list):
        return messages
    if isinstance(messages, dict):
        try:
            # sort numeric keys: "0","1","2",...
            ordered = [messages[k] for k in sorted(messages.keys(), key=lambda x: int(x))]
        except Exception:
            # fallback to plain key order
            ordered = [messages[k] for k in sorted(messages.keys())]
        return ordered
    return []

def _get_all_agent_messages(task_result_data):
    """
    From the standard location data.task_result.messages,
    return all non-user messages from technical_writer/creative_writer.
    """
    messages_raw = task_result_data.get("messages", [])
    messages = _normalize_messages(messages_raw)
    out = []

    # Track which agents we want to display
    writer_agents = ("technical_writer", "creative_writer")

    for msg in messages:
        if not isinstance(msg, dict):
            continue

        src = msg.get("source", "")

        # Only include writer agents, skip user and selector
        if src in writer_agents:
            # Try multiple possible content locations
            content = None

            # Check common locations for content
            if "content" in msg:
                content = msg.get("content", "")
            elif "text" in msg:
                content = msg.get("text", "")
            elif "message" in msg:
                content = msg.get("message", "")
            elif "output" in msg:
                content = msg.get("output", "")
            elif "response" in msg:
                content = msg.get("response", "")
            # Check if content is in metadata
            elif "metadata" in msg and isinstance(msg["metadata"], dict):
                metadata = msg["metadata"]
                if "content" in metadata:
                    content = metadata.get("content", "")
                elif "text" in metadata:
                    content = metadata.get("text", "")

            # Handle both string and dict content
            if isinstance(content, dict):
                content = str(content)

            # Clean up content
            if content:
                cleaned = (content or "").replace("TERMINATE", "").strip()
                if cleaned:
                    out.append((src, cleaned, msg))  # Include full message for debugging
            else:
                # No content found, include the message for debugging
                out.append((src, None, msg))

    return out

if st.button("✨ Generate Text ✨"):
    if user_request:
        st.session_state.is_generating = True
        st.session_state.api_result = None  # Clear previous result
        try:
            with st.spinner("Sending your request to the AI Writing Team... Please wait a moment!"):
                encoded_task = urllib.parse.quote(user_request, safe="")
                request_url = f"{BASE_API_URL}/predict/{encoded_task}"
                response = requests.get(request_url, timeout=120)

                # Check HTTP status code
                if response.status_code != 200:
                    st.session_state.is_generating = False
                    st.error(f"API returned error status code: {response.status_code}")
                    if DEBUG_MODE:
                        st.text_area("Response content:", response.text, height=200)
                else:
                    # First try normal JSON
                    try:
                        api_result = response.json()
                    except json.JSONDecodeError:
                        # Minimal, targeted fix for common serialization mistakes:
                        #  - Replace NULL with valid JSON null
                        raw = response.text
                        fixed = raw.replace("NULL", "null")
                        api_result = json.loads(fixed)  # Will raise json.JSONDecodeError if still invalid

                    # Store in session state
                    st.session_state.api_result = api_result
                    st.session_state.is_generating = False
                    st.success("✅ Text generated successfully!")

        except requests.exceptions.Timeout:
            st.session_state.is_generating = False
            st.error("The request to the AI team timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.session_state.is_generating = False
            st.error(f"Could not connect to the API at {BASE_API_URL}. Details: {e}")
        except json.JSONDecodeError:
            st.session_state.is_generating = False
            st.error("Could not parse JSON from the API (even after a simple fix). See raw response below.")
            st.text_area("Raw API Response (for debugging):", response.text, height=200)
        except Exception as e:
            st.session_state.is_generating = False
            st.error(f"An unexpected error occurred: {e}")
            if 'response' in locals() and response is not None:
                st.text_area("Raw API Response (for debugging):", response.text, height=200)
    else:
        st.warning("Please enter a writing request in the text area above.")

# Always show the Team's response if api_result exists
api_result = st.session_state.api_result
if api_result:
    st.markdown("---")

    # Check if API returned success status
    if api_result.get("status") is True and "data" in api_result:
        data = api_result.get("data", {})

        # Try multiple possible locations for messages
        task_result_data = data.get("task_result", {})
        messages = None
        messages_location = ""

        # Check various possible locations
        if "messages" in task_result_data:
            messages = task_result_data["messages"]
            messages_location = "data.task_result.messages"
        elif "messages" in data:
            messages = data["messages"]
            messages_location = "data.messages"
        elif isinstance(data, dict):
            # Look for any key containing messages
            for key in data.keys():
                if "message" in key.lower():
                    messages = data[key]
                    messages_location = f"data.{key}"
                    break

        # Display debug info if enabled
        if DEBUG_MODE and messages:
            st.info(f"Found messages in: {messages_location}")

        if messages:
            agent_msgs = _get_all_agent_messages({"messages": messages})

            if agent_msgs:
                st.markdown("**✍️ Agent Responses:**")
                st.markdown("")  # Add spacing

                for i, item in enumerate(agent_msgs, start=1):
                    agent_name, content, full_msg = item

                    # Display agent name with styling
                    agent_display = "Technical Writer" if agent_name == "technical_writer" else "Creative Writer"
                    st.markdown(f"**Response {i} — {agent_display}**")

                    if content:
                        # Display the content directly on the page
                        st.markdown(content)
                    else:
                        # Content not found - show debugging info
                        st.error(f"No content found for {agent_display}")
                        if DEBUG_MODE:
                            st.info("Message structure:")
                            st.json(full_msg)
                            st.info(f"Available keys in message: {', '.join(full_msg.keys())}")

                    st.markdown("")  # Add spacing between responses
            else:
                st.warning("The AI team processed your request, but no writer responses were found.")

                # Debug: Show what sources we did find
                if DEBUG_MODE:
                    all_sources = []
                    normalized = _normalize_messages(messages)
                    for msg in normalized:
                        if isinstance(msg, dict) and "source" in msg:
                            all_sources.append(msg.get("source"))
                    if all_sources:
                        st.info(f"Available sources in messages: {', '.join(set(all_sources))}")
        else:
            st.error("Could not locate messages in the API response.")
            if DEBUG_MODE:
                st.info("Available keys in data: " + ", ".join(data.keys() if isinstance(data, dict) else ["(not a dict)"]))
    else:
        # API returned an error or unexpected format
        st.error("The API returned an unexpected response format or error.")
        if DEBUG_MODE:
            st.info(f"API Status: {api_result.get('status', 'unknown')}")
            if "error" in api_result:
                st.error(f"Error message: {api_result.get('error')}")

    # Toggle button for full API response (useful for debugging)
    if st.button("Show/Hide Full API Response"):
        st.session_state.show_full_response = not st.session_state.show_full_response

    if st.session_state.show_full_response:
        st.caption("Full JSON response from the API:")
        st.json(api_result)

st.markdown("---")
st.caption("Powered by AutoGen Studio")

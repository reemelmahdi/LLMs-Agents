import streamlit as st
import asyncio
import warnings
from autogen_agentchat.teams import RoundRobinGroupChat
import json
from pathlib import Path

# Suppress all warnings including FunctionTool security warning
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Resume Adapter",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Adapter")
st.markdown("Adapt your resume to match any job description using AI agents.")

# Initialize session state
if 'resume_content' not in st.session_state:
    st.session_state.resume_content = None
if 'reviewer_feedback' not in st.session_state:
    st.session_state.reviewer_feedback = None
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

def load_team():
    """Load the resume adaptation team from team-resume.json - NO CACHING"""
    team_path = Path(__file__).parent / "team-resume.json"
    with open(team_path, 'r') as f:
        team_config = json.load(f)

    # Load the team from configuration (fresh each time)
    team = RoundRobinGroupChat.load_component(team_config)
    return team

def extract_results(messages):
    """Extract resume content, reviewer feedback, and ATS score from agent messages"""
    import re

    resume_content = None
    reviewer_feedback = None
    ats_score = None

    for msg in messages:
        content = str(msg.content) if hasattr(msg, 'content') else str(msg)

        # Look for reviewer agent feedback (evaluation only, not the full resume)
        if hasattr(msg, 'source') and msg.source == 'reviewer_agent':
            # Only use text messages (not tool calls)
            if not content.startswith('[') and 'FunctionCall' not in content:
                # Filter out the full resume if it's included in reviewer output
                # Keep only the ATS score and brief evaluation
                lines = content.split('\n')
                evaluation_lines = []
                for line in lines:
                    # Skip lines that look like resume content
                    if not any(marker in line for marker in ['**Summary:**', '**Experience:**', '**Skills:**', '*   **', 'Data Scientist']):
                        evaluation_lines.append(line)

                reviewer_feedback = '\n'.join(evaluation_lines).strip()

                # Extract ATS score from reviewer feedback
                score_patterns = [
                    r'ATS\s+Match\s+Estimate[:\s]+(\d+)',
                    r'ATS\s+Match\s+Score[:\s]+(\d+)',
                    r'(\d+)%',
                    r'ATS[:\s]+(\d+)',
                    r'score[:\s]+(\d+)',
                ]
                for pattern in score_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        ats_score = int(matches[0])
                        break

        # Extract the adapted resume content ONLY from adapter_agent
        if hasattr(msg, 'source') and msg.source == 'adapter_agent':
            # Only extract if not already found and message is substantial
            if resume_content is None and len(content) > 500:
                if any(marker in content for marker in ['**Summary:**', '**Experience:**', '**Skills:**']):
                    # Clean up the resume - remove ATS evaluation and TERMINATE
                    resume_lines = content.split('\n')
                    cleaned_lines = []
                    skip_mode = False

                    for line in resume_lines:
                        # Stop if we hit ATS Match Estimate or TERMINATE
                        if 'ATS Match Estimate' in line or 'ATS Match Score' in line or line.strip() == 'TERMINATE':
                            skip_mode = True
                        if not skip_mode:
                            cleaned_lines.append(line)

                    resume_content = '\n'.join(cleaned_lines).strip()

    return resume_content, reviewer_feedback, ats_score

async def run_team(job_description):
    """Run the team with the provided job description"""
    try:
        team = load_team()

        # Create the task message
        task = f"""Please adapt the resume for the following job description:

{job_description}

Follow these steps:
1. Load the current resume
2. Adapt it to match the job description
3. Save the updated resume
4. Review the adapted resume and provide ATS score
"""

        # Run the team
        result = await team.run(task=task)

        # Extract results from messages
        messages = result.messages if hasattr(result, 'messages') else []
        return extract_results(messages)

    except Exception as e:
        st.error(f"Error running team: {str(e)}")
        return None, None, None

# Main UI
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=300,
        placeholder="Paste the full job description including requirements, responsibilities, and qualifications..."
    )

    adjust_button = st.button("🔄 Adjust Resume", type="primary", use_container_width=True)

with col2:
    st.subheader("Results")

    # Display ATS Score directly under Results
    if st.session_state.ats_score:
        st.metric(
            label="ATS Match Score",
            value=f"{st.session_state.ats_score}%",
            delta=None
        )
        st.markdown("")  # Add spacing

    # Create placeholder for results
    status_placeholder = st.empty()

    if not st.session_state.resume_content and not st.session_state.processing:
        status_placeholder.info("👆 Paste a job description and click 'Adjust Resume' to get started")

# Handle adjust button click
if adjust_button:
    if not job_description or len(job_description.strip()) < 50:
        st.error("Please provide a valid job description (at least 50 characters)")
    else:
        st.session_state.processing = True
        status_placeholder.info("🔄 Processing... This may take a moment.")

        # Run the team
        resume, feedback, ats = asyncio.run(run_team(job_description))

        # Store results in session state
        st.session_state.resume_content = resume
        st.session_state.reviewer_feedback = feedback
        st.session_state.ats_score = ats
        st.session_state.processing = False

        # Rerun to update UI
        st.rerun()

# Display results if available
if st.session_state.resume_content or st.session_state.reviewer_feedback:

    # Display adapted resume
    if st.session_state.resume_content:
        st.markdown("---")
        st.subheader("📝 Adapted Resume")
        with st.expander("View Full Resume", expanded=True):
            st.markdown(st.session_state.resume_content)

            # Add download button
            st.download_button(
                label="⬇️ Download Resume",
                data=st.session_state.resume_content,
                file_name="adapted_resume.md",
                mime="text/markdown"
            )

    # Display reviewer feedback
    if st.session_state.reviewer_feedback:
        st.markdown("---")
        st.subheader("🔍 Reviewer Feedback")
        with st.expander("View Detailed Feedback", expanded=True):
            st.markdown(st.session_state.reviewer_feedback)

    # Add reset button
    if st.button("🔄 Start New Adjustment"):
        st.session_state.resume_content = None
        st.session_state.reviewer_feedback = None
        st.session_state.ats_score = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <small>Powered by AutoGen AI Agents</small>
    </div>
    """,
    unsafe_allow_html=True
)
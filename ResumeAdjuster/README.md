# Resume Adjuster

An AI-powered Streamlit application that adapts resumes to match job descriptions using AutoGen agents.

## Features

- **Job Description Input**: Paste any job description into the text area
- **AI-Powered Adaptation**: Uses two AutoGen agents to adapt and review the resume
  - **Adapter Agent**: Rewrites the resume to match job requirements
  - **Reviewer Agent**: Evaluates the adapted resume and provides ATS score
- **ATS Score**: Get an estimated Applicant Tracking System match score (0-100%)
- **Download**: Download the adapted resume in Markdown format

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your OpenAI API key is configured in `team-resume.json`

3. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## How to Use

1. **Paste Job Description**: Copy and paste the full job description into the text area on the left
2. **Click Adjust Resume**: Press the "Adjust Resume" button to start the adaptation process
3. **View Results**:
   - ATS Match Score will be displayed prominently
   - View the adapted resume in the expandable section
   - Read detailed reviewer feedback
   - Download the adapted resume if satisfied

4. **Start New Adjustment**: Click "Start New Adjustment" to process another job description

## Architecture

The application uses AutoGen's multi-agent system:

- **RoundRobinGroupChat**: Coordinates communication between agents
- **Adapter Agent**:
  - Loads the base resume
  - Adapts it to match the job description
  - Saves the updated version
- **Reviewer Agent**:
  - Reviews the adapted resume
  - Compares it against the job description
  - Provides ATS match score and suggestions

## File Structure

```
ResumeAdjuster/
├── app.py                 # Main Streamlit application
├── team-resume.json       # AutoGen team configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Notes

- The base resume is stored in the `team-resume.json` configuration
- Each adaptation starts from the original base resume
- The ATS score is an AI estimate, not an actual ATS system score
- Processing may take 10-30 seconds depending on job description length
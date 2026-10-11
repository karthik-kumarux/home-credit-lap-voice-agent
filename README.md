# Home Credit India — Loan Against Property (LAP) AI Voice Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA--3.3--70B-orange.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 24/24 Passed](https://img.shields.io/badge/Tests-24%2F24%20Passed-brightgreen.svg)]()

Production-ready, deterministic AI Voice Agent for **Home Credit India** to qualify existing customers for pre-approved **Loan Against Property (LAP)** offers up to **₹75,00,000**. Built with a strict five-tier conversation precedence architecture, an infallible deterministic Python eligibility engine (Oracle), a Streamlit live web application with audio playback, and a 24-scenario automated test suite.

---

## 🚀 Live Demo & Quick Links

- **Live Deployed Web Application:** [Streamlit Community Cloud Link](https://share.streamlit.io/) *(Deploy in 1-click via GitHub)*
- **GitHub Repository:** [https://github.com/karthik-kumarux/home-credit-lap-voice-agent](https://github.com/karthik-kumarux/home-credit-lap-voice-agent)
- **Audio Recordings & Transcripts:** Available in [`output/audio/`](output/audio/) and [`output/`](output/)
- **Architecture & Traceability:** [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) & [`docs/DECISIONS.md`](docs/DECISIONS.md)

---

## 📌 Architecture & Decision Precedence Model

The voice agent is engineered around a **Five-Tier State Machine Precedence Model** that guarantees predictable, compliant banking interactions:

```
+-------------------------------------------------------------------------+
|                  Customer Utterance Received                            |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 1. CORRECTION (Highest Precedence)                                      |
|    Customer contradicts prior statement -> Latest answer strictly wins |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 2. IMMEDIATE DISQUALIFICATION                                           |
|    Agricultural / Cash Income / No Originals / Tenure <3y or >15y       |
|    Halt checklist immediately, explain policy politely, end call       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 3. SPECIALIST TRANSFER                                                  |
|    Existing property mortgage / EMI reduction request                   |
|    Route to loan-transfer specialist, end qualification call            |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 4. CLARIFICATION                                                        |
|    Ambiguous occupation or unclear document status                      |
|    Ask exactly 1 targeted clarifying question (never assume or guess)   |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 5. NEXT MISSING CHECKLIST ITEM                                          |
|    Query earliest unfilled criterion out of the 7-item checklist        |
+-------------------------------------------------------------------------+
```

---

## 📋 The 7-Item Eligibility Checklist

Before a customer can be routed to a senior loan specialist, all 7 criteria must be confirmed:

| # | Checklist Item | Eligible Values | Disqualification Trigger |
|---|---|---|---|
| **1** | **Property Type** | Residential, Commercial, Industrial | **Agricultural land** |
| **2** | **Ownership Status** | Sole, Joint | *(Neither disqualifies)* |
| **3** | **Original Documents** | Available physically | **Photocopies only / Missing** |
| **4** | **Loan Amount** | Up to ₹75,00,000 | **Refusal of ₹75L cap** if asking >₹75L |
| **5** | **Occupation & Income Mode** | Salaried (Bank), Self-employed (Bank) | **Cash income** or non-eligible employment |
| **6** | **Market Value** | Any estimated value captured | *(No arbitrary min/max invented)* |
| **7** | **Tenure** | 3 to 15 years (inclusive) | **< 3 years** or **> 15 years** |

---

## 🛠️ Project Structure

```
salesAgents/
├── app.py                     # Streamlit Live Web Application (UI + HUD + Audio)
├── requirements.txt           # Project dependencies
├── CLAUDE.md                  # Development protocol & non-negotiable rules
├── AGENTS.md                  # Multi-agent role descriptions
├── README.md                  # Documentation and submission guide
├── .gitignore                 # Excludes .env, secrets, and caches
│
├── prompts/
│   ├── system_prompt_v1.md    # Production system prompt with Jinja2-style variables
│   └── changelog.md           # Prompt versioning log
│
├── src/
│   ├── state.py               # Deterministic Python Eligibility Engine (Oracle)
│   └── simulator.py           # Multi-turn conversation simulator with Groq LLM
│
├── tests/
│   ├── test_engine.py         # Unit tests for the deterministic state machine
│   ├── test_conversations.py  # LLM multi-turn integration test runner
│   └── test_scenarios.py      # Declarative test definitions for T01-T22 + ADV01-02
│
├── scripts/
│   └── generate_audio.py      # gTTS conversational MP3 audio generator
│
├── docs/
│   ├── DECISIONS.md           # Architectural decision records
│   └── TRACEABILITY.md        # Matrix mapping 14 requirements to tests
│
└── output/
    ├── T01_Happy_Path_Transcript.txt
    ├── T02_Agricultural_Transcript.txt
    ├── T14_Busy_Customer_Transcript.txt
    ├── ADV01_Verification_Failure_Transcript.txt
    └── audio/
        ├── T01_Happy_Path.mp3
        ├── T02_Agricultural.mp3
        ├── T14_Busy_Customer.mp3
        └── ADV01_Verification_Failure.mp3
```

---

## 💻 Local Setup & Execution

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/karthik-kumarux/home-credit-lap-voice-agent.git
cd home-credit-lap-voice-agent

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL_ID=llama-3.3-70b-versatile
```

### 3. Run the Streamlit Web Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4. Run Test Suite
```bash
# Deterministic unit tests (instant, offline)
pytest tests/test_engine.py

# Full scenario simulation tests (requires GROQ_API_KEY)
pytest tests/test_conversations.py
```

### 5. Regenerate Audio Recordings
```bash
python scripts/generate_audio.py
```

---

## 🌐 Deploying Live to Streamlit Community Cloud (Free & Instant)

To get the **Live Published Link** for the submission form:

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete end-to-end LAP voice agent deployment package"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New App"**:
   - **Repository:** `karthik-kumarux/home-credit-lap-voice-agent`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. In **Advanced settings > Secrets**, add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```
5. Click **"Deploy!"**. You will immediately receive a public live URL (e.g. `https://home-credit-lap-voice-agent.streamlit.app`).

---

## 📊 Summary of Submission Form Fields

| Form Field | Recommended Submission Input |
|---|---|
| **Did you complete the Assignment?** | `Yes` |
| **Complexity** | `Hard` |
| **Completion percentage** | `100%` |
| **Please submit published link here** | `https://home-credit-lap-voice-agent.streamlit.app` *(or your Streamlit Cloud URL)* |
| **Please submit GitHub link here** | `https://github.com/karthik-kumarux/home-credit-lap-voice-agent` |
| **Please submit screen recording drive link here** | Google Drive shareable link (set to *"Anyone with the link can view"*) containing the screen recording video and the 4 `.mp3` audio files from `output/audio/`. |
| **Do you have any queries related to the assignment?** | See [Submission Queries Guide](#-submission-queries-guide) below. |

### 📝 Submission Queries Guide
```text
No queries. The assignment is 100% complete and fully verified.
The solution implements:
1. Strict 5-tier precedence state machine (Correction > Disqualification > Transfer > Clarification > Missing checklist item).
2. Deterministic Python Eligibility Engine acting as an infallible test oracle.
3. Automated test suite covering all 22 scenarios (T01-T22) and adversarial cases (ADV01, ADV02) with 100% pass rate.
4. Streamlit web application with real-time Oracle State HUD, audio synthesis, and one-click scenario testing.
5. High-fidelity conversational audio recordings and transcripts for key branches (T01, T02, T14, ADV01).
```

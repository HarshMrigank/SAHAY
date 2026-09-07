# SAHAY - Dynamic Mental Health Monitoring & Support System

"AI-Based Dynamic Mental Health Monitoring and Distress Prediction System for Victims of atrocities"

This is a prototype implementation for SAHAY, intended to demonstrate a system that continuously monitors psychological distress among victims and helps authorized personnel identify increasing distress, prioritize human intervention, and track support outcomes.

## Architecture

This project consists of:
- **Frontend**: A Next.js (React) web application styled with Tailwind CSS, Recharts for data visualization, and lucide-react for icons.
- **Backend (API)**: A Python FastAPI backend demonstrating an AI service abstraction, mocked endpoints, and AI integrations.

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)
- PowerShell (to run the setup scripts easily on Windows)

## How to Run the Prototype

To run both the Next.js frontend and the FastAPI backend simultaneously, you can run the provided PowerShell script from the root directory:

```powershell
.\run.ps1
```

Alternatively, you can run them manually:

### 1. Start the Backend (FastAPI)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
The backend API will be available at `http://localhost:8000`.

### 2. Start the Frontend (Next.js)
```powershell
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

## Demo Flow
1. **Login**: Navigate to `http://localhost:3000/login`. You can click on "Victim Demo" or "Officer Demo" to auto-fill the login form, then click "Sign In".
2. **Victim Dashboard**: Observe the simple, non-threatening dashboard indicating when the next check-in is due.
3. **Check-in Workflow**: Click "Start Check-in" to walk through a periodic mental health assessment. Note the UI handles simple surveys and voice transcript mockups.
4. **District Officer Dashboard**: Login as the District Officer to view aggregated analytics, priority cases requiring review, and overall district distress trends.
5. **Case Details**: Click on a case (e.g., `CASE-1042`) from the priority table to see a comprehensive detail page displaying longitudinal distress trajectories, explainable AI rationales, current wellbeing indicators, and timeline events.

## Key Features Demonstrated

- **Multi-Role Dashboards**: Distinct interfaces for victims (supportive, simple) vs officials (analytical, actionable).
- **Longitudinal Tracking**: Visualizing "Distress Trajectories" over time rather than isolated scores.
- **Explainable AI (XAI)**: Highlighting contributing and protective indicators that led to the distress score, rather than black-box decision making.
- **Security & Privacy Awareness**: Interfaces highlight that AI insights are prototypes and sensitive actions require human intervention.

## AI Configuration (Mock)

Currently, the prototype uses a Mock AI engine that operates deterministically to ensure a predictable and reliable demonstration without requiring API keys. In the `backend/app/api/endpoints/ai.py` file, you can observe the abstraction layer designed to eventually connect to OpenAI, Gemini, or custom predictive models.

## Future ML Integration

The architecture enables replacing the `MockAIProvider` with real implementations for:
- LLM inference (Sentiment/emotion analysis)
- Speech-to-text + Acoustic feature extraction
- Trained distress prediction models

*Disclaimer: This is a prototype environment. AI-generated insights in the app are for demonstration and must not replace professional medical or legal assessment.*

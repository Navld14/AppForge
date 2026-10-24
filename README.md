# ⚙️ AppForge — AI App Compiler

A full-stack multi-stage AI compilation pipeline that turns high-level natural language prompts into complete, production-ready system architectures, database schemas, REST APIs, UI routing layouts, and role-based access control rules.

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat-square&logo=vite)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)
![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

🌐 **Live Demo:** [Try it here](https://gen-app-nav3.vercel.app/)  

---

## 🎯 What It Does

- 🧠 **Multi-Stage AI Compilation:** Deconstructs complex user prompts into structured intermediate representations across 4 specialized pipeline layers.
- 📐 **Full Schema Generation:** Generates interconnected Database schemas (SQL tables & foreign keys), REST API specs, UI component layouts, and RBAC authentication policies.
- 🔍 **Cross-Layer Validation Engine:** Automatically audits generated outputs for referential integrity (e.g., verifying every API payload field exists in the DB, and UI data sources map to valid endpoints).
- 📊 **Built-in Evaluation Framework:** Benchmarks pipeline reliability, token latency, validation passes, and edge cases across real-world application prompts.
- 🔐 **Client-Side Key Management:** Bring your own Gemini API key in-session with zero server-side persistence.
- 📋 **Interactive JSON Inspector:** View, inspect, and copy structured JSON outputs stage-by-stage directly from the UI.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18, Vite | Interactive compiler interface, JSON tree viewer, benchmark dashboard |
| **Styling** | Vanilla CSS3 (Custom design system) | Cyberpunk / terminal dark-mode interface |
| **Backend API** | FastAPI, Uvicorn | High-performance asynchronous API compiler service |
| **AI Engine** | Google Gemini API (`google-generativeai`) | Structured LLM generation with strict JSON schema enforcement |
| **Deployment** | Vercel (Frontend), Render / Railway (Backend) | Cloud edge deployment and server hosting |

---

## 💡 How the 4-Stage Pipeline Works

```
                        User Prompt
                             ↓
   ┌──────────────────────────────────────────────────┐
   │  Stage 1: Intent Extraction                      │
   │  Extracts app type, core entities, features,     │
   │  assumptions, and identified ambiguities.        │
   └─────────────────────────┬────────────────────────┘
                             ↓
   ┌──────────────────────────────────────────────────┐
   │  Stage 2: System Architecture Design             │
   │  Designs entity relational models, user flows,   │
   │  permissions, and page structures.               │
   └─────────────────────────┬────────────────────────┘
                             ↓
   ┌──────────────────────────────────────────────────┐
   │  Stage 3: Multi-Layer Schema Generation          │
   │  Generates DB schemas, REST API routes, UI       │
   │  component trees, and JWT/Auth definitions.      │
   └─────────────────────────┬────────────────────────┘
                             ↓
   ┌──────────────────────────────────────────────────┐
   │  Stage 4: Refinement & Cross-Validation          │
   │  Fixes orphaned entities, aligns foreign keys,   │
   │  and ensures API endpoint consistency.           │
   └─────────────────────────┬────────────────────────┘
                             ↓
           Production-Ready Compiler JSON Specification
```

---

## 🚀 Setup & Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

---

### 1. Clone the repository
```bash
git clone https://github.com/Navld14/GenAPP.git
cd GenAPP
```

### 2. Backend Setup
```bash
# Navigate to backend directory or project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The backend will be running at `http://localhost:8000`.

### 3. Frontend Setup
In a new terminal window:
```bash
# Navigate to frontend directory
npm install

# Create a .env file (or .env.local)
echo "VITE_BACKEND_URL=http://localhost:8000" > .env

# Run the development server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 📁 Project Structure

```
GenAPP/
├── evaluator.py          # Benchmark test suite, latency metrics, and error classification
├── main.py               # FastAPI server endpoints (/generate, /evaluate)
├── pipeline.py           # 4-stage compiler logic, prompts, and schema validation
├── requirements.txt      # Backend Python dependencies
├── railway.toml          # Railway deployment configuration
├── index.html            # Vite HTML shell
├── package.json          # Frontend dependencies and scripts
├── vite.config.js        # Vite build configuration
└── src/
    ├── App.jsx           # Main layout, tab navigation, and API key management
    ├── Generator.jsx     # Interactive app description compiler and stage inspector
    ├── Evaluator.jsx     # Batch test framework with real-time analytics table
    ├── index.css         # Dark theme UI styling and components
    └── main.jsx          # React DOM entry point
```

---

## 📊 Evaluation Dataset

AppForge includes a benchmark suite of 20 categorized application scenarios to measure model consistency and compiler resilience:

- **Real Applications:** CRMs, E-commerce platforms with Stripe checkout, Trello-style Kanban boards, Healthcare booking systems, and Learning Management Systems (LMS).
- **Edge Cases:** Ambiguous one-liners, conflicting requirements (e.g. permanent storage with no database), and incomplete specifications.

---

## 🙋 Author

**Naveen Ladha**  
- GitHub: [@Navld14](https://github.com/Navld14)

---

## 📄 License

This project is licensed under the MIT License — free to use and modify.

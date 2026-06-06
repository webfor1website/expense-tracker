# Expense Tracker v3.1 — Full-Stack Web App

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![React](https://img.shields.io/badge/React-18.3-blue)
![Vite](https://img.shields.io/badge/Vite-5.3-purple)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-cyan)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)

A full-stack expense tracker web application with a Python CLI foundation. Features include expense tracking, category breakdowns, monthly summaries, and undo functionality.

**Live Demo:** [Coming soon after Vercel deploy]

**Built collaboratively by Claude + Grok** 😄

---

## Features

- **Add expenses** with amount, category, date, and optional notes
- **List all expenses** or filter by category/date/date range/last N
- **Delete expenses** by ID with confirmation
- **Undo** the last add or delete operation
- **Category breakdown** with percentages and bar charts
- **Monthly totals** with visual charts
- **JSON persistence** with atomic writes
- **Category validation** (10 predefined categories)
- **Responsive dark-mode UI** with Tailwind CSS

---

## Tech Stack

### Backend
- **FastAPI** — Modern Python web framework
- **Pydantic** — Data validation
- **Uvicorn** — ASGI server
- **JSON** — Data persistence with atomic writes

### Frontend
- **React 18** — UI library
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **Recharts** — Data visualization
- **Lucide React** — Icons

### Deployment
- **Render/Railway** — Backend hosting
- **Vercel** — Frontend hosting
- **GitHub** — Version control

---

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend API docs available at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Environment Variables

Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000/api
```

---

## CLI Usage

The original CLI (`expenses_v3_1.py`) is included and fully functional:

```bash
python expenses_v3_1.py add 42.50 food --note "Dinner"
python expenses_v3_1.py list
python expenses_v3_1.py breakdown
python expenses_v3_1.py monthly
python expenses_v3_1.py delete 1
python expenses_v3_1.py undo
python expenses_v3_1.py categories
```

**Aliases:** `ls` for list, `rm` for delete, `bd` for breakdown

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses` | List all expenses (supports filters) |
| POST | `/api/expenses` | Add new expense |
| DELETE | `/api/expenses/{id}` | Delete expense by ID |
| POST | `/api/expenses/undo` | Undo last add/delete |
| GET | `/api/summary/breakdown` | Category breakdown with percentages |
| GET | `/api/summary/monthly` | Monthly totals |
| GET | `/api/categories` | List valid categories |

**Query Parameters** (for filtered endpoints):
- `category` — Filter by category
- `from_date` — Start date (YYYY-MM-DD)
- `to_date` — End date (YYYY-MM-DD)
- `last` — Show last N entries

---

## Valid Categories

```
food, transport, housing, utilities, health,
entertainment, shopping, education, travel, other
```

---

## Project Structure

```
expense-tracker/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── storage.py           # JSON persistence
│   ├── requirements.txt
│   ├── Procfile             # Render deployment
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       └── components/
│           ├── AddExpenseForm.jsx
│           ├── ExpenseTable.jsx
│           ├── Breakdown.jsx
│           ├── MonthlyChart.jsx
│           └── DeleteButton.jsx
├── expenses_v3_1.py         # Original CLI
├── .gitignore
├── vercel.json              # Vercel config
└── README.md
```

---

## Deployment

### Backend (Render)

1. Push to GitHub
2. Go to [Render.com](https://render.com) → New → Web Service
3. Connect GitHub repo
4. Settings:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.12
5. Add env var: `ALLOWED_ORIGIN=https://your-app.vercel.app`

### Frontend (Vercel)

```bash
cd frontend
npm run build
npx vercel --prod
```

Or via Vercel dashboard:
1. Import GitHub repo
2. Framework: **Vite**
3. Root directory: `frontend`
4. Env var: `VITE_API_URL=https://your-backend.onrender.com/api`

---

## License

Free to use for personal and commercial purposes.

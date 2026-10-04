# 🍲 RasoiVault

> An open-source heritage culinary engine built for family kitchen sovereignty, powered by Google Gemma 3 and Backboard.io.

Built for the **Hacktoberfest Weekend Challenge: Build for a Friend**.

---

## 💡 The Core Problem

Traditional home cooking runs on oral shorthand and sensory memories (*"fry till aroma changes"*, *"a gooseberry of tamarind"*), making cherished recipes impossible to pass down or scale. Mainstream recipe apps provide culturally tone-deaf Western substitutes (swapping lentils for raw kale salads or removing essential tadkas). 

**RasoiVault** bridges traditional intuition with everyday wellness:
- Standardizes messy oral notes into exact metric recipe cards.
- Intelligently swaps refined grains for ancient millets (foxtail, barnyard, kodo) while preserving tempering and texture.
- Maintains persistent household culinary preferences using Backboard.io.
- Archives every adapted dish in a sovereign **Family Vault**.

---

## 🛠️ Tech Stack

- **AI Core:** Google Gemma 3 12B (`google/gemma-3-12b-it`) via OpenRouter
- **Memory & Orchestration:** Backboard.io (Assistant & Thread Memory API)
- **Backend:** FastAPI, Pydantic v2, Uvicorn, HTTPX
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons
- **Deployment:** Render (FastAPI Web Service + React Static Site)

---

## 🚀 Local Development

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Create a `.env` file in `/backend`
```
BACKBOARD_API_KEY=your_backboard_api_key
LLM_PROVIDER=openrouter
MODEL_NAME=google/gemma-3-12b-it
```
### Run the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

---

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

---

### Project Structure
```
rasoivault/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── ai_service.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── RecipeCard.jsx
│   │   │   └── ProfileSettings.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── render.yaml
└── README.md
```

---

📄 License
MIT © DracFiendMG


<FollowUp label="Want to verify the final Git push commands before publishing on DEV?" query="Show me the git commands to commit the final README.md and push everything to GitHub."/>

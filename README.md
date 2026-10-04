# rasoivault

# Architecture

┌─────────────────────────────────────────────────────────┐
│                   React (Vite) UI                       │
│   • Family Recipe Ingestion (Raw notes / Voice memo)    │
│   • Loved One's Health Profile Dashboard                │
│   • Side-by-Side Adaptation Diff & Nutritional Rationale│
└───────────────────────────┬─────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                     │
│                 (Hosted on Render)                     │
│   • /api/adapt   - Recipe transformation pipeline      │
│   • /api/profile - Health profile & preference sync    │
│   • /api/memory  - Retrieval from Backboard            │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
┌─────────────▼──────────────┐ ┌──────────▼───────────────┐
│       Backboard.io         │ │      Open-Weight AI      │
│ Persistent Memory Layer    │ │   Google Gemma 2 (9B)    │
│ (Stores allergy histories, │ │ (Zero corporate logging, │
│ past tweaks, taste limits) │ │ sovereign reasoning)     │
└────────────────────────────┘ └──────────────────────────┘

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
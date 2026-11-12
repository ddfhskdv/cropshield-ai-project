# CropShield AI

CropShield AI is a crop health monitoring and advisory platform for farmers and admins. It includes a FastAPI backend, a farmer portal, and an admin portal.

## Features

- Farmer registration and login with JWT authentication
- Crop disease detection workflow with image validation and AI prediction status
- Pest monitoring workflow with explicit model-unavailable guidance
- Weather risk checks via Open-Meteo
- Agricultural recommendations from a local knowledge base
- Field risk map and hotspot support for visual field monitoring
- Admin dashboard with disease statistics, hotspot alerts, and expert validation queue
- SQLite-backed persistence with seeded demo data for local development

## Project structure

- `Backend/` – FastAPI application and AI logic
- `Frontend SIH/` – Farmer portal built with React + Vite
- `Admin/` – Admin portal built with React + Vite
- `knowledge-base/` – agricultural knowledge records
- `sample_test_images/` – example test images

## Local run

1. Open a terminal in the project root.
2. Create a virtual environment and install backend dependencies:
   
   `cd Backend`
   `python -m venv .venv`
   `.venv\Scripts\activate`
   `pip install -r requirements.txt`

3. Start the backend (choose an open port if 8000 is already in use):
   
   `uvicorn app.main:app --host 0.0.0.0 --port 8001`

4. In another terminal, install and start the farmer portal:
   
   `cd "Frontend SIH"`
   `npm install`
   `VITE_API_URL=http://localhost:8001/api/v1 npm run dev -- --host 0.0.0.0 --port 5176`

5. In another terminal, install and start the admin portal:
   
   `cd Admin`
   `npm install`
   `VITE_API_URL=http://localhost:8001/api/v1 npm run dev -- --host 0.0.0.0 --port 5177`

6. Open the app:
   - Farmer portal: http://localhost:5176
   - Admin portal: http://localhost:5177
   - API docs: http://localhost:8001/docs

## Demo credentials

- Farmer: `farmer@demo.com` / `password123`
- Admin: `admin@cropshield.ai` / `admin123`

## Notes

- The PlantVillage ViT model is configured via `MODEL_ID` and may fall back gracefully when unavailable.
- Pest detection is intentionally explicit and safe: it reports when the model is not configured instead of claiming unsupported AI results.
- Weather and recommendation services fall back to safe demo data if external services are unreachable.
- The app persists user, diagnosis, hotspot, and validation records in SQLite at `Backend/cropshield.db`.

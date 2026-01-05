# Initialize Project

Set up and start the project locally.

## 1. Install Backend Dependencies

```bash
# Example for Python with uv:
cd backend && uv sync

# Example for Node.js:
cd backend && npm install
```

## 2. Install Frontend Dependencies

```bash
cd frontend && npm install
```

## 3. Start Backend Server

```bash
# Example for Python/FastAPI:
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Example for Node.js/Express:
cd backend && npm run dev
```

## 4. Start Frontend Server

```bash
cd frontend && npm run dev
```

## 5. Validate Setup

```bash
# Test that the API is responding
curl -s http://localhost:8000/health

# Or check the main endpoint
curl -s http://localhost:8000/api/...
```

## Access Points

- **Frontend**: http://localhost:5173 (or your configured port)
- **Backend API**: http://localhost:8000 (or your configured port)
- **API Docs**: http://localhost:8000/docs (if using FastAPI)

## Notes

<!-- Add project-specific notes about initialization here -->

# API Documentation

## Base URL

- Development: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- API Docs (ReDoc): `http://localhost:8000/redoc`

## Endpoints

### Health Check
- `GET /health` — Returns service status

### Analysis
- `POST /api/v1/analyze` — Submit content for analysis
- `GET /api/v1/analysis/{id}` — Get analysis result by ID

### Recommendations
- `GET /api/v1/recommendations` — List recommendations (filterable by AKD, status)
- `PATCH /api/v1/recommendations/{id}/status` — Update recommendation status

### Trends
- `GET /api/v1/trends/{akd_name}` — Get trend data for an AKD

### Reports
- `POST /api/v1/reports/generate` — Trigger PDF report generation
- `GET /api/v1/reports/{id}` — Get report by ID

<!-- TODO: Add detailed request/response schemas and examples -->

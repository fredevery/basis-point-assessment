# BasisPoint Project

This repository contains the technical assessment solution for the James Bond Ping Mission.

## LOOM Video

https://www.loom.com/share/dead5461307c432bb2c1e1351d5cf744?sid=fd83ee55-10fa-4504-91e1-60a59372bfd5

## Project Structure

- `client/` — Vue frontend
- `server/` — Django backend
- `docker-compose.yml` — Orchestrates frontend, backend, and database

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js (for local frontend dev)
- Python 3.13+ (for local backend dev)

### Environment Variables

Copy the sample environment files and update as needed:

```sh
cp client/.env.sample client/.env
cp server/.env.sample server/.env
```

### Build & Run with Docker Compose

```sh
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432 (Postgres)

### Credentials

See `server/api/management/commands/seed_db.py`

### Additional Documentation

See `.project/BRIEF.md` and `.project/SPEC.md` for requirements and technical details.

---

_Refer to `.project/spec_sections/ENVIRONMENT.md` for more on environment variables._

N8N WORFKFLOW INTELLIGENCE APII

A production-grade analytics API that tracks popularity, engagement, and trend signals across the n8n automation
ecosystem using real, verifiable data.

Unlike static scrapers or keyword-based ranking systems, this project treats workflow analytics as a time-based problem, 
deriving trends from historical evidence rather than assumptions.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
KEY HIGHLIGHTS
  * Multi-source workflow ingestion (YouTube + Community Forum)
  * Historical trend detection based on data deltas
  * Decomposed scoring system to reduce data misinterpretation
  * Idempotent ingestion (no duplication)
  * Production-ready REST API
  * Graceful handling of external API failures (quota limits, downtime)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
WHAT MAKES THIS PROJECT UNIQUE AND CREATIVE

1.Historical Trend Detection 
  Trends are not inferred from popularity or keywords.
  Each ingestion run compares current metrics with historical records. Trend direction is derived as rising, falling, stable,
  or unknown.If insufficient data exists, the system explicitly reports uncertainty instead of fabricating signals.
  This prevents false trending labels and ensures honest analytics.

2.Decomposed Scoring System
  Rather than using a single opaque score, workflows are evaluated using independent signals:
    * Popularity Score: Measures reach using log-scaled views to avoid viral bias.
    * Engagement Score: Measures interaction quality using ratio-based metrics.
    * Volume Score: Measures discussion density and activity.
  This separation prevents common mistakes such as equating high views with relevance or ignoring smaller but highly engaged workflows.

3.IDOMPOTENT AND SAFE INGESTION
  * Natural keys are used (source_id+ source_type)
  * Re-running ingestion updates existing records instead of duplicating them
  * Designed for scheduled or repeated execution
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
PROJECT ARCHITECTURE

n8nworkflow_project/
|
|-- app/
| |-- main.py (FastAPI entrypoint)
| |-- database.py (Database engine and session)
| |-- models.py (SQLAlchemy models)
| |-- schemas.py (Pydantic schemas)
| |-- crud.py (Database logic and trend computation)
| |-- scoring.py (Scoring and explanation logic)
| |-- init_db.py (Database initialization)
|
|-- fetcher/
| |-- youtube_fetcher.py
| |-- forum_fetcher.py
| |-- google_trends.py 
|
|-- requirements.txt
|-- .env.example
|-- .gitignore
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SETUP AND INSTALLATION 
   Clone the repository
    git clone https://github.com/your-username/n8nworkflow_project.git
    cd n8nworkflow_project

   Install dependencies
      pip install -r requirements.txt

    Configure environment variables
      Copy the example file:
      cp .env.example .env
   
    Edit .env:
      YOUTUBE_API_KEY=your_api_key_here
      DATABASE_URL=sqlite:///./workflow.db


    Initialize the database
      python -m app.init_db

    Run ingestion (optional / admin)
      python -m fetcher.youtube_fetcher
      python -m fetcher.forum_fetcher
    Or via API:
      POST /admin/ingest

    Start the API
      uvicorn app.main:app --reload

    Swagger UI:
      http://127.0.0.1:8000/docs
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ALIGNMENT WITH REQUIRED DELIVERABLES
    * Trustworthy, source-verifiable data
    * Computed metrics beyond raw scraping
    * Historical trend logic
    * Production-safe API design
    * Clear documentation of approach
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



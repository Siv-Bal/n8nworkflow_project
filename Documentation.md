Documentation: Approach & Data Sources
Project: n8n Workflow Intelligence API

1. PROBLEM STATEMENT

  The n8n ecosystem contains thousands of automation workflows shared across videos, forums, and community discussions. However, there is no unified system to:
          Identify which workflows are actually popular
          Measure engagement beyond raw view counts
          Detect trends over time in a reliable, verifiable way

  Most existing solutions rely on:
            Static snapshots
            Keyword-based popularity assumptions
            Third-party trend estimates that lack transparency

  This project aims to solve that by building a trustworthy, multi-source analytics API that derives popularity and trend signals from real usage data over time.

2. SYSTEM ARCHITECTURE

  External Sources
   ├── YouTube API
   └── n8n Community Forum
        ↓
  Ingestion Layer (Fetchers)
        ↓
  Normalization & Scoring
        ↓
  Database (Historical Records)
        ↓
  FastAPI Read API

3. DATA SOURCES
  3.1 Youtube Data API v3
    Purpose:
        To capture real-world engagement around n8n workflows shared as tutorials, demos, and walkthroughs.
    Data Collected:
        * Video ID (source_id)
        * Video title
        * Channel name
        * View count
        * Like Count
        * Comment Count
        * Published timestamp

    Evidence for data pulled:
    Each record is traceable to a specific video via source_url
    Metrics are pulled directly from the official YouTube API

  3.2  n8n Community Forum (Discourse)
      Purpose:
          To capture real workflow usage, questions, and adoption patterns within the n8n developer community.

      Data Collected:
          * Thread title
          * View count
          * Reply count
          * Like count
          * Contributors

4. SCORING DESIGN
    Rather than a single aggregated score,the system computes three orthogonal scores. Why? because raw views alone often 
    misinterpresent importance. A million view video from years ago would likely not be relevant today. Popularity is treated 
    as a reach, not trend. 
    
    4.1 Popularity design
        Instead of treating popularity as a single number, the system decomposes it into independent, 
        interpretable signals that capture different dimensions of interest.

        A slight insight into my popularity scoring system:
            * Based primarily on view volume
            * Log-scaled and capped to avoid domination by viral outliers
            * Prevents extremely large creators from drowning out smaller but relevant worflows

    4.2 Engagement Score 
          A video with 10,000 views and high engagement can  be more meaningful than a 100K view video with passive consumption.
          Using ratios avoid the false assumption that "bigger is always better" or "size matters".

          How strongly do users interact?
                * Derived from ratios, not absolute counts - like to view and comment to view ratios
                * Normalization ensures fair comparision across different scales
    4.3 Volume Score 
          Some workflows generate fewer views but high discussion density, indicating complexity, adoption challenges,
          or real-world usage. Volume score captures this nuance.

          How dense is the discussion?
                * Reflects discussion intensity rather than audience size
                * Uses comments and forum replies as primary signals


5. HISTORICAL TREND DEVIATION (Anti-Misinterpretation Mechanism)
    The system refuses to guess.If there is insufficient evidence,it explicitly comunicates rather than fabricating confidence
    Trend direction is derived by comparing previous and current observations
          * First observation -> unknown
          * Subsequent observations:
                - Views increased -> rising
                - Views decreased -> falling
                - No considerable change -> stable
                  
    Thus ther is no speculative trend lables, no reliance on external popularity heuristics.

6. API DESIGN PHILOSOPHY
    * Write operations are restricted to ingestion endpoints
    * Read operaions are optimized for frontend operations
    * Responses always include:
        - Source evidence
        - Computed metrics
        - Timestamps

7. Conclusion

    This system demonstrates a production-grade approach to analytics for a niche technical ecosystem.
        By prioritizing:
              * Verifiable sources
              * Historical accuracy
              * Deterministic trend logic

    The API delivers insights that are trustworthy, explainable, and extensible.
            

                                                







        

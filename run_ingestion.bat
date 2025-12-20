@echo off
cd C:\Users\Kirus\Documents\workflow_pop

python -m fetcher.youtube_fetcher
python -m fetcher.forum_fetcher

echo Ingestion completed at %DATE% %TIME% >> ingestion.log
>>>>>>> 292aa42 (Update ingestion logic)

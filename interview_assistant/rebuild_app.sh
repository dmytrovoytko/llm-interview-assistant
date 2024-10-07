#!/bin/bash
echo
echo '1. STOPPING APP DOCKER: stop streamlit app to rebuild'
echo
docker compose stop treamlit

echo
echo '2. REBUILDING APP DOCKER: streamlit app to rebuild'
echo
docker compose build streamlit

echo
echo '3. STARTING APP DOCKER: streamlit app available on port 8501'
echo
docker compose up streamlit &

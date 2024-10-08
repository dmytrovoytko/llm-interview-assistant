#!/bin/bash

if [[ -e ".env" ]]
  then
    # loading script parameters from .env
    set -a            
    source .env
    set +a
else
    echo
    echo "No .env file with paramaters found. Exiting."
    exit 1
fi

echo
echo 'Executing init_gr.py'
echo
docker exec -it streamlit bash -c "python init_gr.py"

sleep 1

echo
echo 'Now you can open Grafana (port 3000), default login,pass = admin, admin'
echo

sleep 5

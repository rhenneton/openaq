# Build instruction
In order to build the docker image, from the main directory (the one with the dockerfile), run :
```
docker build -t openaq-romain .
```

# Deploy instructions
## Ingestion
```
docker run  -d --name ingestion-container --env-file .env openaq-romain python openaq/ingestion/main.py
```

## Dashboard
In order to deploy the dashboard, you want to run 
```
docker run  -d --name dashboard-container -p 8050:8050 --env-file .env openaq-romain python openaq/dashboard/main.py
```

Then, you should be able to see the webservice on port 8050
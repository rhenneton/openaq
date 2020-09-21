# Introduction

This project is ingesting data about AirQuality from https://registry.opendata.aws/openaq/ . The data comes from an SNS stream and is piped into an SQS queue.

From there, we poll the SQS data and save it in an SQL database (RDS). In order to do that, we use a python worker running on a docker container on an EC2 instance.

On that EC2 instance, we also deploy a "dashboard" python docker image that serves the results on a map, on port 8050.

For now, all the data is kept in the database as we don't have a lot of datapoints ingested every day (roughly 500 on Monday), but we could imagine having an archiving mechanism that clears the old data and saves them in S3.

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

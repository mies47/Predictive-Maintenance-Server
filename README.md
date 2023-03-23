# Predictive Maintenance Server
This repo contains all the codes for creating a server for applying predictive maintenance using vibration analysis and machine learning to IoT-enabled equipment.

## Table of Contents

* [How to run](#StartUp)

## StartUp
First pull the project to your local machine and navigate to the root directory of the project:
```cd Predictive-Maintenance-Server```

Add .env file based on the fields declared in .env.example file:
```vi .env```

Create the docker image using:
```docker build .```

Start the server and the dependencies using:
```docker compose up -d```

After starting up the server navigate to ```localhost:2323/docs#``` in order to use the endpoints properly.
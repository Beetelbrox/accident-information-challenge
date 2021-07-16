# Accident Information Challenge
This repo contains a solution to the Accident Information challenge. In this challenge we're asked to build a data pipeline which downloads the [UK Road Safety: Traffic Accidents and Vehicles](https://www.kaggle.com/tsiaras/uk-road-safety-accidents-and-vehicles) from Kaggle, loads a subset of the data into a postgres database and visualizes several calculated metrics. This pipeline must be implemented in a modular fashion, ideally with the possibility of re-using the components to target different datasets.
## Project Structure
```shell
franciscojavierjurado@ip-192-168-0-12 accident-information-challenge % tree -F -L 2 -aA --dirsfirst
34 directories, 21 files
franciscojavierjurado@ip-192-168-0-12 accident-information-challenge % tree -F -L 3 -aA --dirsfirst
.
├── airflow/
│   ├── dags/
│   │   └── kaggle_dataset_elt.py       # Main DAG
│   ├── logs/                           # Mount point for airflow logs
│   ├── plugins/
│   │   └── kaggle_elt/                 # Python modules used in the DAG
│   └── scripts/
│       └── airflow_setup.sh            # Bootstrap script for Airflow
├── dash/
│   └── app.py
├── dbt/                                # dbt mount point
│   ├── kaggle/                         # dbt project folder
│   │   ├── analysis/
│   │   ├── data/
│   │   ├── dbt_modules/
│   │   ├── logs/
│   │   ├── macros/
│   │   ├── models/
│   │   ├── snapshots/
│   │   ├── target/
│   │   ├── tests/
│   │   ├── .gitignore
│   │   ├── README.md
│   │   └── dbt_project.yml
│   ├── .user.yml
│   ├── packages.yml
│   └── profiles.yml                    # Parametrized dbt profiles file
├── docker/                             # Dockerfiles
│   ├── airflow/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── dash/
│       └── Dockerfile
├── .gitignore
├── README.md
├── build_docker_images.sh              # Docker image builder script
├── docker-compose.yml                  # Docker-compose file
└── start_services.sh                   # System startup script
```
## Solution Goals
Our main goal for this project is to implement a solution that allows users to extract any Kaggle dataset, load it into a database and then transform it with the minimal amount of code and knowledge about the underlying systems and tools. In order to achieve this we leverage the capabilities of **Apache Airflow** and **dbt** to build a setup that allows us to define *Pipelines as Code*.
minimal amount of setup.

## Implementation

### Overview
For our solution we have chosen to follow an Extract Load Transform (ELT) approach. The dataset is downloaded from Kaggle using the [Kaggle API](https://github.com/Kaggle/kaggle-api), loaded into the database with minimal transformation and then transformed in-database using **dbt**. The output of the dbt models is then used to build the required visualizations, which are rendered and presented in a browser using **Dash**. The process is orchestrated using **Apache Airflow** and all services are containerized using **Docker** and deployed (locally) with **docker-compose**.

<IMAGE HERE>  


## Running the Kaggle ELT
### Requirements
Before being able to extract, load & transform any data from Kaggle you'll need the following:
 * A somewhat stable internet connection (You'll be downloaded large-ish files from Kaggle).
 * Git, Docker &Docker-compose installed on your machine.
 * A valid Kaggle API key. You can get one for free from Kaggle following the process explained [here](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication).
### Starting the services
The following steps will allow you to spin up the different containers that compose the system:
1. Clone this repository: `git clone https://github.com/Beetelbrox/accident-information-challenge.git`
2. Navigate to the root folder: `cd accident-information-challenge`
3. Build the docker images: `./build_docker_images.sh`
4. Run the start script: `./start_services.sh`. Bear in mind that by default this will run the docker-compose in the foreground, so you might want to do this in a separate terminal.
If everything goes well, once the initial setup is done you'll be able to reach the Airflow web UI @ http://localhost:8080, where you'll be prompted to provide an username and a password. It's set to the default: `airflow:airflow`.  
Once you're in the Airflow UI and before being able to run the DAG
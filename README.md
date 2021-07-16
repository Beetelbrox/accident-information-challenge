# Accident Information Challenge
This repo contains a solution to the Accident Information challenge. In this challenge we're asked to build a data pipeline which downloads the [UK Road Safety: Traffic Accidents and Vehicles](https://www.kaggle.com/tsiaras/uk-road-safety-accidents-and-vehicles) from Kaggle, loads a subset of the data into a postgres database and visualizes several calculated metrics. This pipeline must be implemented in a modular fashion, ideally with the possibility of re-using the components to target different datasets.
## Project Structure
```shell
$ tree -F -L 3 -aA --dirsfirst
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
The main objectives we've pursued in our solution to this challenge are the following:
 * **Minimal setup**: Little to no additional dependencies should be needed in order to run the pipeline. Docker & Docker-compose offer a very convenient way to achieve this.
 * **Ease of use**: As the product is aimed for a data analyst audience, we would like to minimize the amount of tool-specific knowledge required to use it. By leveraging airflow and dbt's capabilities we were able to implement a solution that only requires a dataset's description and some metadata in order to extract and load it, and allows to clean and transform it using SQL SELECT statements.
 * **Performance & Scalability**: Because potential users might want to run several of these pipelines in parallel and Kaggle datasets are relatively large, we have aimed to minimize the amount of memory required in the EL process, as well as delegated the transformation process to the database thanks to dbt.

## Implementation
### Overview
For our solution we have chosen to follow an Extract Load Transform (ELT) approach. The dataset is downloaded from Kaggle using the [Kaggle API](https://github.com/Kaggle/kaggle-api), loaded into the database with minimal transformation and then transformed in-database using **dbt**. The output of the dbt models is then used to build the required visualizations, which are rendered and presented in a browser using **Dash**. The process is orchestrated using **Apache Airflow** and all services are containerized using **Docker** and deployed (locally) with **docker-compose**. 
### Design choices
In this section we give some context on the systems that we've chosen, and why we chose them. We tried to use tools that could be used in a production environment, as well as to provide an scalable implementation when possible:
#### Apache Airflow
Airflow is one of the most popular schedulers/orchestrators nowadays and comes with a lot of batteries included. We chose it as our orchestrator because of the way that workflows (dags) are defined in Airflow allows us to dynamically build them from a set of parameters, which in combination with dbt allows us to automate most of the EL pipeline building process. It also has a very nice UI.
#### dbt
The Data Buding Tool (or *dbt*) provides the *T* of *ELT*, and it has gained a lot of traction over the last couple of years. It enables the definition of data transformations as a sequence (a DAG actually) of SQL SELECT statements, which abstracts away a significant chunk of the complexity of building data transformation pipelines. If you know how to write SQL (and a bit of Jinja), you can write pipelines in dbt. It also comes with data validation capabilites thanks to the dbt tests, as well as a mean of data documentation & discovery via the dbt docs (unfortunately, due to timing constraints the current implementation doesn't have a lot in terms of dbt docs). Although the transformations required for this challenge are minimal, we take advantage of the metadata required by dbt to be able to dynamically build pipelines based on dbt configurations.
#### Docker & Docker-compose
They are the de-facto tool for containerizing and deploying applications. Airflow provides a quite nice docker-compose that we had based our implementation on.
#### Dash
Because some degree of data visualization es required, we chose Dash for its simplicity and flexibility. We did not want to have a python script dumping images into a folder, so Dash allows you to create visualizations in python & plotly and publish them as a web page. We explored several other (free) visualization tools like Grafana or Superset that had nicer visuals or more features, but they required too much setup and/or were too specialized (Grafana struggles with data other than time series) so we chose simplicity.

### On credential management
For this challenge we are deploying locally several services that require credentials: 2 postgres databases, airflow, dbt. We have tried to minimize the amount of hardcoded credentials and made it as production-like as possible (within reason) by for example parametrizing dbt profiles to pull credentials from environment variables that are passed into the airflow operator and using airflow connections. Nevertheless, the docker-compose and the bootstrap scripts contain hardcoded (mostly default) credentials to simulate an user introducing them in airflow or a secrets service providing them.  
The only credential that needs to be provided by the user is the Kaggle API key, which we are not able to fake so a real one needs to be used.

### On environment management & the DockerOperator
One of our main goals was to minimize the required setup by running everything inside containers. This posed a challenge for the common practice of creating docker images with the environment for each one of the tasks executed in the Airflow DAG and running them with DockerOperator, as the Docker-on-Docker setup can be tricky depending on the OS and requires dealing with permissions for the docker socket. We also considered running the tasks in PythonVirtualenvOperators, but as dbt is relatively heavy and the venv had to be created and torn down every task run, we weren't convinced with this option either. We eventually opted again for simplicity and packed dbt in the airflow image (luckily without any conflicts on the current versions), and used *PythonOperators* and *BashOperators* to run the tasks. In a production environment with (ideally) a managed service running Airflow we should use DockerImages to isolate the execution environments of the tasks.

### On Custom vs Out-of-the-box Airflow operators
We considered implementing custom Airflow operators to perform the ELT steps, but as we were not doing a lot of reuse and for the sake of simplicity we used the ol' reliable *PythonOperator* and *BashOperator*.

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
### Adding the Kaggle API credentials
The final step before running the dag is to add your Kaggle credentials to the Airflow connections so it can authenticate to the Kaggle API. In the Ariflow UI, navigate to Admin > Connections and on the `kaggle_api` connection click on *edit record*. Once you are on in the *Edit Connection* screen, add your Kaggle username into the `Login` form and your Kaggle key into the `Password` form and press the *Save* button to store the credentials.
### Running the DAG
In order to run the DAG, first toggle the pause/unpause DAG switch to the left of the DAG's name to ON (don't forget to do this, otherwise the DAG won't start without providing any explanation) and hit the *Play* button under *Actions* in the rightmost side of the screen. The DAG takes around a minute to run.

## Querying the data
When the DAG has finished running (and if everything goes well) you should be able to find the data loaded in the postgres database.
You can connect to the database with your favourite SQL client using the following credentials:
```
 - host: localhost
 - dbname: postgres
 - user: admin
 - pass: admin
 - port: 5433
```
The loaded raw data is available in the following tables:
 * `kaggle_raw.accident_information`
 * `kaggle_raw.vehicle_information`




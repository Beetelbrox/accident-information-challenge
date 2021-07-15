# Accident Information Challenge
This repo contains a solution to the Accident Information challenge. In this challenge we're asked to build a data pipeline which downloads the [UK Road Safety: Traffic Accidents and Vehicles](https://www.kaggle.com/tsiaras/uk-road-safety-accidents-and-vehicles) from Kaggle, loads a subset of the data into a postgres database and visualizes several calculated metrics. This pipeline must be implemented in a modular fashion, ideally with the possibility of re-using the components to target different datasets.
## Implementation
### Goals
Our main goal for this project is to implement a solution that allows users to extract any Kaggle dataset, load it into a database and then transform it with the minimal amount of code and knowledge about the underlying systems and tools. In order to achieve this we leverage the capabilities of **Apache Airflow** and **dbt** to build a setup that allows us to define *Pipelines as Code*.
### Overview
For our solution we have chosen to follow an Extract Load Transform (ELT) approach. The dataset is downloaded from Kaggle using the Kaggle python API, loaded into the database with minimal transformation and then transformed in-database using **dbt**. Visualizations are generated using the data in the resulting dbt models and displayed in a browser using **Dash**. The process is orchestrated using **Apache Airflow** and all services are containerized using **Docker** and deployed (locally) with **docker-compose**.  

<IMAGE HERE>  


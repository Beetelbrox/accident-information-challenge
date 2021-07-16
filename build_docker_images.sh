echo "$(pwd)"
docker build docker/airflow/ -t airflow-dbt:0.0.1  
docker build docker/dash/ -t python-dash:0.0.1
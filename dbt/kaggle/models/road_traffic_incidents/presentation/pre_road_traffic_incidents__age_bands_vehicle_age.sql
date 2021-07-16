{{
    config(
        materialized='table'
    )
}}

WITH road_traffic_incidents AS (
    SELECT * FROM {{ ref('stg_road_traffic_incidents__road_traffic_incidents') }}
),
    age_bands_vehicle_age AS (
        SELECT vehicle_age,
               driver_age_band,
               COUNT(*) AS num_accidents
          FROM road_traffic_incidents
         GROUP BY vehicle_age, driver_age_band
    )
SELECT *
FROM age_bands_vehicle_age
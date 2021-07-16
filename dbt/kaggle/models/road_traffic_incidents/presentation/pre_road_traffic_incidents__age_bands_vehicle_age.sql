{{
    config(
        enabled=False
    )
}}

WITH road_traffic_incidents AS (
    SELECT DISTINCT accident_id,
                    age_band_of_driver,
                    age_of_vehicle
      FROM {{ ref('stg_road_traffic_incidents__road_traffic_incidents') }}
),
    age_bands_vehicle_age_working_rel AS (
        SELECT age_of_vehicle,
               age_band_of_driver,
               COUNT(*) AS num_accidents
          FROM road_traffic_incidents
         GROUP BY age_of_vehicle, age_band_of_driver
    ),
    age_bands_vehicle_age AS (
        SELECT age_of_vehicle,
               age_band_of_driver,
               num_accidents,
               ROUND(100 * num_accidents/(SUM(num_accidents) OVER (PARTITION BY age_band_of_driver)), 4) AS pct_accidents
          FROM age_bands_vehicle_age_working_rel
          ORDER BY age_of_vehicle, age_band_of_driver
    )
SELECT *
FROM age_bands_vehicle_age
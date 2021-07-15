WITH road_traffic_incidents AS (
    SELECT * FROM {{ ref('stg_road_traffic_incidents__road_traffic_incidents') }}
),
    agg_vehicle_ages AS (
        SELECT age_of_vehicle,
               COUNT(age_of_vehicle) as num_accidents,
               ROUND(100.0*COUNT(age_of_vehicle)/(SELECT COUNT(age_of_vehicle) FROM road_traffic_incidents), 4) AS pct_accidents
          FROM road_traffic_incidents
         GROUP BY age_of_vehicle
         ORDER BY age_of_vehicle
    )
SELECT *
FROM agg_vehicle_ages
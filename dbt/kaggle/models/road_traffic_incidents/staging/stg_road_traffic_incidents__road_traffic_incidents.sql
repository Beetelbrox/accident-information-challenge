WITH accident_information AS (
    SELECT * FROM {{ ref('base_road_traffic_incidents__accident_information') }}
),
vehicle_information AS (
    SELECT * FROM {{ ref('base_road_traffic_incidents__vehicle_information') }}
),
    road_traffic_incidents AS (
        SELECT ai.accident_id,
               ai.accident_date,
               ai.accident_day_of_week,
               ai.accident_severity,
               vi.driver_age_band,
               vi.vehicle_age,
               vi.driver_home_area_type,
               vi.driver_journey_purpose,
               COUNT(*) AS num_accidents
          FROM accident_information AS ai
            INNER JOIN vehicle_information AS vi
                ON ai.accident_id = vi.accident_id
        GROUP BY ai.accident_id,
                 ai.accident_date,
                 ai.accident_day_of_week,
                 ai.accident_severity,
                 vi.driver_age_band,
                 vi.vehicle_age,
                 vi.driver_home_area_type,
                 vi.driver_journey_purpose
    )
SELECT *
FROM road_traffic_incidents
WITH accident_information AS (
    SELECT * FROM {{ ref('base_road_traffic_incidents__accident_information') }}
),
vehicle_information AS (
    SELECT * FROM {{ ref('base_road_traffic_incidents__vehicle_information') }}
),
    road_traffic_incidents AS (
        SELECT vi.accident_id,
               ai.date,
               ai.day_of_week,
               ai.accident_severity,
               vi.age_band_of_driver,
               vi.age_of_vehicle,
               vi.driver_home_area_type,
               vi.journey_purpose_of_driver
          FROM accident_information AS ai
            INNER JOIN vehicle_information AS vi
                ON ai.id = vi.accident_id
    )
SELECT *
FROM road_traffic_incidents
WITH source AS (
    SELECT * FROM {{ source('road_traffic_incidents', 'vehicle_information') }}
),
    base AS (
        SELECT accident_id :: VARCHAR(13),
               driver_age_band :: VARCHAR(30),
               vehicle_age :: INTEGER,
               driver_home_area_type :: VARCHAR(30),
               driver_journey_purpose :: VARCHAR(30)
          FROM source
    )
SELECT *
  FROM base
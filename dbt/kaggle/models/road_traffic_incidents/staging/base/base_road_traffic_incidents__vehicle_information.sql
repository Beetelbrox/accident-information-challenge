WITH source AS (
    SELECT * FROM {{ source('road_traffic_incidents', 'vehicle_information') }}
),
    base AS (
        SELECT accident_index AS accident_id,
               age_band_of_driver,
               age_of_vehicle,
               driver_home_area_type,
               journey_purpose_of_driver
          FROM source
    )
SELECT *
  FROM base
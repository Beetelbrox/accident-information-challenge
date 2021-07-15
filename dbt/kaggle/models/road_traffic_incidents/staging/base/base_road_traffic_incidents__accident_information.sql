WITH source AS (
    SELECT * FROM {{ source('road_traffic_incidents', 'accident_information') }}
),
    base AS (
        SELECT accident_index AS id,
               date,
               day_of_week,
               accident_severity
          FROM source
    )
SELECT *
  FROM base
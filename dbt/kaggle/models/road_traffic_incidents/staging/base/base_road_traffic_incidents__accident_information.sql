WITH source AS (
    SELECT * FROM {{ source('road_traffic_incidents', 'accident_information') }}
),
    base AS (
        SELECT accident_id :: VARCHAR(13),
               accident_date :: DATE,
               accident_day_of_week :: VARCHAR(10),
               accident_severity :: VARCHAR(7)
          FROM source
    )
SELECT *
  FROM base
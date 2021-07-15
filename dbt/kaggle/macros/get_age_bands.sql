{% macro get_age_bands() %}

{% set age_bands_query %}
SELECT DISTINCT age_band_of_driver
FROM {{ ref('stg_road_traffic_incidents__road_traffic_incidents') }}
ORDER BY 1
{% endset %}

{% if execute %}
{% set results = run_query(age_bands_query) %}
{% set results_list = results.columns[0].values() %}
{% else %}
{% set results_list = [] %}
{% endif %}

{{ return(results_list) }}

{% endmacro %}
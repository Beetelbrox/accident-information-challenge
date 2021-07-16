{% test assert_num_loaded_rows(model) %}
    {% if execute %}
        {%- set source_node = graph.sources.values()
            | selectattr("resource_type", "equalto", "source")
            | selectattr("name", "equalto", model.identifier)
            | first
        -%}
        WITH row_count AS (
            SELECT COUNT(*) as num_rows
            FROM {{ model }}
        )
        SELECT *
        FROM row_count
        WHERE num_rows <> {{source_node.meta.expected_rows}}
    {% endif %}
{%- endtest -%}
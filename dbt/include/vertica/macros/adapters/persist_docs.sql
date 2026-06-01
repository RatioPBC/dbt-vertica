{#
  These macros are sourced from the postgres adapter, with the prefix changed from postgres to vertica
  https://github.com/dbt-labs/dbt-adapters/blob/a679948fedb4bf081c60d9d3bca26acb4116dc9c/dbt-postgres/src/dbt/include/postgres/macros/adapters.sql#L185
#}

{#
  Vertica's COMMENT ON COLUMN supports only tables and projections -- there is no
  syntax for commenting on the columns of a view, and attempting it raises
  "Column <view>.<col> does not exist" even when the column genuinely exists
  (https://docs.vertica.com/24.2.x/en/sql-reference/statements/comment-on-statements/comment-on-column/).
  Whole-view comments are still applied via vertica__alter_relation_comment, so we
  only skip column-level comments for non-table relations.
#}
{% macro vertica__alter_column_comment(relation, column_dict) %}
  {% if relation.type != 'table' %}
    {{ return('') }}
  {% endif %}
  {% set existing_columns = adapter.get_columns_in_relation(relation) | map(attribute="name") | list %}
  {% for column_name in column_dict if (column_name in existing_columns) %}
    {% set comment = column_dict[column_name]['description'] %}
    {% set escaped_comment = vertica_escape_comment(comment) %}
    comment on column {{ relation }}.{{ adapter.quote(column_name) if column_dict[column_name]['quote'] else column_name }} is {{ escaped_comment }};
  {% endfor %}
{% endmacro %}

{% macro vertica__alter_relation_comment(relation, comment) %}
  {% set escaped_comment = vertica_escape_comment(comment) %}
  comment on {{ relation.type }} {{ relation }} is {{ escaped_comment }};
{% endmacro %}

{#
  Render the comment as a standard SQL single-quoted string literal, doubling any
  embedded single quotes. Unlike dollar-quoting ($$...$$), this imposes no forbidden
  substring on the comment text, so arbitrary content -- including literal `$$`, which
  dbt's own persist_docs fixtures embed -- round-trips safely.
  https://docs.vertica.com/24.2.x/en/sql-reference/language-elements/literals/string-literals/
#}
{% macro vertica_escape_comment(comment) -%}
  {% if comment is not string %}
    {% do exceptions.raise_compiler_error('cannot escape a non-string: ' ~ comment) %}
  {% endif %}
  '{{ comment | replace("'", "''") }}'
{%- endmacro %}

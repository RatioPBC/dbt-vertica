{% macro vertica__get_catalog(information_schema, schemas) -%}


   {% set query %}     

        with tables as (
              {{ vertica__get_catalog_tables_sql(information_schema) }}
            {{ vertica__get_catalog_schemas_where_clause_sql(schemas) }}
             ), 
        columns as  (
             {{ vertica__get_catalog_columns_sql(information_schema) }}
             {{ vertica__get_catalog_schemas_where_clause_sql(schemas) }}
          
        )
     
        {{vertica__get_catalog_results_sql ()}}

         {%- endset -%}
          {{ return(run_query(query)) }}


 
{%- endmacro %}

    
  
  


{% macro vertica__get_catalog_relations(information_schema, relations) -%}
   {% set query %}

           
            with tables as (
                {{ vertica__get_catalog_tables_sql(information_schema) }}
                {{ vertica__get_catalog_relations_where_clause_sql(relations) }}
             ), 
        columns as (
             {{ vertica__get_catalog_columns_sql(information_schema) }}
             {{ vertica__get_catalog_relations_where_clause_sql(relations) }}
          
        )
    {{vertica__get_catalog_results_sql ()}}
         {%- endset -%}

          {{ return(run_query(query)) }}

{%- endmacro %}








{% macro vertica__get_catalog_tables_sql(information_schema) -%}
   select * from  (
 select
    '{{ information_schema.database }}' table_database
    , tab.table_schema
    , tab.table_name
    , 'TABLE' table_type
    , tab_cmt.comment table_comment
    , tab.owner_name table_owner
    , col.column_name
    , col.ordinal_position column_index
    , col.data_type column_type
    , col_cmt.comment column_comment
    from v_catalog.tables tab
    join v_catalog.columns col on tab.table_id = col.table_id
    left join v_catalog.comments tab_cmt
        on tab.table_id = tab_cmt.object_id and tab_cmt.object_type = 'TABLE'
    left join v_catalog.comments col_cmt
        on tab.table_id = col_cmt.object_id and col_cmt.object_type = 'COLUMN'
        and col.column_name = col_cmt.child_object
    union all
    select
    '{{ information_schema.database }}' table_database
    , vw.table_schema
    , vw.table_name
    , 'VIEW' table_type
    , vw_cmt.comment table_comment
    , vw.owner_name table_owner
    , col.column_name
    , col.ordinal_position column_index
    , col.data_type column_type
    , col_cmt.comment column_comment
    from v_catalog.views vw
    join v_catalog.view_columns col on vw.table_id = col.table_id
    left join v_catalog.comments vw_cmt
        on vw.table_id = vw_cmt.object_id and vw_cmt.object_type = 'VIEW'
    left join v_catalog.comments col_cmt
        on vw.table_id = col_cmt.object_id and col_cmt.object_type = 'COLUMN'
        and col.column_name = col_cmt.child_object

   )  anything
{%- endmacro %}
 


{% macro vertica__get_catalog_columns_sql(information_schema) -%}
    select * from  ( select
       '{{ information_schema.database }}' table_database , 
    table_schema 
    ,table_name
    , column_name
    , ordinal_position column_index
    , data_type column_type
         
    from v_catalog.columns 

         union all

     select 
    '{{ information_schema.database }}' table_database ,
    table_schema 
    ,table_name
    ,  column_name
    , ordinal_position column_index
    , data_type column_type
    
    from v_catalog.view_columns
    )  y
{%- endmacro %}

{% macro vertica__get_catalog_results_sql() -%}
    select *
    from tables
    join columns using ("table_database", "table_schema", "table_name", "column_name", "column_index", "column_type");
   
{%- endmacro %}

{% macro vertica__get_catalog_schemas_where_clause_sql(schemas) -%}
        where   
        (
          {%- for schema in schemas -%} 
         
      
            lower(table_schema) = lower('{{ schema }}') {%- if not loop.last %} or {% endif %}
          {%- endfor -%}
        )
         
         order by table_schema, table_name, column_index

{%- endmacro %}


{% macro vertica__get_catalog_relations_where_clause_sql(relations) -%}
    where (
        {%- for relation in relations -%}
            {% if relation.schema and relation.identifier %}
                (
                    upper("table_schema") = upper('{{ relation.schema }}')
                    and upper("table_name") = upper('{{ relation.identifier }}')
                )
            {% elif relation.schema %}
                (
                    upper("table_schema") = upper('{{ relation.schema }}')
                )
            {% else %}
                {% do exceptions.raise_compiler_error(
                    '`get_catalog_relations` requires a list of relations, each with a schema'
                ) %}
            {% endif %}

            {%- if not loop.last %} or {% endif -%}
        {%- endfor -%}
    )
{%- endmacro %}

from types import SimpleNamespace
import pytest
from dbt.tests.util import run_dbt


def run_macro(project, macro_name, **kwargs):
    with project.adapter.connection_named("_test_catalog"):
        return project.adapter.execute_macro(macro_name, kwargs=kwargs)


def exec_sql(project, sql):
    with project.adapter.connection_named("_test_setup"):
        project.adapter.connections.get_thread_connection().handle.autocommit = True
        project.adapter.execute(sql, auto_begin=False, fetch=False)


class TestGetCatalogComments:
    @pytest.fixture(scope="class", autouse=True)
    def setup_relations(self, project):
        schema = project.test_schema
        exec_sql(
            project,
            f"""
          CREATE TABLE {schema}.cat_tbl (id int, name varchar(50));
          COMMENT ON TABLE {schema}.cat_tbl IS 'table comment A';
          COMMENT ON COLUMN {schema}.cat_tbl.id IS 'col comment id';
          COMMENT ON COLUMN {schema}.cat_tbl.name IS 'col comment name';
          CREATE VIEW {schema}.cat_vw AS SELECT id FROM {schema}.cat_tbl;
          COMMENT ON VIEW {schema}.cat_vw IS 'view comment B';
      """,
        )
        yield

    def test_table_comments_in_catalog(self, project):
        info_schema = SimpleNamespace(database=project.database)
        table = run_macro(
            project,
            "vertica__get_catalog",
            information_schema=info_schema,
            schemas=[project.test_schema],
        )
        rows = {(r["table_name"], r["column_name"]): r for r in table.rows}
        assert len(rows) == 3
        assert rows[("cat_tbl", "id")]["table_comment"] == "table comment A"
        assert rows[("cat_tbl", "id")]["column_comment"] == "col comment id"
        assert rows[("cat_tbl", "name")]["column_comment"] == "col comment name"

    def test_views_present_with_relation_comment(self, project):
        info_schema = SimpleNamespace(database=project.database)
        table = run_macro(
            project,
            "vertica__get_catalog",
            information_schema=info_schema,
            schemas=[project.test_schema],
        )
        view_rows = [r for r in table.rows if r["table_name"] == "cat_vw"]
        assert len(view_rows) == 1
        assert view_rows, "view missing from catalog"
        assert view_rows[0]["table_type"] == "VIEW"
        assert view_rows[0]["table_comment"] == "view comment B"
        assert view_rows[0]["column_comment"] is None

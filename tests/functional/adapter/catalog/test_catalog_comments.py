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


class TestGetCatalogVolatile:
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

    def get_catalog(self, project):
        info_schema = SimpleNamespace(database=project.database)
        return run_macro(
            project,
            "vertica__get_catalog_volatile",
            information_schema=info_schema,
            schemas=[project.test_schema],
        )

    def test_result_columns(self, project):
        table = self.get_catalog(project)
        assert list(table.column_names) == [
            "id",
            "table_database",
            "table_schema",
            "table_name",
            "table_type",
            "table_owner",
            "column_id",
            "column_name",
            "column_index",
            "column_type",
            "table_comment",
            "column_comment",
        ]

    def test_result_values(self, project):
        table = self.get_catalog(project)
        owner = project.adapter.config.credentials.username
        rows = {
            (r["table_name"], r["column_name"]): dict(zip(table.column_names, r))
            for r in table.rows
        }
        assert len(rows) == 3

        tbl_id = rows[("cat_tbl", "id")]["id"]
        vw_id = rows[("cat_vw", "id")]["id"]
        assert tbl_id is not None
        assert vw_id is not None
        assert tbl_id != vw_id

        assert rows[("cat_tbl", "id")] == {
            "id": tbl_id,
            "table_database": project.database,
            "table_schema": project.test_schema,
            "table_name": "cat_tbl",
            "table_type": "TABLE",
            "table_owner": owner,
            "column_id": f"{tbl_id}-1",
            "column_name": "id",
            "column_index": 1,
            "column_type": "int",
            "table_comment": "table comment A",
            "column_comment": "col comment id",
        }
        assert rows[("cat_tbl", "name")] == {
            "id": tbl_id,
            "table_database": project.database,
            "table_schema": project.test_schema,
            "table_name": "cat_tbl",
            "table_type": "TABLE",
            "table_owner": owner,
            "column_id": f"{tbl_id}-2",
            "column_name": "name",
            "column_index": 2,
            "column_type": "varchar(50)",
            "table_comment": "table comment A",
            "column_comment": "col comment name",
        }
        assert rows[("cat_vw", "id")] == {
            "id": vw_id,
            "table_database": project.database,
            "table_schema": project.test_schema,
            "table_name": "cat_vw",
            "table_type": "VIEW",
            "table_owner": owner,
            "column_id": f"{vw_id}-1",
            "column_name": "id",
            "column_index": 1,
            "column_type": "int",
            "table_comment": "view comment B",
            "column_comment": None,
        }

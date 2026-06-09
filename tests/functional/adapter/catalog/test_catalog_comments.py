from types import SimpleNamespace
import pytest


def run_macro(project, macro_name, **kwargs):
    with project.adapter.connection_named("_test_catalog"):
        return project.adapter.execute_macro(macro_name, kwargs=kwargs)


def exec_sql(project, sql):
    with project.adapter.connection_named("_test_setup"):
        project.adapter.connections.get_thread_connection().handle.autocommit = True
        project.adapter.execute(sql, auto_begin=False, fetch=False)


class CatalogCommentsBase:
    macro_name = None

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
            self.macro_name,
            information_schema=info_schema,
            schemas=[project.test_schema],
        )

    def get_rows(self, project):
        """Catalog rows keyed by (table_name, column_name)."""
        table = self.get_catalog(project)
        rows = {
            (r["table_name"], r["column_name"]): dict(zip(table.column_names, r))
            for r in table.rows
        }
        assert len(rows) == len(table.rows), "duplicate catalog rows"
        return rows

    def test_table_comments_in_catalog(self, project):
        rows = self.get_rows(project)
        assert len(rows) == 3
        assert rows[("cat_tbl", "id")]["table_comment"] == "table comment A"
        assert rows[("cat_tbl", "id")]["column_comment"] == "col comment id"
        assert rows[("cat_tbl", "name")]["column_comment"] == "col comment name"

    def test_views_present_with_relation_comment(self, project):
        view_row = self.get_rows(project)[("cat_vw", "id")]
        assert view_row["table_type"] == "VIEW"
        assert view_row["table_comment"] == "view comment B"
        assert view_row["column_comment"] is None


class TestGetCatalogComments(CatalogCommentsBase):
    macro_name = "vertica__get_catalog"


class TestGetCatalogVolatile(CatalogCommentsBase):
    macro_name = "vertica__get_catalog_volatile"

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
        rows = self.get_rows(project)
        assert len(rows) == 3

        tbl_id = rows[("cat_tbl", "id")]["id"]
        vw_id = rows[("cat_vw", "id")]["id"]
        assert tbl_id is not None
        assert vw_id is not None
        assert tbl_id != vw_id

        def expected_row(
            rel_id, table_name, table_type, table_comment,
            column_name, column_index, column_type, column_comment,
        ):
            return {
                "id": rel_id,
                "table_database": project.database,
                "table_schema": project.test_schema,
                "table_name": table_name,
                "table_type": table_type,
                "table_owner": project.adapter.config.credentials.username,
                "column_id": f"{rel_id}-{column_index}",
                "column_name": column_name,
                "column_index": column_index,
                "column_type": column_type,
                "table_comment": table_comment,
                "column_comment": column_comment,
            }

        assert rows[("cat_tbl", "id")] == expected_row(
            tbl_id, "cat_tbl", "TABLE", "table comment A",
            "id", 1, "int", "col comment id",
        )
        assert rows[("cat_tbl", "name")] == expected_row(
            tbl_id, "cat_tbl", "TABLE", "table comment A",
            "name", 2, "varchar(50)", "col comment name",
        )
        assert rows[("cat_vw", "id")] == expected_row(
            vw_id, "cat_vw", "VIEW", "view comment B",
            "id", 1, "int", None,
        )

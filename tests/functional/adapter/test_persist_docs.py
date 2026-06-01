import json

from dbt.tests.util import run_dbt

from dbt.tests.adapter.persist_docs.test_persist_docs import (
    BasePersistDocs,
    BasePersistDocsAllColumnsMissing,
    BasePersistDocsColumnMissing,
    BasePersistDocsCommentOnQuotedColumn,
    BasePersistDocsQuotedColumnCaseSensitive,
    BasePersistDocsQuotedDescriptionNotAppliedOnMismatch,
)


# Verifies relation- and column-level docs from YAML are persisted as comments
# (queryable in v_catalog.comments) for both table and view materializations,
# including the escaping edge cases (quotes, single quotes, literal $$, -- and
# /* */). Exercises vertica__alter_relation_comment, vertica__alter_column_comment,
# and vertica_escape_comment.
class TestPersistDocsVertica(BasePersistDocs):
    # Overridden from the base suite: Vertica's COMMENT ON COLUMN supports only
    # tables and projections, not views, so view *column* comments can never be
    # persisted (see vertica__alter_column_comment). View *relation* comments and
    # all *table* comments still apply, so we assert has_column_comments=False for
    # the view rather than the base default of True.
    def test_has_comments_pglike(self, project):
        run_dbt(["docs", "generate"])
        with open("target/catalog.json") as fp:
            catalog_data = json.load(fp)
        assert "nodes" in catalog_data
        assert len(catalog_data["nodes"]) == 4

        table_node = catalog_data["nodes"]["model.test.table_model"]
        self._assert_has_table_comments(table_node)

        view_node = catalog_data["nodes"]["model.test.view_model"]
        self._assert_has_view_comments(view_node, has_column_comments=False)

        no_docs_node = catalog_data["nodes"]["model.test.no_docs_model"]
        self._assert_has_view_comments(no_docs_node, False, False)


# A column declared in YAML but absent from the model must not break the run and
# must emit a warning. Exercises the `column_name in existing_columns` filter in
# vertica__alter_column_comment.
class TestPersistDocsColumnMissingVertica(BasePersistDocsColumnMissing):
    pass


# Every documented column is invalid: the run must still succeed (the filter
# skips them all) and warn about each missing column.
class TestPersistDocsAllColumnsMissingVertica(BasePersistDocsAllColumnsMissing):
    pass


# With quote: true the documented identifier comparison must be case-sensitive,
# so a documented `MyCol` does not match the physical (lowercased) column and is
# reported as missing rather than silently applied.
class TestPersistDocsQuotedColumnCaseSensitiveVertica(BasePersistDocsQuotedColumnCaseSensitive):
    pass


# With quote: true and a case-mismatched physical column, the documented
# description must not leak onto a differently-cased physical column even though
# Vertica's case-insensitive matching could otherwise apply it.
class TestPersistDocsQuotedDescriptionNotAppliedOnMismatchVertica(
    BasePersistDocsQuotedDescriptionNotAppliedOnMismatch
):
    pass


# Column comment where the column name must be quoted (quote: true). Exercises
# the adapter.quote(column_name) branch of vertica__alter_column_comment.
class TestPersistDocsCommentOnQuotedColumnVertica(BasePersistDocsCommentOnQuotedColumn):
    pass

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
# including the escaping edge cases (quotes, dollar-quoting, -- and /* */).
# Exercises vertica__alter_relation_comment, vertica__alter_column_comment, and
# vertica_escape_comment via the dollar-quoted ($$...$$) comment literals.
class TestPersistDocsVertica(BasePersistDocs):
    pass


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

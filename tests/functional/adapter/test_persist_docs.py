from dbt.tests.adapter.persist_docs.test_persist_docs import (
    BasePersistDocs,
    BasePersistDocsColumnMissing,
    BasePersistDocsCommentOnQuotedColumn,
)


# Verifies relation- and column-level docs from YAML are persisted as comments
# (queryable in v_catalog.comments) for both table and view materializations,
# including the escaping edge cases (quotes, dollar-quoting, -- and /* */).
class TestPersistDocsVertica(BasePersistDocs):
    pass


# A column declared in YAML but absent from the model must not break the run.
class TestPersistDocsColumnMissingVertica(BasePersistDocsColumnMissing):
    pass


# Column comment where the column name must be quoted (quote: true).
class TestPersistDocsCommentOnQuotedColumnVertica(BasePersistDocsCommentOnQuotedColumn):
    pass

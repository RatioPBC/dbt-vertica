# AGENTS.md — dbt Vertica adapter repo

This file instructs AI coding agents on how to navigate, build, test, and contribute to this repository.

## Repository Layout

```text
dbt-adapters/
├── dbt/adapters/vertica    # Vertica adapter
├── tests/                  # test suite
```

## Environment Setup

All commands are run from the repo root. Also take into account the tasks in `mise.toml`.

## Testing

### Unit Tests (no database required)

```bash
pytest tests/unit/

# Run a specific test
pytest tests/unit/test_base.py
```

Unit tests live in `tests/unit/`. They test Python logic without a live database.

### Integration Tests (requires live database)

```bash
pytest tests/functional/adapter/
```

Integration tests live in `tests/functional/`.

### Test Fixture Pattern

Tests inherit from `dbt-tests-adapter` base classes:

```python
from dbt.tests.adapter.basic import BaseSimpleMaterializations

class TestSimpleMaterializations(BaseSimpleMaterializations):
    pass
```

## Making Changes

### Where to Make Changes

- **SQL behavior changes**: edit macros in `src/dbt/include/vertica/macros/`
- **Python behavior changes**: edit `src/dbt/adapters/vertica/impl.py`
- **Connection/credential changes**: edit `src/dbt/adapters/vertica/connections.py`
- **Relation config changes**: edit `src/dbt/adapters/vertica/relation.py` or `relation_configs/`
- **Base framework changes**: make changes in `dbt-adapters/` and check impact on all adapters

### Macro Override Convention

Override default macros by prefixing with the adapter name:

```sql
-- src/dbt/include/vertica/macros/adapters.sql
{% macro vertica__list_relations_without_caching(schema_relation) %}
    -- adapter-specific SQL
{% endmacro %}
```

### Adding Adapter Methods Available in Macros

Use the `@available` decorator:

```python
from dbt.adapters.base.meta import available

class MyAdapter(SQLAdapter):
    @available
    def my_method(self):
        """Callable in Jinja as adapter.my_method()"""
        pass
```

### Declaring Capabilities

```python
from dbt.adapters.capability import Capability, CapabilitySupport, CapabilityDict, Support

class MyAdapter(SQLAdapter):
    _capabilities = CapabilityDict({
        Capability.SchemaMetadataByRelations: CapabilitySupport(support=Support.Full),
    })
```

## Dependency Relationships

When modifying base packages, check downstream impact:

- Changes to `dbt-adapters` affect **all** adapters
- Changes to `dbt-postgres` affect **dbt-redshift**
- Changes to `dbt-tests-adapter` affect all adapter test suites

## Security Rules

- Never commit `test.env` or any file containing credentials
- Never hardcode credentials, tokens, or access keys in source files
- Treat `test.env.example` as the authoritative list of required env vars (no values)

## Pull Request Checklist

- [ ] Unit tests pass
- [ ] Integration tests pass against a real database (if changing SQL or connection logic)
- [ ] `test.env` not committed
- [ ] New adapter methods decorated with `@available` if needed in macros
- [ ] Capabilities updated if new features are added

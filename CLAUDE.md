# dbt Vertica adapter repo

This file instructs AI coding agents on how to navigate, build, test, and contribute to this repository.

## Repository Layout

```text
dbt-vertica/
├── dbt/adapters/vertica       # Vertica adapter (Python)
├── dbt/include/vertica/macros # adapter macros (SQL)
├── tests/                     # test suite
├── pyproject.toml             # package metadata + deps (hatchling backend)
├── uv.lock                    # pinned dependency lockfile (committed)
└── mise.toml                  # provisioned tools + task runner
```

## Environment Setup

All commands are run from the repo root. This project uses **mise** to provision
tools (Python, `vsql`, `uv`) and **uv** to manage the Python environment
(`pyproject.toml` + `uv.lock`). Also take into account the tasks in `mise.toml`.

In particular:

- install pinned tools with `mise install`
- create the venv and install deps (incl. editable package) with `mise run setup` (runs `uv sync`)
- start Vertica with `mise run vertica:start`
- query Vertica with `mise run vertica:query "select * from..."`
- never execute queries via `docker exec`

The `dbt` package is a namespace package shared with dbt-core. The editable
install (via the hatchling backend's `dev-mode-dirs`) emits a plain `.pth` path
entry, not an import finder, so this repo's `dbt` namespace merges with
dbt-core's. Do **not** run `pip install -e .` — it reintroduces namespace
shadowing and breaks the test suite. Use `mise run setup` / `uv sync`.

To change dependencies, edit `pyproject.toml`, then `mise run setup` (or
`mise run deps`) to sync and `mise run lock` to refresh `uv.lock`.

## Testing

Tests run inside the uv-managed venv. The `mise run test` task wraps
`uv run pytest`; you can also call `uv run pytest ...` directly.

### Unit Tests (no database required)

```bash
mise run test tests/unit/

# Run a specific test
uv run pytest tests/unit/test_base.py
```

Unit tests live in `tests/unit/`. They test Python logic without a live database.

### Integration Tests (requires live database)

Start Vertica first with `mise run vertica:start`, then:

```bash
mise run test                 # whole suite (defaults to tests/)
mise run test:basic           # basic functional adapter tests
uv run pytest tests/functional/adapter/
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

- **SQL behavior changes**: edit macros in `dbt/include/vertica/macros/`
- **Python behavior changes**: edit `dbt/adapters/vertica/impl.py`
- **Connection/credential changes**: edit `dbt/adapters/vertica/connections.py`
- **Relation config changes**: edit `dbt/adapters/vertica/relation.py` or `relation_configs/`
- **Base framework changes**: make changes in `dbt-adapters/` and check impact on all adapters

### Macro Override Convention

Override default macros by prefixing with the adapter name:

```sql
-- dbt/include/vertica/macros/adapters.sql
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
- Changes to `dbt-tests-adapter` affect all adapter test suites

## Security Rules

- Never commit
- Never hardcode credentials, tokens, or access keys in source files
- Treat the `[env]` section in the mise.toml file as the authoritative list of environment variables

## Pull Request Checklist

- [ ] Unit tests pass
- [ ] Integration tests pass against a real database (if changing SQL or connection logic)
- [ ] New adapter methods decorated with `@available` if needed in macros
- [ ] Capabilities updated if new features are added

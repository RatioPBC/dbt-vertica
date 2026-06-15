# dbt-vertica

[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)

[dbt](https://www.getdbt.com/) adapter for [Vertica](https://www.vertica.com/). The adapter uses [vertica-python](https://github.com/vertica/vertica-python) to connect to your Vertica database.

For more information on using dbt with Vertica, consult the [Vertica-Setup](https://docs.getdbt.com/reference/warehouse-setups/vertica-setup) and [Configuration](https://docs.getdbt.com/reference/resource-configs/vertica-configs) pages.

## dbt-vertica Versions Tested

dbt-vertica has been developed using the following software and versions:

* Vertica Server v25.1.0-0
* Python 3.11
* vertica-python client 1.3.1
* dbt-core 1.11.0

## Supported Features

### dbt Core Features

Below is a table for what features the current Vertica adapter supports for dbt. This is constantly improving and changing as both dbt adds new functionality, as well as the dbt-vertica driver improves. This list is based upon dbt 1.3.0

|                dbt Core Features                  | Supported   |
| ------------------------------------------------- | ----------- |
| Table Materializations                            | Yes         |
| Ephemeral Materializations                        | Yes         |
| View Materializations                             | Yes         |
| Incremental Materializations - Append             | Yes         |
| Incremental Materailizations - Merge              | Yes         |
| Incremental Materializations - Delete+Insert      | Yes         |
| Incremental Materializations - Insert_Overwrite   | Yes         |
| Snapshots - Timestamp                             | Yes         |
| Snapshots - Check Cols                            | No          |
| Seeds                                             | Yes         |
| Tests                                             | Yes         |
| Documentation                                     | Yes         |
| External Tables                                   | Untested    |
| Unit Testing                                      | Yes         |

* **Yes** - Supported, and tests pass.
* **No** - Not supported or implemented.
* **Untested** - May support out of the box, though hasn't been tested.
* **Passes Test** - The tests have passed, though haven't tested in a production like environment.

## Installation

```text
$ pip install dbt-vertica
```

You don't need to install dbt separately. Installing `dbt-vertica` will also install `dbt-core` and `vertica-python`.

## Sample Profile Configuration

```profiles.yml

your-profile:
  outputs:
    dev:
      type: vertica # Don't change this!
      host: [hostname]
      port: [port] # or your custom port (optional)
      username: [your username] 
      password: [your password] 
      database: [database name] 
      oauth_access_token: [access token]
      schema: [dbt schema] 
      connection_load_balance: True
      backup_server_node: [list of backup hostnames or IPs]
      retries: [1 or more]
      threads: [1 or more] 
      autocommit: False
  target: dev

```

### Description of Profile Fields

| Property                  | Required? | Default Value     | Example       | Description |
| ------------------------- | --------- | ----------------- | ------------- | ----------- |
| type                      | Yes       | None              | vertica       | The specific adapter to use. |
| host                      | Yes       | None              | 127.0.0.1     | The host name or IP address of any active node in the Vertica Server. |
| port                      | Yes       | 5433              | 5433          | The port to use, default or custom. |
| username                  | Yes       | None              | dbadmin       | The username to use to connect to the server. |
| password                  | Yes       | None              | my_password   | The password to use for authenticating to the server. |
| database                  | Yes       | None              | my_db         | The name of the database running on the server. |
| oauth_access_token        | No        | ""                | "an-token"    | To authenticate via OAuth, provide an OAuth Access Token that authorizes a user to the database. |
| schema                    | No        | None              | VMart         | The schema to build models into. |
| connection_load_balance   | No        | true              | true          | A Boolean value that indicates whether the connection can be redirected to a host in the database other than host. |
| backup_server_node        | No        | none              | example [^1]  | List of hosts to connect to if the primary host specified in the connection (host, port) is unreachable. Each item in the list should be either a host string (using default port 5433) or a (host, port) tuple. A host can be a host name or an IP address. |
| retries                   | No        | 2                 | 3             | The retry times after an unsuccessful connection. |
| threads                   | No        | 1                 | 3             | The number of threads the dbt project will run on. |
| autocommit                | Yes       | False             | True          | Connection autocommit(True/False) |
| label                     | No        | A generated label | dbt_dbadmin   | A session label to identify the connection. |

[^1]: `['123.123.123.123','www.abc.com',('123.123.123.124',5433)]`

For more information on Vertica’s connection properties please refer to [Vertica-Python](https://github.com/vertica/vertica-python#create-a-connection) Connection Properties.

## Changelog

See the [changelog](https://github.com/vertica/dbt-vertica/blob/main/CHANGELOG.md)

## Contributing guidelines

Have a bug or an idea? Please see [CONTRIBUTING.md](https://github.com/vertica/dbt-vertica/blob/main/CONTRIBUTING.md) for details

## Develop

```bash
# start vertica in a new terminal
mise run vertica:start
# if you need vertica sql console access to the running container
mise run vertica:vsql
# if you need console access to the running container
mise run vertica:bash
# to actually get deps installed
mise run setup
# testing...
mise run test:basic
# all tests
mise run test
# a specific test
mise run test tests/functional/adapter/concurrency/test_concurrency.py
# stop vertica if desired
mise run vertica:stop
```

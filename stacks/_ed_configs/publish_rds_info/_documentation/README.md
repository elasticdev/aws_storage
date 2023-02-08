**Description**
  - Publishes the RDS information on the ED dashboard
  - Fetches information in ED's resource database.
  - Meant to be a substack and called by a stack that installs RDS

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| db_instance_name   | name of the RDS instance                | string   | None         |
| db_root_user   | root user for RDS                 | string   | None         |
| db_root_password   | root password RDS                 | string   | None         |

**Optional**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| db_name   | db name                  | string   | None         |
| db_user   | the user of the db                 | string   | None         |
| db_password   | the password of the db                 | string   | None         |
| publish_creds   | whether to display credentials on the ED dashboard                 | boolean   | True         |

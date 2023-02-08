**Description**
  - The stack that creates an Elastic Container Repository in AWS (ecr) for docker images if it doesn't exists.
  - If the ecr exists, it will not do anything.

**Required**
  - Provide AWS credentials reference in yml that has permission to create the ecr.

**Optional**

- either name or docker_repo needs to be specify

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| name   | name of the repository                 | string   | None         |
| docker_repo   | name of the repository with a key "docker_repo"                | string   | None         |
| aws_default_region   | default aws region               | string   | us-east-1         |


**Sample entry**

```
infrastructure:
   ecr_repo:
       stack_name: elasticdev:::ecr_repo
       arguments:
          name: flask_sample
       credentials:
           - reference: aws_2
             orchestration: true
```

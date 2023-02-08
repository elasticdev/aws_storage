**Description**

  - The stack creates a simple dynamodb

**Required**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| dynamodb_name   | name of the dynamodb table | string   |        |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| aws_default_region   | default aws region               | string   | us-east-1         |
| hash_key   | the hash key of the dynamodb table | string   |  \_id      |
| billing_mode   | pay per request | string   |  PAY_PER_REQUEST | 
| cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |

**Sample entry**

```
global_arguments:
   aws_default_region: eu-west-1
labels:
   general: 
     environment: dev
     purpose: test
infrastructure:
   dynamodb:
       stack_name: elasticdev:::aws_dynamodb
       arguments:
          dynamodb_name: example-dynamodb-table
       labels:
          - general
       credentials:
           - reference: eval-ed-iam
             orchestration: true
```

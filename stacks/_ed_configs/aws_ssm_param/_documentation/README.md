**Description**

  - The stack uploads values into aws ssm parameter store

**Required**
| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| ssm_key   | ssm key for the parameter store                 | string   | random         |
| ssm_value   | ssm value for the parameter store                 | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| aws_default_region   | default aws region               | string   | us-east-1         |
| ssm_description   | ssm description for the parameter store                 | string   | None         |
| ssm_type   | ssm type for the parameter store                 | choice   | SecureString(default),String         |

**Sample entry**

```
infrastructure:
   ssm:
       stack_name: elasticdev:::aws_parameter_store
       arguments:
          ssm_key: key123
          ssm_value: hello123
       credentials:
           - reference: ec2
             orchestration: true
```

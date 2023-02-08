**Description**

  - The stack creates a s3 bucket in aws.

**Required**
| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| bucket   | bucket in aws | string   | random         |
| acl   | acl for bucket | private/public   | private         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| aws_default_region   | default aws region               | string   | us-east-1         |
| force_destroy   | force_destroy for bucket if destroying| string   | None         |
| versioning   | versioning for bucket assets| string   | None         |
| enable_lifecycle   | enable_lifecycle for bucket                 | string   | None         |
| expire_days   | expire_days for bucket assets only if lifecycle is enabled                | int   | None         |
| noncurrent_version_expiration   | noncurrent_version_expiration for bucket assets only if lifecycle is enabled | int   | None         |
| cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |

**Sample entry**

```
infrastructure:
   s3:
       stack_name: elasticdev:::aws_s3_bucket
       arguments:
          bucket: test4532532
          acl: private
          enable_lifecycle: true
          expire_days: 7
          publish_to_saas: true
       credentials:
           - reference: ec2
             orchestration: true
```

**Description**

  - The stack creates RDS in an existing VPC

**Infrastructure**

  - expects an existing VPC/security groups created by ED (e.g. elasticdev:::aws_vpc-simple)

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vpc_name   | name of the vpc                 | string   | None         |
| rds_name   | the name given to the rds instance | string   | None         |
| sg_id   | the security group id for the rds instance | string   | None         |
| subnet_ids   | the subnet_ids separated by comma - csv - for rds instance | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| aws_default_region   | the default aws region               | string   | us-west-1         |
| master_username   | the master username for rds               | string   | random        |
| master_password   | the master password for rds               | string   | random        |
| engine | the rds engine | string | MySQL   |
| engine_version | the rds engine version | string | 5.7   |
| allocated_storage | the rds storage size | string | 10   |
| db_name | the db_name to create in rds | string | random   |
| instance_class | the instance_class for rds instance | string | db.t2.micro   |
| port | the port for rds instance | string | 3306   |
| multi_az | sets multi placement zone for rds | string | false   |
| storage_type | storage type for rds | string | gp2   |
| storage_encrypted | encrypt storage for rds | string | false   |
| publicly_accessible | makes rds publicly accessible | string | false   |
| allow_major_version_upgrade | allow_major_version_upgrade for rds | string | true   |
| auto_minor_version_upgrade | auto_minor_version_upgrade for rds | string | true   |
| skip_final_snapshot | skip_final_snapshot for rds when destroying | string | true   |
| publish_creds | show credentials on the ED dashboard | string | True   |
| cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |

**Sample launch - simple**

```
infrastructure:
   rds:
       stack_name: elasticdev:::aws_rds
       arguments:
          rds_name: rds-dev-mysql
          vpc_name: eval-ed-vpc
          sg_id: sg-0faf106a572b7af8f
          subnet_ids: subnet-045721f387afabc72,subnet-05075171b106721ad,subnet-0a5e767ac278c437a
          allocated_storage: 14
          db_name: app
       credentials:
           - reference: aws_2
             orchestration: true
```

**Sample launch - with labels/selectors**

```
global_arguments:
   aws_default_region: eu-west-1
   cloud_tags_hash:
       environment: dev
       purpose: eval-ed
labels:
   general:
     environment: dev
     purpose: test
   infrastructure:
     cloud: aws
     product: rds
     app_tier: database
selectors:
   vpc_info:
     labels:
       environment: dev
       app_tier: networking
     keys:
       provider: aws
       region: eu-west-1
     parameters:
       must_exists: True
       resource_type: vpc
   sg_info:
     labels:
       environment: dev
       app_tier: networking
     keys:
       provider: aws
       region: eu-west-1
       name: database
     parameters:
       must_be_one: True
       resource_type: security_group
   subnet_info:
     labels:
       environment: dev
       app_tier: networking
     keys:
       provider: aws
       region: eu-west-1
       name: private
     parameters:
       resource_type: subnet
infrastructure:
   rds:
       stack_name: elasticdev:::aws_rds
       arguments:
          vpc_name: selector:::vpc_info::name
          sg_id: selector:::sg_info::sg_id
          subnet_ids: selector:::subnet_info::subnet_id:csv
          rds_name: eval-ed-rds
          allocated_storage: 14
          db_name: app
          publish_creds: true
          publish_to_saas: true
       to_base64:
         - cloud_tags_hash
       labels:
         - general
         - infrastructure
       selectors:
         - vpc_info
         - sg_info
         - subnet_info
       credentials:
           - reference: eval-ed-iam
             orchestration: true
       inputvars:
           - reference: rds
             orchestration: true
```

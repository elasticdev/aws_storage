def run(stackargs):

    import json
    import os

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")  # we can query this resources through selector
    stack.parse.add_required(key="sg_id")  # we can query this resources through selector
    stack.parse.add_required(key="subnet_ids")  # we can query this resources through selector
    stack.parse.add_required(key="rds_name")

    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="master_username",default="null")
    stack.parse.add_optional(key="master_password",default="null")

    stack.parse.add_optional(key="engine",default="MySQL")
    stack.parse.add_optional(key="engine_version",default="5.7")
    stack.parse.add_optional(key="allocated_storage",default=10)
    stack.parse.add_optional(key="db_name",default="_random")
    stack.parse.add_optional(key="instance_class",default="db.t2.micro")
    stack.parse.add_optional(key="port",default="3306")
    stack.parse.add_optional(key="multi_az",default="false")
    stack.parse.add_optional(key="storage_type",default="gp2")
    stack.parse.add_optional(key="publicly_accessible",default="false")
    stack.parse.add_optional(key="storage_encrypted",default="false")
    stack.parse.add_optional(key="allow_major_version_upgrade",default="true")
    stack.parse.add_optional(key="auto_minor_version_upgrade",default="true")
    stack.parse.add_optional(key="skip_final_snapshot",default="true")
    stack.parse.add_optional(key="use_docker",default=True,null_allowed=True)
    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    stack.parse.add_optional(key="backup_retention_period",default="1") 
    stack.parse.add_optional(key="backup_window",default="10:22-11:22")           
    stack.parse.add_optional(key="maintenance_window",default="Mon:00:00-Mon:03:00")

    # docker image to execute terraform with
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env")
    stack.parse.add_optional(key="publish_creds",default="null")
    stack.parse.add_optional(key="publish_to_saas",default="null")  # this is true, this will overide publish_creds

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::rds")

    # add substacks
    stack.add_substack('elasticdev:::publish_rds_info')

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # set variables
    stack.set_variable("resource_type","rds")

    # automatically name the db_subnet_name
    stack.set_variable("db_subnet_name","{}-subnet".format(stack.rds_name))

    # set username and password
    if not stack.master_username and stack.inputvars.get("DB_MASTER_USERNAME"):
        stack.set_variable("master_username",stack.inputvars["DB_MASTER_USERNAME"])
    elif not stack.master_username:
        stack.set_variable("master_username",stack.random_id(size=20))

    if not stack.master_password and stack.inputvars.get("DB_MASTER_PASSWORD"):
        stack.set_variable("master_password",stack.inputvars["DB_MASTER_PASSWORD"])
    elif not stack.master_password:
        stack.set_variable("master_password",stack.random_id(size=20))

    # stack.logger.debug("DB_MASTER_USERNAME {}".format(stack.master_username))
    # stack.logger.debug("DB_MASTER_PASSWORD {}".format(stack.master_password))

    # Execute execgroup
    env_vars = {"TF_VAR_rds_name":stack.rds_name}
    env_vars["TF_VAR_db_name"] = stack.db_name
    env_vars["TF_VAR_db_subnet_name"] = stack.db_subnet_name
    env_vars["TF_VAR_rds_master_username"] = stack.master_username
    env_vars["TF_VAR_rds_master_password"] = stack.master_password

    env_vars["TF_VAR_security_group_ids"] = stack.sg_id
    env_vars["TF_VAR_subnet_ids"] = stack.subnet_ids

    env_vars["TF_VAR_allocated_storage"] = stack.allocated_storage
    env_vars["TF_VAR_engine"] = stack.engine
    env_vars["TF_VAR_engine_version"] = stack.engine_version
    env_vars["TF_VAR_instance_class"] = stack.instance_class
    env_vars["TF_VAR_multi_az"] = stack.multi_az
    env_vars["TF_VAR_storage_type"] = stack.storage_type
    env_vars["TF_VAR_publicly_accessible"] = stack.publicly_accessible
    env_vars["TF_VAR_storage_encrypted"] = stack.storage_encrypted
    env_vars["TF_VAR_allow_major_version_upgrade"] = stack.allow_major_version_upgrade
    env_vars["TF_VAR_auto_minor_version_upgrade"] = stack.auto_minor_version_upgrade
    env_vars["TF_VAR_skip_final_snapshot"] = stack.skip_final_snapshot
    env_vars["TF_VAR_port"] = stack.port
    env_vars["TF_VAR_backup_retention_period"] = stack.backup_retention_period
    env_vars["TF_VAR_backup_window"] = stack.backup_window
    env_vars["TF_VAR_maintenance_window"] = stack.maintenance_window
    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region

    # cloud tags
    if stack.cloud_tags_hash: 
        env_vars["TF_VAR_cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))

    env_vars["AWS_DEFAULT_REGION"] = stack.aws_default_region
    env_vars["STATEFUL_ID"] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["RESOURCE_TAGS"] = "{},{},{}".format(stack.resource_type, stack.rds_name, stack.aws_default_region)

    #env_vars["TF_TEMPLATE_VARS"] = ",".join(env_vars.keys())

    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["METHOD"] = "create"
    env_vars["CLOBBER"] = True
    if stack.use_docker: env_vars["use_docker".upper()] = True

    docker_env_fields_keys = env_vars.keys()
    docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    docker_env_fields_keys.remove("METHOD")

    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["name"] = stack.rds_name
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = "Creating RDS {}".format(stack.rds_name)
    stack.rds.insert(**inputargs)

    if stack.publish_creds or stack.publish_to_saas:

        # publish variables
        default_values = {"db_instance_name":stack.rds_name}
        default_values["db_root_user"] = stack.master_username
        default_values["db_root_password"] = stack.master_password
        if stack.publish_creds: default_values["publish_creds"] = True

        inputargs = {"default_values":default_values}
        inputargs["automation_phase"] = "infrastructure"
        inputargs["human_description"] = 'Publish RDS info {}'.format(stack.rds_name)
        stack.publish_rds_info.insert(display=True,**inputargs)

    return stack.get_results()

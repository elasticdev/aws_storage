def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="bucket")
    stack.parse.add_required(key="acl",default="_random")

    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="versioning",default="null")
    stack.parse.add_optional(key="force_destroy",default="null")
    stack.parse.add_optional(key="enable_lifecycle",default="null")
    stack.parse.add_optional(key="expire_days",default="null")
    stack.parse.add_optional(key="noncurrent_version_expiration",default="null")
    stack.parse.add_optional(key="publish_to_saas",default=True)
    stack.parse.add_optional(key="cloud_tags_hash",default="null")

    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::buckets")
    stack.add_substack('elasticdev:::ed_core::publish_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("resource_type","cloud_storage")

    env_vars = {"aws_default_region".upper(): stack.aws_default_region }
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env

    env_vars["TF_VAR_bucket"] = stack.bucket
    env_vars["TF_VAR_acl"] = stack.acl
    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region

    if stack.cloud_tags_hash: 
        env_vars["TF_VAR_cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))

    if stack.force_destroy:
        env_vars["TF_VAR_force_destroy"] = "true"

    if stack.versioning:
        env_vars["TF_VAR_versioning"] = "true"
        
    if stack.enable_lifecycle:
        env_vars["TF_VAR_enable_lifecycle"] = "true"
    else:
        env_vars["TF_VAR_enable_lifecycle"] = "false"

    if stack.enable_lifecycle and stack.expire_days:
        env_vars["TF_VAR_expire_days"] = str(stack.expire_days)

    if stack.enable_lifecycle and stack.noncurrent_version_expiration:
        env_vars["TF_VAR_noncurrent_version_expiration"] = str(stack.noncurrent_version_expiration)

    env_vars["METHOD"] = "create"
    env_vars["CLOBBER"] = True
    env_vars["RESOURCE_TAGS"] = "{},{}".format(stack.resource_type,stack.aws_default_region)
    env_vars["use_docker".upper()] = True

    docker_env_fields_keys = env_vars.keys()
    docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    docker_env_fields_keys.remove("METHOD")

    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["display"] = True
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = "Create {} bucket {}".format(stack.resource_type,stack.bucket)
    stack.buckets.insert(**inputargs)

    if not stack.publish_to_saas: return stack.get_results()

    # publish the info
    keys_to_publish = [ "arn",
                        "name",
                        "expire_days",
                        "encryption",
                        "noncurrent_version_expiration",
                        "bucket_versioning",
                        "resource_type" ]

    overide_values = { "name":stack.bucket }
    default_values = { "resource_type":stack.resource_type }
    default_values["publish_keys"] = stack.b64_encode(keys_to_publish)

    inputargs = { "default_values":default_values,
                  "overide_values":overide_values }

    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Publish resource info for {}'.format(stack.resource_type)
    stack.publish_resource.insert(display=True,**inputargs)

    return stack.get_results()


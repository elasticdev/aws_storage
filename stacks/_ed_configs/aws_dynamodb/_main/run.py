def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="dynamodb_name")

    stack.parse.add_optional(key="hash_key",default='_id')
    stack.parse.add_optional(key="billing_mode",default='PAY_PER_REQUEST')
    stack.parse.add_optional(key="cloud_tags_hash",default='null')
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")
    stack.parse.add_optional(key="publish_to_saas",default="null")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::dynamodb")
    stack.add_substack('elasticdev:::ed_core::publish_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("resource_type","aws_dynamodb")

    env_vars = {"aws_default_region".upper(): stack.aws_default_region }
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["TF_VAR_dynamodb_name"] = stack.dynamodb_name
    env_vars["TF_VAR_billing_mode"] = stack.billing_mode
    env_vars["TF_VAR_hash_key"] = stack.hash_key

    if stack.cloud_tags_hash: 
        env_vars["TF_VAR_cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))

    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region

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
    inputargs["human_description"] = "Create dynamodb {}".format(stack.dynamodb_name)
    stack.dynamodb.insert(**inputargs)

    if not stack.publish_to_saas: return stack.get_results()

    # publish the info
    keys_to_publish = [ "billing_mode",
                        "arn",
                        "hash_key",
                        "name",
                        "ttl",
                        "resource_type" ]

    overide_values = { "name":stack.dynamodb_name }
    default_values = { "resource_type":stack.resource_type }
    default_values["publish_keys"] = stack.b64_encode(keys_to_publish)

    inputargs = { "default_values":default_values,
                  "overide_values":overide_values }

    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Publish resource info for {}'.format(stack.resource_type)
    stack.publish_resource.insert(display=True,**inputargs)

    return stack.get_results()

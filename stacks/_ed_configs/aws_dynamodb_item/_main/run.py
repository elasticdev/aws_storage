def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="table_name")
    stack.parse.add_required(key="item_hash")
    stack.parse.add_optional(key="hash_key",default='_id')

    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::dynamodb_item")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("resource_type","db_item")

    env_vars = {"aws_default_region".upper(): stack.aws_default_region }
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["TF_VAR_table_name"] = stack.table_name
    env_vars["TF_VAR_item_hash"] = stack.item_hash
    env_vars["TF_VAR_hash_key"] = stack.hash_key
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
    inputargs["human_description"] = "Create dynamodb item in {}".format(stack.table_name)
    stack.dynamodb_item.insert(**inputargs)

    return stack.get_results()

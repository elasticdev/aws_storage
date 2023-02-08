def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="ssm_value")
    stack.parse.add_required(key="ssm_key",default="_random")

    stack.parse.add_optional(key="ssm_type",default="SecureString")
    stack.parse.add_optional(key="ssm_description",default="null")
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")
    stack.parse.add_optional(key="publish_to_saas",default="null")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::ssm_parameter_store")
    stack.add_substack('elasticdev:::ed_core::publish_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("resource_type","cloud_parameters")

    if not stack.ssm_description:
        stack.set_variable("ssm_description","The ssm parameter for key = {}".format(stack.ssm_key))

    env_vars = {"aws_default_region".upper(): stack.aws_default_region }
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env

    env_vars["TF_VAR_ssm_key"] = stack.ssm_key
    env_vars["TF_VAR_ssm_value"] = stack.ssm_value
    env_vars["TF_VAR_ssm_type"] = stack.ssm_type
    env_vars["TF_VAR_ssm_description"] = stack.ssm_description
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
    inputargs["human_description"] = "Create {} key {}".format(stack.resource_type,stack.ssm_key)
    stack.ssm_parameter_store.insert(**inputargs)

    if not stack.publish_to_saas: return stack.get_results()

    # publish the info
    keys_to_publish = [ "key_id",
                        "tier",
                        "type",
                        "name",
                        "resource_type" ]

    overide_values = { "name":stack.ssm_key }
    default_values = { "resource_type":stack.resource_type }
    default_values["publish_keys"] = stack.b64_encode(keys_to_publish)

    inputargs = { "default_values":default_values,
                  "overide_values":overide_values }

    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Publish resource info for {}'.format(stack.resource_type)
    stack.publish_resource.insert(display=True,**inputargs)

    return stack.get_results()

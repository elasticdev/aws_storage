def _determine_instance_id(stack):

    if stack.instance_id and stack.availability_zone: return
    
    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["resource_type"] = "server"
    if stack.aws_default_region: _lookup["region"] = stack.aws_default_region

    if stack.instance_id: 
        _lookup["instance_id"] = stack.instance_id
    elif stack.hostname: 
        _lookup["hostname"] = stack.hostname
    else:
        return

    _lookup["search_keys"] = "instance_id"
    server_info = list(stack.get_resource(**_lookup))[0]

    if not stack.instance_id:
        stack.set_variable("instance_id",
                           server_info["instance_id"])

    if not stack.availability_zone:
        stack.set_variable("availability_zone",
                           server_info["availability_zone"])

    if not stack.aws_default_region:
        stack.set_variable("aws_default_region",
                           server_info["region"])

    return 

def run(stackargs):

    import json

    stackargs["add_cluster"] = False
    stackargs["add_instance"] = False

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="volume_name")
    stack.parse.add_required(key="volume_size",default=10)

    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env")
    stack.parse.add_optional(key="stateful_id",default="_random")

    stack.parse.add_optional(key="hostname",default="null")
    stack.parse.add_optional(key="aws_default_region",default="null")

    stack.parse.add_optional(key="availability_zone",default="null")
    stack.parse.add_optional(key="instance_id",default="null")
    stack.parse.add_optional(key="use_docker",default=True,null_allowed=True)

    # labels and tags
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")

    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::ebs_volume")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()

    _determine_instance_id(stack)

    stack.set_variable("resource_type","ebs_volume")

    # call to create volume
    env_vars = {"AWS_DEFAULT_REGION":stack.aws_default_region}
    env_vars["STATEFUL_ID"] = stack.stateful_id

    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region
    env_vars["TF_VAR_availability_zone"] = stack.availability_zone
    env_vars["TF_VAR_volume_size"] = stack.volume_size
    env_vars["TF_VAR_volume_name"] = stack.volume_name
    env_vars["EBS_VOLUME_NAME"] = stack.volume_name

    if stack.cloud_tags_hash:
        env_vars["TF_VAR_cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))

    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["RESOURCE_TYPE"] = stack.resource_type
    env_vars["RESOURCE_TAGS"] = "{},{},{},{},{}".format("ebs","ebs_volume", "aws", stack.volume_name, stack.aws_default_region)
    env_vars["METHOD"] = "create"
    if stack.use_docker: env_vars["use_docker".upper()] = True

    _docker_env_fields_keys = env_vars.keys()
    _docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    _docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    _docker_env_fields_keys.append("AWS_DEFAULT_REGION")
    _docker_env_fields_keys.remove("METHOD")
    env_vars["DOCKER_ENV_FIELDS"] = ",".join(_docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["human_description"] = 'Creates ebs volume "{}"'.format(stack.volume_name)
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["automation_phase"] = "infrastructure"
    if stack.tags: inputargs["tags"] = stack.tags
    if stack.labels: inputargs["labels"] = stack.labels
    stack.ebs_volume.insert(**inputargs)

    return stack.get_results()

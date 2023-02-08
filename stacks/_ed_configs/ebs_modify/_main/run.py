def _determine_instance_id(stack):

    if stack.instance_id and stack.aws_default_region: return
    
    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["resource_type"] = "server"
    if stack.aws_default_region: _lookup["region"] = stack.aws_default_region
    if stack.hostname: _lookup["hostname"] = stack.hostname
    if stack.instance_id: _lookup["instance_id"] = stack.instance_id
    _lookup["search_keys"] = "instance_id"
    server_info = list(stack.get_resource(**_lookup))[0]

    if not stack.instance_id:
        stack.set_variable("instance_id",
                           server_info["instance_id"])

    if not stack.aws_default_region:
        stack.set_variable("aws_default_region",
                           server_info["region"])

    return 

def _determine_volume_id(stack):

    if stack.volume_id: return
    if not stack.volume_name: return 
    
    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["name"] = stack.volume_name
    _lookup["resource_type"] = "ebs_volume"
    if stack.aws_default_region: _lookup["region"] = stack.aws_default_region
    _info = list(stack.get_resource(**_lookup))[0]

    stack.set_variable("volume_id",
                       _info["volume_id"])

    return 

def run(stackargs):

    import json

    stackargs["add_cluster"] = False
    stackargs["add_instance"] = False

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_optional(key="volume_name",default='null')
    stack.parse.add_optional(key="volume_id",default='null')

    stack.parse.add_optional(key="terraform_docker_exec_env",default="elasticdev/terraform-run-env")
    stack.parse.add_optional(key="ansible_docker_exec_env",default="elasticdev/ansible-run-env")

    stack.parse.add_optional(key="hostname",default="null")
    stack.parse.add_optional(key="aws_default_region",default="null")

    stack.parse.add_optional(key="instance_id",default="null")
    stack.parse.add_optional(key="device_name",default="/dev/xvdc")

    stack.parse.add_optional(key="volume_mountpoint",default="null")
    stack.parse.add_optional(key="volume_fstype",default="null")

    # this is needed for ansible when you need to ssh into the machine
    # and format and mount the volume
    stack.parse.add_optional(key="ssh_key_name",default="null")
    stack.parse.add_optional(key="use_docker",default=True,null_allowed=True)
    stack.parse.add_optional(key="config_network",default="public")

    # labels and tags
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")

    # Add shelloutconfigs
    # stack.add_shelloutconfig('elasticdev:::ansible::write_ssh_key')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::attach_volume_to_ec2")
    stack.add_execgroup("elasticdev:::aws_storage::config_vol")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()

    _determine_instance_id(stack)
    _determine_volume_id(stack)

    stack.set_variable("resource_type","ebs_volume_attach")

    if not stack.volume_id:
        msg = "Cannot determine volume_id to attach to instance"
        stack.ehandle.NeedRtInput(message=msg)

    if not stack.instance_id:
        msg = "Cannot determine instance_id to mount volume"
        stack.ehandle.NeedRtInput(message=msg)

    # Call to create the server with shellout script
    env_vars = {"AWS_DEFAULT_REGION":stack.aws_default_region}
    env_vars["STATEFUL_ID"] = stack.random_id(size=10)

    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region
    env_vars["TF_VAR_device_name"] = stack.device_name
    env_vars["TF_VAR_instance_id"] = stack.instance_id
    env_vars["TF_VAR_volume_id"] = stack.volume_id

    env_vars["docker_exec_env".upper()] = stack.terraform_docker_exec_env
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["RESOURCE_TAGS"] = "{},{},{},{},{}".format("ebs","ebs_attach", "aws", stack.volume_id, stack.aws_default_region)
    env_vars["METHOD"] = "create"
    if stack.use_docker: env_vars["use_docker".upper()] = True

    _docker_env_fields_keys = env_vars.keys()
    _docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    _docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    _docker_env_fields_keys.append("AWS_DEFAULT_REGION")
    _docker_env_fields_keys.remove("METHOD")
    env_vars["DOCKER_ENV_FIELDS"] = ",".join(_docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["human_description"] = 'Attaches ebs volume to instance_id "{}"'.format(stack.instance_id)
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["stateful_id"] = env_vars["STATEFUL_ID"]
    inputargs["automation_phase"] = "infrastructure"
    if stack.tags: inputargs["tags"] = stack.tags
    if stack.labels: inputargs["labels"] = stack.labels
    stack.attach_volume_to_ec2.insert(**inputargs)

    # minimal to optionally format and mount volume
    # format and attach with ansible via fstab

    # Testingyoyo
    # ansible will require python installed

    if stack.volume_fstype and stack.volume_mountpoint:

        # get ssh_key
        _lookup = {"must_be_one":True}
        _lookup["resource_type"] = "ssh_key_pair"
        _lookup["name"] = stack.ssh_key_name
        _lookup["serialize"] = True
        _lookup["serialize_keys"] = [ "private_key" ]
        private_key = stack.get_resource(decrypt=True,**_lookup)["private_key"]

        # get server info
        _lookup = {"must_be_one":True}
        _lookup["resource_type"] = "server"
        _lookup["hostname"] = stack.hostname
        _host_info = list(stack.get_resource(**_lookup))[0]

        env_vars = {"STATEFUL_ID":stack.random_id(size=10)}
        env_vars["ANS_VAR_volume_fstype"] = stack.volume_fstype
        env_vars["ANS_VAR_volume_mountpoint"] = stack.volume_mountpoint
        env_vars["ANS_VAR_private_key"] = private_key
        env_vars["METHOD"] = "create"
        env_vars["ANS_VAR_exec_ymls"] = "entry_point/20-format.yml,entry_point/30-mount.yml"

        if stack.config_network == "private":
            env_vars["ANS_VAR_host_ips"] = _host_info["private_ip"]
        else:
            env_vars["ANS_VAR_host_ips"] = _host_info["public_ip"]

        inputargs = {"display":True}
        inputargs["human_description"] = 'Format and mount volume on instance_id "{}" fstype {} mountpoint {}'.format(stack.instance_id,
                                                                                                                      stack.volume_fstype,
                                                                                                                      stack.volume_mountpoint)
        inputargs["env_vars"] = json.dumps(env_vars)
        inputargs["stateful_id"] = env_vars["STATEFUL_ID"]
        inputargs["automation_phase"] = "infrastructure"
        if stack.tags: inputargs["tags"] = stack.tags
        if stack.labels: inputargs["labels"] = stack.labels
        stack.config_vol.insert(**inputargs)

    return stack.get_results()

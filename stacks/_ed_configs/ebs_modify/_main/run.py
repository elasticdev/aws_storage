import json

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }

        self.resource_values["name"] = self.stack.resource_name

        return self.resource_values

    def _get_docker_settings(self):
    
        env_vars = { "method": "create",
                     "aws_default_region": self.stack.aws_default_region,
                     "stateful_id":self.stack.stateful_id,
                     "resource_tags": "{},{},{}".format(self.stack.resource_type, 
                                                        self.stack.resource_name,
                                                        self.stack.aws_default_region),
                     "name": self.stack.resource_name }
    
        include_env_vars_keys = [ "aws_access_key_id",
                                  "aws_secret_access_key" ]
    
        self.docker_settings = { "env_vars":env_vars,
                                 "include_env_vars_keys":include_env_vars_keys }

        return self.docker_settings
    
    def _get_tf_settings(self):

        tf_vars = { "aws_default_region": self.stack.aws_default_region }
        tf_vars["aws_default_region"] = self.stack.aws_default_region
        tf_vars["device_name"] = self.stack.device_name
        tf_vars["instance_id"] = self.stack.instance_id
        tf_vars["volume_id"] = self.stack.volume_id

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        add_keys = [ "instance_id",
                     "id" ]
        
        maps = { "ec2_instance_id":"instance_id" }

        resource_params = { "add_keys": add_keys,
                            "map_keys": maps,
                            "include_raw": "True" }

        self.tf_settings = { "tf_vars":tf_vars,
                             "terraform_type":self.stack.terraform_type,
                             "resource_params": resource_params }

        return self.tf_settings

    def get(self):

        ed_resource_settings = { "tf_settings":self._get_tf_settings(),
                                 "docker_settings":self._get_docker_settings(),
                                 "resource_values":self._get_resource_values_to_add(),
                                 "resource_type":self.stack.resource_type,
                                 "provider":self.stack.provider
                                 }

        return self.stack.b64_encode(ed_resource_settings)

def _determine_instance_id(stack):

    if stack.instance_id and stack.aws_default_region: 
        return
    
    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["resource_type"] = "server"

    if stack.aws_default_region: 
        _lookup["region"] = stack.aws_default_region

    if stack.hostname: 
        _lookup["hostname"] = stack.hostname

    if stack.instance_id: 
        _lookup["instance_id"] = stack.instance_id

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

    if stack.volume_id: 
        return

    if not stack.volume_name: 
        return 
    
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

    stack.parse.add_optional(key="terraform_docker_exec_env",default="elasticdev/terraform-run-env:1.3.7")
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
    stack.parse.add_optional(key="config_network",default="public")

    # labels and tags
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")

    # Add shelloutconfigs
    # stack.add_shelloutconfig('elasticdev:::ansible::write_ssh_key')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::attach_volume_to_ec2","cloud_resource")
    stack.add_execgroup("elasticdev:::aws_storage::config_vol")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()

    _determine_instance_id(stack)
    _determine_volume_id(stack)

    stack.set_variable("resource_type","ebs_volume_attach")
    stack.set_variable("provider","aws")
    stack.set_variable("stateful_id",stack.random_id())
    stack.set_variable("resource_name","{}-{}".format(stack.hostmame,stack.volume_name))
    stack.set_variable("terraform_type","aws_volume_attachment")

    if not stack.volume_id:
        msg = "Cannot determine volume_id to attach to instance"
        stack.ehandle.NeedRtInput(message=msg)

    if not stack.instance_id:
        msg = "Cannot determine instance_id to mount volume"
        stack.ehandle.NeedRtInput(message=msg)

    _ed_resource_settings = EdResourceSettings(stack=stack)

    env_vars = { "STATEFUL_ID":stack.stateful_id,
                 "METHOD":"create" }

    env_vars["ed_resource_settings_hash".upper()] = _ed_resource_settings.get()
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["name"] = stack.resource_name
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = "Creating name {} type {}".format(stack.resource_name,stack.resource_type)
    inputargs["display_hash"] = stack.get_hash_object(inputargs)

    if stack.tags: 
        inputargs["tags"] = stack.tags

    if stack.labels: 
        inputargs["labels"] = stack.labels

    stack.cloud_resource.insert(**inputargs)

    # ansible will require python installed
    if not stack.volume_fstype:
        return stack.get_results()

    if not stack.volume_mountpoint:
        return stack.get_results()

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
    inputargs["human_description"] = 'format/mount vol on instance_id "{}" fstype {} mountpoint {}'.format(stack.instance_id,
                                                                                                           stack.volume_fstype,
                                                                                                           stack.volume_mountpoint)
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["stateful_id"] = env_vars["STATEFUL_ID"]
    inputargs["automation_phase"] = "infrastructure"

    if stack.tags: 
        inputargs["tags"] = stack.tags

    if stack.labels: 
        inputargs["labels"] = stack.labels

    stack.config_vol.insert(**inputargs)

    return stack.get_results()

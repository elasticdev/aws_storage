import json

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }

        self.resource_values["name"] = self.stack.resource_name
        self.resource_values["hostname"] = self.stack.hostname
        self.resource_values["volume_id"] = self.stack.volume_id
        self.resource_values["volume_name"] = self.stack.volume_name

        return self.resource_values

    def _get_docker_settings(self):
    
        env_vars = { "method": "create",
                     "stateful_id":self.stack.stateful_id,
                     "aws_default_region": self.stack.aws_default_region,
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
        tf_vars["device_name"] = self.stack.device_name
        tf_vars["instance_id"] = self.stack.instance_id
        tf_vars["volume_id"] = self.stack.volume_id

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        add_keys = [ "arn",
                     "id" ]
        
        maps = { "instance_id":"id",
                 "ec2_instance_id":"id" }

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

def _get_instance_id(stack):

    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["resource_type"] = "server"
    _lookup["hostname"] = stack.hostname
    _lookup["region"] = stack.aws_default_region
    _info = list(stack.get_resource(**_lookup))[0]

    return _info["instance_id"]

def _get_volume_id(stack):

    _lookup = {"must_exists":True}
    _lookup["must_be_one"] = True
    _lookup["name"] = stack.volume_name
    _lookup["resource_type"] = "ebs_volume"
    _lookup["region"] = stack.aws_default_region
    _info = list(stack.get_resource(**_lookup))[0]

    return _info["volume_id"]

def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="hostname")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")

    stack.parse.add_optional(key="volume_name",default='null')
    stack.parse.add_optional(key="device_name",default="/dev/xvdc")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:1.3.7")
    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::attach_volume_to_ec2","cloud_resource")

    # Initialize 
    stack.init_execgroups()
    stack.init_variables()

    if not stack.volume_name:
        stack.set_variable("volume_name","{}-data".format(stack.hostname))

    stack.set_variable("provider","aws")
    stack.set_variable("stateful_id",stack.random_id())

    stack.set_variable("instance_id",_get_instance_id(stack))
    stack.set_variable("volume_id",_get_volume_id(stack))

    stack.set_variable("resource_name","attachment_{}".format(stack.volume_name))
    stack.set_variable("resource_type","ebs_volume_attach")
    stack.set_variable("terraform_type","aws_volume_attachment")

    _ed_resource_settings = EdResourceSettings(stack=stack)

    env_vars = { "STATEFUL_ID":stack.stateful_id,
                 "METHOD":"create" }

    env_vars["ed_resource_settings_hash".upper()] = _ed_resource_settings.get()
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["use_docker".upper()] = True
    env_vars["CLOBBER"] = True

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["name"] = stack.resource_name
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = 'Attaches ebs volume to instance_id "{}"'.format(stack.instance_id)
    inputargs["display_hash"] = stack.get_hash_object(inputargs)

    stack.cloud_resource.insert(**inputargs)

    return stack.get_results()

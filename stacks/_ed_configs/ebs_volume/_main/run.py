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
        tf_vars["availability_zone"] = self.stack.availability_zone
        tf_vars["volume_size"] = self.stack.volume_size
        tf_vars["volume_name"] = self.stack.volume_name

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        resource_keys = [ "availability_zone",
                          "arn",
                          "id" ]
        
        resource_keys_maps = { "volume_id":"id" }

        self.tf_settings = { "tf_vars":tf_vars,
                             "terraform_type":self.stack.terraform_type,
                             "tfstate_raw": "True",
                             "resource_keys_maps": resource_keys_maps,
                             "resource_keys": resource_keys }

        return self.tf_settings

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
    stack.add_execgroup("elasticdev:::aws_storage::ebs_volume","cloud_resource")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()

    _determine_instance_id(stack)

    stack.set_variable("resource_type","ebs_volume")
    stack.set_variable("provider","aws")
    stack.set_variable("stateful_id",stack.random_id())

    stack.set_variable("resource_name",stack.volume_name)
    set_variable("terraform_type","aws_s3_bucket")

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
    inputargs["human_description"] = "Creating name {} type {}".format(stack.resource_name,stack.resource_type)
    inputargs["display_hash"] = stack.get_hash_object(inputargs)

    stack.cloud_resource.insert(**inputargs)

    return stack.get_results()

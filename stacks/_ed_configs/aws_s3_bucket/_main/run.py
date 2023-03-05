import json

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }

        if self.stack.enable_lifecycle and self.stack.expire_days:
            self.resource_values["expire_days"] = str(self.stack.expire_days)

        self.resource_values["name"] = self.stack.bucket

        if self.stack.enable_lifecycle:
            self.resource_values["enable_lifecycle"] = "true"

        if self.stack.versioning:
            self.resource_values["versioning"] = "true"

        if self.stack.force_destroy:
            self.resource_values["force_destroy"] = "true"
            
        if self.stack.enable_lifecycle and self.stack.noncurrent_version_expiration:
            self.resource_values["noncurrent_version_expiration"] = str(self.stack.noncurrent_version_expiration)
    
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

        '''
        #_results["expire_days"] = resource["instances"][0]["attributes"]["lifecycle_rule"][0]["expiration"][0]["days"]
        #_results["noncurrent_version_expiration"] = resource["instances"][0]["attributes"]["lifecycle_rule"][0]["noncurrent_version_expiration"][0]["days"]
        #_results["encryption"] = resource["instances"][0]["attributes"]["server_side_encryption_configuration"][0]["rule"][0]["apply_server_side_encryption_by_default"][0]["sse_algorithm"]
        #_results["bucket_versioning"] = resource["instances"][0]["attributes"]["versioning"][0]["enabled"]
        '''
    
        tf_vars = { "aws_default_region": self.stack.aws_default_region }

        tf_vars["bucket"] = self.stack.bucket
        tf_vars["acl"] = self.stack.acl
        tf_vars["aws_default_region"] = self.stack.aws_default_region

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        if self.stack.force_destroy:
            tf_vars["force_destroy"] = "true"

        if self.stack.versioning:
            tf_vars["versioning"] = "true"
            
        if self.stack.enable_lifecycle:
            tf_vars["enable_lifecycle"] = "true"
        else:
            tf_vars["enable_lifecycle"] = "false"

        if self.stack.enable_lifecycle and self.stack.expire_days:
            tf_vars["expire_days"] = str(self.stack.expire_days)

        if self.stack.enable_lifecycle and self.stack.noncurrent_version_expiration:
            tf_vars["noncurrent_version_expiration"] = str(self.stack.noncurrent_version_expiration)
    
        add_keys = [ "server_side_encryption_configuration",
                     "lifecycle_rule",
                     "versioning",
                     "arn",
                     "id" ]

        maps = { "id":"arn" }

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
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:1.3.7")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::buckets","cloud_resource")
    stack.add_substack('elasticdev:::ed_core::publish_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("provider","aws")
    stack.set_variable("stateful_id",stack.random_id())

    stack.set_variable("terraform_type","aws_s3_bucket")
    stack.set_variable("resource_type","cloud_storage")
    stack.set_variable("resource_name",stack.bucket)

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

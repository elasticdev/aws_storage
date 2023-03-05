import json

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }

        self.resource_values["rds_name"] = self.stack.rds_name
        self.resource_values["name"] = self.stack.rds_name

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
        tf_vars = {"rds_name":self.stack.rds_name}
        tf_vars["db_name"] = self.stack.db_name
        tf_vars["db_subnet_name"] = self.stack.db_subnet_name
        tf_vars["rds_master_username"] = self.stack.master_username
        tf_vars["rds_master_password"] = self.stack.master_password
        tf_vars["security_group_ids"] = list(self.stack.sg_id.split(","))
        tf_vars["subnet_ids"] = list(self.stack.subnet_ids.split(","))
        tf_vars["allocated_storage"] = self.stack.allocated_storage
        tf_vars["engine"] = self.stack.engine
        tf_vars["engine_version"] = self.stack.engine_version
        tf_vars["instance_class"] = self.stack.instance_class
        tf_vars["multi_az"] = self.stack.multi_az
        tf_vars["storage_type"] = self.stack.storage_type
        tf_vars["publicly_accessible"] = self.stack.publicly_accessible
        tf_vars["storage_encrypted"] = self.stack.storage_encrypted
        tf_vars["allow_major_version_upgrade"] = self.stack.allow_major_version_upgrade
        tf_vars["auto_minor_version_upgrade"] = self.stack.auto_minor_version_upgrade
        tf_vars["skip_final_snapshot"] = self.stack.skip_final_snapshot
        tf_vars["port"] = self.stack.port
        tf_vars["backup_retention_period"] = self.stack.backup_retention_period
        tf_vars["backup_window"] = self.stack.backup_window
        tf_vars["maintenance_window"] = self.stack.maintenance_window

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        add_keys = [ "arn",
                     "id"
                     ]
        
        maps = { "db_id":"arn" }

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

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")  # we can query this resources through selector
    stack.parse.add_required(key="sg_id")  # we can query this resources through selector
    stack.parse.add_required(key="subnet_ids")  # we can query this resources through selector
    stack.parse.add_required(key="rds_name")

    stack.parse.add_optional(key="stateful_id",default="_random")
    stack.parse.add_optional(key="master_username",default="null")
    stack.parse.add_optional(key="master_password",default="null")

    stack.parse.add_optional(key="engine",default="MySQL")
    stack.parse.add_optional(key="engine_version",default="5.7")
    stack.parse.add_optional(key="allocated_storage",default=10)
    stack.parse.add_optional(key="db_name",default="_random")
    stack.parse.add_optional(key="instance_class",default="db.t2.micro")
    stack.parse.add_optional(key="port",default="3306")
    stack.parse.add_optional(key="multi_az",default="false")
    stack.parse.add_optional(key="storage_type",default="gp2")
    stack.parse.add_optional(key="publicly_accessible",default="false")
    stack.parse.add_optional(key="storage_encrypted",default="false")
    stack.parse.add_optional(key="allow_major_version_upgrade",default="true")
    stack.parse.add_optional(key="auto_minor_version_upgrade",default="true")
    stack.parse.add_optional(key="skip_final_snapshot",default="true")
    stack.parse.add_optional(key="use_docker",default=True,null_allowed=True)
    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    stack.parse.add_optional(key="backup_retention_period",default="1") 
    stack.parse.add_optional(key="backup_window",default="10:22-11:22")           
    stack.parse.add_optional(key="maintenance_window",default="Mon:00:00-Mon:03:00")

    # docker image to execute terraform with
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:1.3.7")
    stack.parse.add_optional(key="publish_creds",default="null")
    stack.parse.add_optional(key="publish_to_saas",default="null")  # this is true, this will overide publish_creds

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_storage::rds","cloud_resource")

    # add substacks
    stack.add_substack('elasticdev:::publish_rds_info')

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # set variables
    stack.set_variable("provider","aws")
    stack.set_variable("stateful_id",stack.random_id())

    stack.set_variable("terraform_type","aws_db_instance")
    stack.set_variable("resource_type","rds")
    stack.set_variable("resource_name",stack.rds_name)

    # automatically name the db_subnet_name
    stack.set_variable("db_subnet_name","{}-subnet".format(stack.rds_name))

    # set username and password
    if not stack.master_username and stack.inputvars.get("DB_MASTER_USERNAME"):
        stack.set_variable("master_username",stack.inputvars["DB_MASTER_USERNAME"])
    elif not stack.master_username:
        stack.set_variable("master_username",stack.random_id(size=20))

    if not stack.master_password and stack.inputvars.get("DB_MASTER_PASSWORD"):
        stack.set_variable("master_password",stack.inputvars["DB_MASTER_PASSWORD"])
    elif not stack.master_password:
        stack.set_variable("master_password",stack.random_id(size=20))

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

    if stack.publish_creds or stack.publish_to_saas:

        # publish variables
        default_values = {"db_instance_name":stack.rds_name}
        default_values["db_root_user"] = stack.master_username
        default_values["db_root_password"] = stack.master_password
        if stack.publish_creds: default_values["publish_creds"] = True

        inputargs = {"default_values":default_values}
        inputargs["automation_phase"] = "infrastructure"
        inputargs["human_description"] = 'Publish RDS info {}'.format(stack.rds_name)
        stack.publish_rds_info.insert(display=True,**inputargs)

    return stack.get_results()

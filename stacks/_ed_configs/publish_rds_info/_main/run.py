def run(stackargs):

    # instantiate stack
    stack = newStack(stackargs)

    # add variables
    stack.parse.add_required(key="db_instance_name")
    stack.parse.add_required(key="db_root_user",default="null")
    stack.parse.add_required(key="db_root_password",default="null")

    stack.parse.add_optional(key="db_name",default="null")
    stack.parse.add_optional(key="db_user",default="null")
    stack.parse.add_optional(key="db_password",default="null")
    stack.parse.add_optional(key="publish_creds",default="null")

    # init the stack namespace
    stack.init_variables()

    _info = stack.get_resource(name=stack.db_instance_name,
                               resource_type="rds",
                               must_be_one=True)[0]

    engine = _info.get("engine")

    if stack.db_root_user: 
        root_username = stack.db_root_user
    else:
        root_username = _info.get("username")

    if stack.db_root_password: 
        root_password = stack.db_root_password
    else:
        root_password = _info.get("password")

    keys2pass = [ "db_subnet_group_name",
                  "arn",
                  "publicly_accessible",
                  "security_group_names",
                  "availability_zone",
                  "allocated_storage",
                  "instance_class",
                  "port",
                  "performance_insights_enabled",
                  "storage_type",
                  "multi_az",
                  "engine",
                  "engine_version" ]

    _public_var = stack.dict_to_dict(keys2pass,{},_info,addNone=None)

    db_endpoint = _info.get("endpoint")

    if engine and db_endpoint:
        _public_var["{}_instance_name".format(engine)] = stack.db_instance_name
        _public_var["{}_endpoint".format(engine)] = db_endpoint
        _public_var["{}_host".format(engine)] = db_endpoint

        if stack.publish_creds:

            _public_var["{}_root_user".format(engine)] = root_username
            _public_var["{}_root_password".format(engine)] = root_password

            if stack.db_name: 
                _public_var["{}_db_name".format(engine)] = stack.db_name

            if stack.db_user: 
                _public_var["{}_db_user".format(engine)] = stack.db_user

            if stack.db_password: 
                _public_var["{}_db_password".format(engine)] = stack.db_password
    elif db_endpoint:
        _public_var["db_instance_name"] = stack.db_instance_name
        _public_var["db_endpoint"] = db_endpoint
        _public_var["db_host"] = db_endpoint

        if stack.publish_creds:

            _public_var["db_root_user"] = root_username
            _public_var["db_root_password"] = root_password

            if stack.db_name: 
                _public_var["db_name"] = stack.db_name

            if stack.db_user: 
                _public_var["db_user"] = stack.db_user

            if stack.db_password: 
                _public_var["db_password"] = stack.db_password

    stack.publish(_public_var)

    return stack.get_results()

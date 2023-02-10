def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="name",default="null")
    stack.parse.add_required(key="docker_repo",default="null")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")

    # Add shelloutconfig dependencies
    stack.add_shelloutconfig('elasticdev:::aws_storage::ecr_repo',"ecr_repo_script")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()
    stack.init_shelloutconfigs()

    if stack.name:
        name = stack.name
    elif stack.docker_repo:
        name = stack.docker_repo
    else:
        msg = "We need either name or docker_repo for creating the ecr_repo"
        stack.ehandle.NeedRtInput(message=msg)

    # Check if ECR repo exists for docker images
    docker_repo = stack.check_resource(name=name,
                                       resource_type="ecr_repo",
                                       provider="aws")

    if not docker_repo:

        stack.env_vars = {"INSERT_IF_EXISTS":True}
        stack.env_vars["AWS_DEFAULT_REGION"] = stack.aws_default_region
        stack.env_vars["NAME"] = stack.name
        stack.env_vars["METHOD"] = "create"

        inputargs = {"display":True}
        inputargs["human_description"] = 'Creating AWS ecr_repo'
        inputargs["env_vars"] = json.dumps(stack.env_vars)
        inputargs["automation_phase"] = "infrastructure"
        inputargs["retries"] = 2
        inputargs["timeout"] = 180
        inputargs["wait_last_run"] = 2
        stack.ecr_repo_script.resource_exec(**inputargs)

    else:

        msg = 'ecr_repo name {} exists - creation not needed'.format(name)
        stack.logger.debug(msg)

        cmd = "sleep 1"
        stack.add_external_cmd(cmd=cmd,
                               order_type="report::shellout",
                               human_description=msg,
                               display=True,
                               role="external/cli/execute")

    return stack.get_results()

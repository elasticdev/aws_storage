from jiffycommon.serialization import b64_encode

codebuild_name = "flask-sample-private"
git_repo = "flask-sample-private"
git_url = "git@github.com:joeblow/flask_sample-private.git"
docker_repo_name = "flask_sample"
ecr_repo_name = "flask_sample"
privileged_mode = "true"
image_type = "LINUX_CONTAINER"
build_image = "aws/codebuild/standard:5.0"
build_timeout = "444"
compute_type = "BUILD_GENERAL1_SMALL"
docker_registry = "null"
aws_default_region = "eu-west-1"
trigger_id = "123456"
secret = "secret123"
branch = "master"
table_name = "codebuild-shared-ed-eval-settings"

item = { "_id":{"S": trigger_id},
         "codebuild_name":{"S": codebuild_name},
         "git_repo":{"S": git_repo},
         "git_url":{"S": git_url},
         "docker_repo_name":{"S": docker_repo_name},
         "ecr_repo_name":{"S": ecr_repo_name},
         "privileged_mode":{"S": privileged_mode},
         "image_type":{"S": image_type},
         "build_image":{"S": build_image},
         "build_timeout":{"S": build_timeout},
         "compute_type":{"S": compute_type},
         "docker_registry":{"S": docker_registry},
         "aws_default_region":{"S": aws_default_region},
         "trigger_id":{"S": trigger_id},
         "secret":{"S": secret},
         "branch":{"S": branch}
         }

print(b64_encode(item))

variable "aws_region" {
  description = "The AWS region to create resources in."
}

variable "aws_profile" {
  description = "The AWS-CLI profile for the account to create resources in."
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

terraform {
  required_version = "~> 1.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.42.0"
    }
  }
}

module "ecr" {
  source = "./modules/ecr"
}

module "iam" {
  source = "./modules/iam"
}

module "network" {
  source     = "./modules/network"
  aws_region = var.aws_region
}

module "alb" {
  source                         = "./modules/alb"
  http_server_alb_security_group = module.network.http_server_alb_security_group
  alb_subnets                    = module.network.public_subnets
  vpc_id                         = module.network.vpc_id
}


module "ecs" {
  source                              = "./modules/ecs"
  private_subnets                     = module.network.private_subnets
  http_server_security_group          = module.network.http_server_security_group
  http_server_target_group_arn        = module.alb.http_server_target_group_arn
  http_server_canary_target_group_arn = module.alb.http_server_canary_target_group_arn
  http_server_ecr_uri                 = module.ecr.http_server_ecr_uri
  http_server_canary_ecr_uri          = module.ecr.http_server_canary_ecr_uri
  ecs_task_role_arn                   = module.iam.ecs_task_role_arn
  ecs_task_execution_role_arn         = module.iam.ecs_task_execution_role_arn
}

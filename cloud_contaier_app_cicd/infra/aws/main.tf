terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = "ap-northeast-1"
}


resource "aws_ecr_repository" "sample_ecr_repository" {
  name                 = "sample-aws-ecr-repository"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}



resource "aws_iam_role" "sample_apprunner_role" {
  name = "sample-apprunner-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sample_apprunner_policy_attachment" {
  role       = aws_iam_role.sample_apprunner_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_apprunner_service" "sample_apprunner_service" {
  service_name = "sample-apprunner-service"
  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.sample_apprunner_role.arn
    }
    auto_deployments_enabled = true
    image_repository {
      image_configuration {
        port = "80"
      }
      image_identifier      = "${aws_ecr_repository.sample_ecr_repository.repository_url}:latest"
      image_repository_type = "ECR"
    }
  }
  instance_configuration {
    cpu    = 256
    memory = 512
  }
}


# actions用
resource "aws_iam_openid_connect_provider" "sample_iam_openid_connect_provider" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  # terraformの公式documentのまま
  thumbprint_list = ["cf23df2207d99a74fbe169e3eba035e633b65d94"]
}

resource "aws_iam_policy" "sample_iam_policy" {
  name        = "sample-iam-policy"
  description = "sample-iam-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
        ],
        Resource = ["*"],
      },
    ],
  })
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "sample_actions_role" {
  name = "sample-actions-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sts:AssumeRoleWithWebIdentity",
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
        },
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com",
            # FIXME: Please set your branch name
            "token.actions.githubusercontent.com:sub" = "repo:hosimesi/code-for-techblogs:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "sample_actions_role_policy_attachment" {
  role       = aws_iam_role.sample_actions_role.name
  policy_arn = aws_iam_policy.sample_iam_policy.arn
}

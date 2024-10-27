resource "aws_iam_policy" "ecs_task_execution_policy" {
  name = "ecs-task-execution-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:CreateSecurityGroup",
          "ec2:CreateTags",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs",
          "ec2:DeleteSecurityGroup",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "ssm:DescribeParameters",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "logs:PutLogEvents",
          "ecr:BatchCheckLayerAvailability"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_policy" {
  name = "ecs-task-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:CreateSecurityGroup",
          "ec2:CreateTags",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs",
          "ec2:DeleteSecurityGroup",
          "ec2:DescribeInstances",
          "aps:GetSeries",
          "aps:GetLabels",
          "aps:GetMetricMetadata",
          "ecs:CreateCluster",
          "ecs:DeleteCluster",
          "ecs:DeregisterTaskDefinition",
          "ecs:DescribeClusters",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeTasks",
          "ecs:ListAccountSettings",
          "ecs:ListClusters",
          "ecs:ListTaskDefinitions",
          "ecs:RegisterTaskDefinition",
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:UpdateService",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:GetLogEvents",
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}


resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {}
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ssm.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_execution_policy.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.arn
}


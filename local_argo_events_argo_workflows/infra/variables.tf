variable "region" {
  type    = string
  default = "asia-northeast1"
}

variable "project" {
  description = "Project where the artifact registry repositories are placed"
  type        = string
}

SHORT_SHA := $(shell git rev-parse --short HEAD)
DOCKERFILE_REPOSITORY := docker
DOCKERFILE := Dockerfile
DOCKERFILE_LOADTEST := Dockerfile.loadtest
REGION := asia-northeast1
ARTIFACT_REPOSITORY := $(REGION)-docker.pkg.dev
PROJECT_ID := $(shell gcloud config get-value project)
REPOSITORY_NAME := chat-app
IMAGE_NAME := chat-app
LOADTEST_NAME := loadtest


.PHONY: login
login:
	gcloud auth login --update-adc

.PHONY: plan
plan:
	terraform -chdir=infra plan -var-file=local.tfvars

.PHONY: apply
apply:
	terraform -chdir=infra apply -var-file=local.tfvars

.PHONY: destroy
destroy:
	terraform -chdir=infra destroy -var-file=local.tfvars

.PHONY: build
build:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	# docker buildx build --platform=linux/amd64 -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	# docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):latest
	docker buildx build --platform=linux/amd64 -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(LOADTEST_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_LOADTEST) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(LOADTEST_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(LOADTEST_NAME):latest

.PHONY: push
push:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	# docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA)
	# docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):latest
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(LOADTEST_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(LOADTEST_NAME):latest


.PHONY: loadtest-local
loadtest-local:
	docker exec -it loadtest k6 run loadtest/main.js

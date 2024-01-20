SHORT_SHA := $(shell git rev-parse --short HEAD)
PROJECT_ENV := <your-config-env>
DOCKERFILE_REPOSITORY := docker
DOCKERFILE := Dockerfile
REGION := asia-northeast1
ARTIFACT_REPOSITORY := $(REGION)-docker.pkg.dev
PROJECT_ID := $(shell gcloud config get-value project)
REPOSITORY_NAME := inference-on-secure-cloud-run
INFERENCE_IMAGE_NAME := inference
TRAIN_IMAGE_NAME := train


.PHONY: login
login:
	gcloud auth login
	gcloud auth application-default login
	gcloud config configurations activate $(PROJECT_ENV)

.PHONY: build/train
build/train:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker buildx build --platform=linux/amd64 --target train -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):latest

.PHONY: build/inference
build/inference:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker buildx build --platform=linux/amd64 --target inference -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):latest

.PHONY: build
build:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker buildx build --platform=linux/amd64 --target train -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):latest
	docker buildx build --platform=linux/amd64 --target inference -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):latest

.PHONY: push/train
push/train:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):latest

.PHONY: push/inference
push/inference:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):latest

.PHONY: push
push:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):latest
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):latest

.PHONY: run/train
run/train:
	docker run -it --rm \
		$(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(TRAIN_IMAGE_NAME):$(SHORT_SHA)

.PHONY: run/inference
run/inference:
	docker run -it --rm \
		$(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(INFERENCE_IMAGE_NAME):$(SHORT_SHA)


.PHONY: request
request:
	curl -X POST http:/<your-lb-ip>/inference/ -H 'Content-Type: application/json' -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'

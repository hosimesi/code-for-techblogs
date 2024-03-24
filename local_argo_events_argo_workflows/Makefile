SHORT_SHA := $(shell git rev-parse --short HEAD)
GCP_ENV := <your-env> # FIXME: set your GCP environment
DOCKERFILE_REPOSITORY := docker
DOCKERFILE := Dockerfile
REGION := asia-northeast1
ARTIFACT_REPOSITORY := $(REGION)-docker.pkg.dev
PROJECT_ID := $(shell gcloud config get-value project)
REPOSITORY_NAME := argo-workflows
IMAGE_NAME := argo-workflows
ARGO_WORKFLOWS_SERVICE_ACCOUNT_EMAIL := argo-workflows-sa@$(PROJECT_ID).iam.gserviceaccount.com
ARGO_EVENTS_SERVICE_ACCOUNT_EMAIL := argo-events-sa@$(PROJECT_ID).iam.gserviceaccount.com
ARGO_WORKFLOWS_KEY := argo_workflows_key.json
ARGO_EVENTS_KEY := argo_events_key.json
DOCKER_CREDENTIAL_NAME := docker-credentials
GCP_CREDENTIAL_NAME := gcp-credentials
ARGO_WORKFLOW_NAMESPACE := argo
ARGO_EVENTS_NAMESPACE := argo-events


.PHONY: login
login:
	gcloud auth login
	gcloud config configurations activate $(GCP_ENV)
	gcloud auth application-default login

.PHONY: build
build:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker buildx build --platform=linux/amd64 --target local -t $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE) .
	docker tag $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA) $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):latest

.PHONY: push
push:
	gcloud auth configure-docker asia-northeast1-docker.pkg.dev
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):$(SHORT_SHA)
	docker push $(ARTIFACT_REPOSITORY)/$(PROJECT_ID)/$(REPOSITORY_NAME)/$(IMAGE_NAME):latest

.PHONY: format  ## Run linter and formatter
format:
	poetry run black .
	poetry run ruff . --fix
	poetry run mypy . --no-site-packages


.PHONY: kind
kind:
	kind create cluster
	kind get nodes


.PHONY: argo-install
argo-install:
	kubectl kustomize ./argo-infra/argo-events/overlays/local | kubectl apply -f -
	kubectl kustomize ./argo-infra/argo-workflows/overlays/local | kubectl apply -f -
	kubectl kustomize ./argo-infra/event-bus/overlays/local | kubectl apply -f -
	# kubectl kustomize ./argo-infra/external-secret/overlays/local | kubectl apply -f -


# FIXME: set your mail address
.PHONY: create-secret
create-secret:
	gcloud iam service-accounts keys create --iam-account $(ARGO_WORKFLOWS_SERVICE_ACCOUNT_EMAIL) $(ARGO_WORKFLOWS_KEY)
	gcloud iam service-accounts keys create --iam-account $(ARGO_EVENTS_SERVICE_ACCOUNT_EMAIL) $(ARGO_EVENTS_KEY)
	kubectl create secret docker-registry $(DOCKER_CREDENTIAL_NAME) \
        --docker-server=https://$(REGION)-docker.pkg.dev \
        --docker-username=_json_key \
        --docker-password="`cat $(ARGO_WORKFLOWS_KEY)`" \
        --docker-email=<your-mail-address> \
        --namespace=$(ARGO_WORKFLOW_NAMESPACE)
	kubectl create secret generic $(GCP_CREDENTIAL_NAME) --from-file=key.json=$(ARGO_WORKFLOWS_KEY) --namespace=$(ARGO_WORKFLOW_NAMESPACE)
	kubectl create secret generic $(GCP_CREDENTIAL_NAME) --from-file=key.json=$(ARGO_EVENTS_KEY) --namespace=$(ARGO_EVENTS_NAMESPACE)
	kubectl create secret generic $(GCP_CREDENTIAL_NAME) --from-file=key.json=$(ARGO_WORKFLOWS_KEY)
	rm $(ARGO_WORKFLOWS_KEY) $(ARGO_EVENTS_KEY)


.PHONY: plan
plan:
	terraform plan -var-file=local.tfvars

.PHONY: apply
apply:
	terraform apply -var-file=local.tfvars


.PHONY: update
update:
	poetry lock
	poetry install --sync --no-root
	poetry run task update_dev
	poetry run task update_app


.PHONY: deploy
deploy:
	kubectl kustomize ./workflows/overlays/local | kubectl apply -f -
	argo submit -n $(ARGO_WORKFLOW_NAMESPACE) --watch ./workflows/overlays/local/run-workflow.yaml


.PHONY: port-forward
port-forward:
	kubectl -n $(ARGO_WORKFLOW_NAMESPACE) port-forward deployment/argo-server 2746:2746


.PHONY: notify
notify:
	gsutil notification create -f json -t argo-workflows-topic gs://argo-workflows-bucket


.PHONY: upload
upload:
	gsutil cp original.csv gs://argo-workflows-bucket/test/original.csv

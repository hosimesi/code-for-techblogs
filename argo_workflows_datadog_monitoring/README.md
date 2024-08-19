# argo_workflows_datadog_monitoring
# Overview
Repository for Montoring Argo Workflows using Datadog .\
blog link: https://zenn.dev/articles/7c168941b33341


# How to use
1. Change directory.
    ```bash
    cd path/to/argo_workflows_datadog_monitoring/infra
    ```
2. Create Google Cloud Resource
    ```bash
    $ terraform init
    ```
    ```bash
    $ terraform plan
    ```
    ```bash
    $ terraform apply
    ```
3. Create Argo Workflows
    ```bash
    $ helm repo add argo https://argoproj.github.io/argo-helm
    ```
    ```bash
    $ helm install --create-namespace --namespace argo argo-workflows argo/argo-workflows
    ```
4. Install Datadog Agent
    ```bash
    $ helm repo add datadog https://helm.datadoghq.com
    ```
    ```bash
    $ helm repo update
    ```
    ```bash
    $ kubectl create secret generic datadog-secret --from-literal api-key=<your-api-key>
    ```
5. Deploy Datadog Agent
    ```bash
    $ kubectl apply -f datadog-agent.yaml
    ```
6. Update Deployment
    ```bash
    $ kubectl apply -f workflow-controller-values.yaml
    ```

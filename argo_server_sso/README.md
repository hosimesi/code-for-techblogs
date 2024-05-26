# Overview
Repository for Argo Workflows used SSO .\
blog link: https://zenn.dev/hosimesi/articles/d8cabcf1c53080


# How to use
1. The cloud you want to build.
    ```bash
    $ cd path/to/infra
    ```
2. Change FIXME to suit your own environment.
3. Apply Resource.
    ```bash
    $ terraform init
    ```
    ```bash
    $ terraform plan
    ```
    ```bash
    $ terraform apply
    ```
4. Apply to GKE(namespace)
    ```bash
    $ kubectl apply -f argoworkflows/base/namespace.yaml
    ```
5. Apply to GKE
    ```bash
    $ kubectl apply -k argoworkflows/overlays/dev
    ```

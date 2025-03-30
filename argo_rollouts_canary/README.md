# argo_rollouts_canary
## Overview
Repository for Argo Rollouts.\
blog link: https://zenn.dev/hosimesi/articles/65f06185a9be79


## How to use
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
5. Apply to GKE resouce
    ```bash
    $ kubectl apply -f **/**.yaml
    ```

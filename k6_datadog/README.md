# k6_datadog
# Overview
Repository for Stress test with k6 and Datadog \
blog link: https://zenn.dev/hosimesi/articles/8368d79e93b3ae


# How to use
1. Change directory.
    ```bash
    cd path/to/fastapi_profiling
    ```
2. Replace Varivable
    - project id
3. Run debugger in Docker
    ```bash
    $ docker compose up --build
    ```
4. Create Google Cloud Resource
   ```bash
    $ make plan
   ```
   ```bash
    $ make apply
   ```
5. Create GKE Resource
    ```bash
    $ kubectl -k ./k8s/overlays/
    ```
6. Build Datadog Agent
    ```bash
    $ kubectl -k ./k8s/overlays/datadog-agent.yaml
    ```
7. 
   <!-- kubctl apply -f ./k8s/overlays/job.yaml -->

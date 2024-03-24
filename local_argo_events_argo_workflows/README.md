# Overview
Local Argo Workflows and Argo events.\
blog link: https://zenn.dev/articles/4fbd8d43d1f11a

# Pre-requirements
1. Install kind, kubectl, kustomize, poetry
    ```bash
    $ pip list | grep poetry
    poetry                      1.7.1
    poetry-core                 1.8.1
    poetry-plugin-export        1.6.0
    ```
    ```bash
    $ brew install kind
    ```
    ```bash
    $ brew install kubectl
    ```
    ```bash
    $ brew install kustomize
    ```

# How to run in local.
1. Auth gcloud.
    ```Makefile
    $ make login
    ```
2. Create gcp resource.
    ```bash
    $ terraform apply -var-file=<variables file>
    ```
3. Build image.
    ```bash
    $ make build
    ```
4. Push image.
    ```bash
    $ make push
    ```
5. Create kind.
    ```bash
    $ make kind
    ```
6. Install argo.
    ```bash
    $ make argo-install
    ```
7. Create secret.
    ```bash
    $ make create-secret
    ```
8. Deploy workflow.
    ```bash
    $ make deploy
    ```
9. Set notify.
    ```bash
    $ make notify
    ```
10. Upload titanic files.
    ```bash
    $ make upload
    ```



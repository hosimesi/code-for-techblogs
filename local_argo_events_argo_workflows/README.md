# Overview
IP-restricted secure inference endpoints on Cloud Run.\
blog link: https://zenn.dev/hosimesi/articles/36fedaa5425c7b

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

2. Auth gcloud.
    ```Makefile
    $ make login
    ```

3. Create gcp resource.
    ```bash
    $ make apply
    ```

4. Push image.
    ```bash
    $ make push
    ```

<!-- # How to use in local
```bash
cd path/to/inference_on_secure_cloud_run
```

## Train
1. Run train in local
    ```Makefile
    $ make train
    ```


## Inference Server
1. Upload to your trained model to GCS.
   ```bash
    $ gsutil cp train/model.pkl gs://inference-on-secure-cloud-run/artifacts/model.pkl
   ```

2. Edit docker-compose.yaml
    ```yaml
        environment:
        - CLOUDSDK_CONFIG=/root/.config/gcloud
        - GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json
        - GOOGLE_CLOUD_PROJECT=<your-project>
    ```

3. Run up.
    ```yaml
    $ docker compose up --build
    ```

# How to deploy
1. Set FIXME in code for your environment.
2. Plan
    ```bash
    $ terraform plan
    ```
3. Deploy
    ```bash
    $ terraform apply
    ```
4. Destroy
    ```bash
    $ terraform destroy
    ``` -->

# Overview

# Pre-requirements

# How to use in local
1. Edit docker-compose.yaml
```
    environment:
      - CLOUDSDK_CONFIG=/root/.config/gcloud
      - GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json
      - GOOGLE_CLOUD_PROJECT=<your-project>
```


# How to deploy
```
terraform apply
```


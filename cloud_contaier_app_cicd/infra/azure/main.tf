terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.89.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47.0"
    }
  }
}

provider "azuread" {
  # FIXME: Replace with your tenant ID
  tenant_id = "your-tenant-id"
}


provider "azurerm" {
  skip_provider_registration = true
  # FIXME: Replace with your subscription ID
  subscription_id = "your-subscription-id"
  features {}
}


resource "azurerm_resource_group" "sample_resource_group" {
  name     = "sample-azure-resource-group"
  location = "japaneast"
}

resource "azurerm_container_registry" "sample_container_registry" {
  name                = "sampleazurecontainerregistryhoshii" # FIXME: Replace with your container registry name
  resource_group_name = azurerm_resource_group.sample_resource_group.name
  location            = azurerm_resource_group.sample_resource_group.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_user_assigned_identity" "sample_container_app_user_assigned_identity" {
  name                = "sample-azure-container-app-identity"
  location            = azurerm_resource_group.sample_resource_group.location
  resource_group_name = azurerm_resource_group.sample_resource_group.name
}

resource "azurerm_role_assignment" "sample_container_registry_role_assignment" {
  scope                = azurerm_container_registry.sample_container_registry.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.sample_container_app_user_assigned_identity.principal_id
}


resource "azurerm_container_app_environment" "sample_container_app_environment" {
  name                = "sample-azure-container-app-environment"
  location            = azurerm_resource_group.sample_resource_group.location
  resource_group_name = azurerm_resource_group.sample_resource_group.name
}

resource "azurerm_container_app" "sample_container_app" {
  name                         = "sample-azure-container-app"
  container_app_environment_id = azurerm_container_app_environment.sample_container_app_environment.id
  resource_group_name          = azurerm_resource_group.sample_resource_group.name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.sample_container_app_user_assigned_identity.id]
  }

  registry {
    server   = azurerm_container_registry.sample_container_registry.login_server
    identity = azurerm_user_assigned_identity.sample_container_app_user_assigned_identity.id
  }

  ingress {
    external_enabled = true
    target_port      = 80
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    container {
      name = "sample-azure-container-app"
      # FIXME: Replace with your image name
      image  = "${azurerm_container_registry.sample_container_registry.login_server}/sample-azure-repository:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }
}


# actions用
data "azuread_domains" "sample-azuread-domains" {
  only_initial = true
}

# Retrieve client configuration
data "azuread_client_config" "current" {}

# Create an application
resource "azuread_application" "sample-github-actions-azuread-application" {
  display_name = "sample-github-actions-azuread-app"
  owners       = [data.azuread_client_config.current.object_id]
}

# Create a service principal
resource "azuread_service_principal" "sample-github-actions-azuread-service-principal" {
  client_id = azuread_application.sample-github-actions-azuread-application.client_id
  owners    = [data.azuread_client_config.current.object_id]
}

# Create a federated identity credential
resource "azuread_application_federated_identity_credential" "sample-github-actions-azuread-app-federated-identity-credential" {
  application_id = "/applications/${azuread_application.sample-github-actions-azuread-application.object_id}"
  display_name   = "sample-github-actions-azuread-app-federated-identity-credential"
  description    = "Federated identity credential for GitHub Actions"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:hosimesi/code-for-techblogs:ref:refs/heads/main"
}

# ACR Push Role
data "azurerm_role_definition" "acrpush" {
  name = "AcrPush"
}

# Contributor Role
data "azurerm_role_definition" "contributor" {
  name = "Contributor"
}

# Role Assignment to application
resource "azurerm_role_assignment" "acrpush" {
  scope                = azurerm_container_registry.sample_container_registry.id
  role_definition_name = data.azurerm_role_definition.acrpush.name
  principal_id         = azuread_service_principal.sample-github-actions-azuread-service-principal.object_id
}

# Role Assignment to container apps
resource "azurerm_role_assignment" "contributor" {
  scope                = azurerm_container_app.sample_container_app.id
  role_definition_name = data.azurerm_role_definition.contributor.name
  principal_id         = azuread_service_principal.sample-github-actions-azuread-service-principal.object_id
}


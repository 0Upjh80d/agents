metadata description = 'Creates an Azure AI Foundry Project'
param name string
param location string = resourceGroup().location
param tags object = {}

param displayName string = name
param hubName string
param keyVaultName string
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Enabled'
param skuName string = 'Basic'
@allowed(['Basic', 'Free', 'Premium', 'Standard'])
param skuTier string = 'Basic'

resource hub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' existing = {
  name: hubName
}

resource project 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuTier
  }
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: displayName
    hbiWorkspace: false
    v1LegacyMode: false
    publicNetworkAccess: publicNetworkAccess
    hubResourceId: hub.id
  }
}

module keyVaultAccess '../security/keyvault-access.bicep' = {
  name: 'keyvault-access'
  params: {
    keyVaultName: keyVaultName
    principalId: project.identity.principalId
  }
}

module amlDataScientistServiceRole '../security/role.bicep' = {
  name: 'aml-data-scientist-service-role'
  params: {
    principalId: project.identity.principalId
    roleDefinitionId: 'f6c7c914-8db3-469d-8ca1-694a8f32e121' // AzureML Data Scientist
    principalType: 'ServicePrincipal'
  }
}

module amlSecretsReaderServiceRole '../security/role.bicep' = {
  name: 'aml-secrets-reader-service-role'
  params: {
    principalId: project.identity.principalId
    roleDefinitionId: 'ea01e6af-a1c1-4350-9563-ad00f8c72ec5' // Azure Machine Learning Workspace Connection Secrets Reader
    principalType: 'ServicePrincipal'
  }
}

output id string = project.id
output name string = project.name
output principalId string = project.identity.principalId

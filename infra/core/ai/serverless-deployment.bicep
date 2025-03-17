metadata description = 'Creates an serverless deployment in Azure AI Foundry'
param name string
param location string = resourceGroup().location
param tags object = {}

@maxLength(32)
param endpointName string = ''
param keyVaultName string
param modelId string = ''
param modelName string = ''
param registry string = ''
param primaryKeySecretName string = 'massEndpointPrimaryKey'
param secondaryKeySecretName string = 'massEndpointSecondaryKey'

var modelId_ = !empty(modelId) ? modelId : 'azureml://registries/${registry}/models/${modelName}'
var subscriptionName = '${modelName}-subscription'
var endpointName_ = !empty(endpointName) ? endpointName : take(replace(replace('${modelName}', '_', '-'), '.', '-'), 32)

resource marketplaceSubscription 'Microsoft.MachineLearningServices/workspaces/marketplaceSubscriptions@2024-10-01' = if (!startsWith(
  modelId_,
  'azureml://registries/azureml/'
)) {
  name: replace('${name}/${subscriptionName}', '.', '-')
  properties: {
    modelId: modelId_
  }
}

resource maasEndpoint 'Microsoft.MachineLearningServices/workspaces/serverlessEndpoints@2024-10-01' = {
  name: '${name}/${endpointName_}'
  location: location
  sku: {
    name: 'Consumption'
  }
  properties: {
    modelSettings: {
      modelId: modelId_
    }
    authMode: 'Key'
  }
  dependsOn: [
    marketplaceSubscription
  ]
}

module massEndpointPrimaryKey '../security/keyvault-secret.bicep' = {
  name: 'mass-primary-key-secret'
  params: {
    name: primaryKeySecretName
    tags: tags
    keyVaultName: keyVaultName
    secretValue: maasEndpoint.listKeys().primaryKey
  }
}

module massEndpointSecondaryKey '../security/keyvault-secret.bicep' = {
  name: 'mass-secondary-key-secret'
  params: {
    name: secondaryKeySecretName
    tags: tags
    keyVaultName: keyVaultName
    secretValue: maasEndpoint.listKeys().secondaryKey
  }
}

output endpointUri string = maasEndpoint.properties.inferenceEndpoint.uri

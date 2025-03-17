metadata description = 'Creates the Hub dependencies'
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsName string = ''
param containerRegistryName string = ''
param keyVaultName string
param logAnalyticsName string = ''
param openAiModelDeployments array = []
param openAiServiceName string
param openAiServiceLocation string
param storageAccountName string

module keyVault '../security/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    name: keyVaultName
    location: location
    tags: tags
  }
}

module storageAccount '../storage/storage-account.bicep' = {
  name: 'storage-account'
  params: {
    name: storageAccountName
    location: location
    tags: tags
    containers: [
      {
        name: 'default'
      }
    ]
    files: [
      {
        name: 'default'
      }
    ]
    queues: [
      {
        name: 'default'
      }
    ]
    tables: [
      {
        name: 'default'
      }
    ]
    corsRules: [
      {
        allowedOrigins: [
          'https://mlworkspace.azure.ai'
          'https://ml.azure.com'
          'https://*.ml.azure.com'
          'https://ai.azure.com'
          'https://*.ai.azure.com'
          'https://mlworkspacecanary.azure.ai'
          'https://mlworkspace.azureml-test.net'
        ]
        allowedMethods: [
          'GET'
          'HEAD'
          'POST'
          'PUT'
          'DELETE'
          'OPTIONS'
          'PATCH'
        ]
        maxAgeInSeconds: 1800
        exposedHeaders: [
          '*'
        ]
        allowedHeaders: [
          '*'
        ]
      }
    ]
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: false
    }
    shareDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

module logAnalytics '../monitor/loganalytics.bicep' = {
  name: 'log-analytics'
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

module applicationInsights '../monitor/applicationinsights.bicep' = if (!empty(applicationInsightsName)) {
  name: 'application-insights'
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

module containerRegistry '../host/container-registry.bicep' = if (!empty(containerRegistryName)) {
  name: 'container-registry'
  params: {
    name: containerRegistryName
    location: location
    tags: tags
  }
}

module cognitiveServices '../ai/cognitive-services.bicep' = {
  name: 'cognitive-services'
  params: {
    name: openAiServiceName
    location: openAiServiceLocation
    tags: tags
    kind: 'AIServices'
    deployments: openAiModelDeployments
  }
}

output keyVaultId string = keyVault.outputs.id
output keyVaultName string = keyVault.outputs.name
output keyVaultEndpoint string = keyVault.outputs.endpoint

output storageAccountId string = storageAccount.outputs.id
output storageAccountName string = storageAccount.outputs.name

output containerRegistryId string = !empty(containerRegistryName) ? containerRegistry.outputs.id : ''
output containerRegistryName string = !empty(containerRegistryName) ? containerRegistry.outputs.name : ''
output containerRegistryEndpoint string = !empty(containerRegistryName) ? containerRegistry.outputs.loginServer : ''

output applicationInsightsId string = !empty(applicationInsightsName) ? applicationInsights.outputs.id : ''
output applicationInsightsName string = !empty(applicationInsightsName) ? applicationInsights.outputs.name : ''
output applicationInsightsConnectionString string = !empty(applicationInsightsName)
  ? applicationInsights.outputs.connectionString
  : ''
output logAnalyticsWorkspaceId string = !empty(logAnalyticsName) ? logAnalytics.outputs.id : ''
output logAnalyticsWorkspaceName string = !empty(logAnalyticsName) ? logAnalytics.outputs.name : ''

output openAiId string = cognitiveServices.outputs.id
output openAiServiceName string = cognitiveServices.outputs.name
output openAiServiceLocation string = cognitiveServices.outputs.location
output openAiEndpoint string = cognitiveServices.outputs.endpoints['OpenAI Language Model Instance API']

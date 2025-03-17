metadata description = 'Creates the AI environment'
param location string = resourceGroup().location
param tags object = {}

param aiHubName string
param aiProjectName string
param applicationInsightsName string
param containerRegistryName string
param deployments array = []
param keyVaultName string
param logAnalyticsName string
param openAiApiVersion string
param openAiConnectionName string
param openAiServiceName string
param openAiServiceLocation string
param storageAccountName string

var openAiDeployments = filter(deployments, deployment => toLower(deployment.platform) == 'openai')
var serverlessDeployments = filter(deployments, deployment => toLower(deployment.platform) == 'serverless')

module hubDependencies './hub-dependencies.bicep' = {
  name: 'hub-dependencies'
  params: {
    location: location
    tags: tags
    keyVaultName: keyVaultName
    storageAccountName: storageAccountName
    containerRegistryName: containerRegistryName
    applicationInsightsName: applicationInsightsName
    logAnalyticsName: logAnalyticsName
    openAiServiceName: openAiServiceName
    openAiModelDeployments: openAiDeployments
    openAiServiceLocation: openAiServiceLocation
  }
}

module hub './hub.bicep' = {
  name: 'hub'
  params: {
    name: aiHubName
    location: location
    tags: tags
    displayName: aiHubName
    keyVaultId: hubDependencies.outputs.keyVaultId
    storageAccountId: hubDependencies.outputs.storageAccountId
    containerRegistryId: hubDependencies.outputs.containerRegistryId
    applicationInsightsId: hubDependencies.outputs.applicationInsightsId
    openAiServiceName: hubDependencies.outputs.openAiServiceName
    openAiConnectionName: openAiConnectionName
  }
}

module project './project.bicep' = {
  name: 'project'
  params: {
    location: location
    tags: tags
    name: aiProjectName
    displayName: aiProjectName
    hubName: hub.outputs.name
    keyVaultName: hubDependencies.outputs.keyVaultName
  }
}

@batchSize(1)
module serverlessDeployment './serverless-deployment.bicep' = [
  for deployment in serverlessDeployments: {
    name: replace(deployment.name, '.', '-')
    params: {
      name: project.outputs.name
      modelId: deployment.model.?id
      modelName: deployment.model.?name
      registry: deployment.model.?registry
      endpointName: deployment.name
      keyVaultName: hubDependencies.outputs.keyVaultName
    }
  }
]

// Outputs
// Resource Group
output resourceGroupName string = resourceGroup().name
// Azure AI Foundry Hub
output hubName string = hub.outputs.name
output hubPrincipalId string = hub.outputs.principalId
// Azure AI Foundry Project
output projectName string = project.outputs.name
output projectPrincipalId string = project.outputs.principalId
// Azure Key Vault
output keyVaultName string = hubDependencies.outputs.keyVaultName
output keyVaultEndpoint string = hubDependencies.outputs.keyVaultEndpoint
// Azure Application Insights
output applicationInsightsName string = hubDependencies.outputs.applicationInsightsName
output applicationInsightsConnectionString string = hubDependencies.outputs.applicationInsightsConnectionString
output logAnalyticsWorkspaceName string = hubDependencies.outputs.logAnalyticsWorkspaceName
// Azure Container Registry
output containerRegistryName string = hubDependencies.outputs.containerRegistryName
output containerRegistryEndpoint string = hubDependencies.outputs.containerRegistryEndpoint
// Azure Storage Account
output storageAccountName string = hubDependencies.outputs.storageAccountName
// Azure OpenAI Service
output openAiServiceName string = hubDependencies.outputs.openAiServiceName
output openAiServiceLocation string = hubDependencies.outputs.openAiServiceLocation
output openAiEndpoint string = hubDependencies.outputs.openAiEndpoint

output serverlessDeployments array = [
  for (deployment, i) in serverlessDeployments: {
    name: deployment.name
    endpointUri: serverlessDeployment[i].outputs.endpointUri
  }
]

output openAiDeployments array = [
  for (deployment, i) in openAiDeployments: {
    name: deployment.name
    endpointUri: hubDependencies.outputs.openAiEndpoint
  }
]

output deployments array = [
  for (deployment, i) in deployments: union(deployment, {
    endpointUri: deployment.platform == 'serverless'
      ? serverlessDeployment[i].outputs.endpointUri
      : hubDependencies.outputs.openAiEndpoint
    apiVersion: openAiApiVersion
  })
]

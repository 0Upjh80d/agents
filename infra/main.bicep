targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@description('Tenant id for the subscription')
param tenantId string = subscription().tenantId

@description('Id of the user or app to assign application roles')
param principalId string

@description('Id of the group to assign application roles')
param groupPrincipalId string // Set in main.parameters.json

@description('Name of the resource group')

@description('Name of the AI hub')
param aiHubName string = ''

@description('Name of the AI project')
param aiProjectName string = ''

@description('Name of the key vault')
param keyVaultName string = ''

@description('Name of the storage account')
param storageAccountName string = ''

@description('Name of the OpenAI service')
param openAiServiceName string = ''

@description('Name of the OpenAI connection name')
param openAiConnectionName string = ''

@allowed([
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'switzerlandnorth'
  'uksouth'
  'japaneast'
  'northcentralus'
  'australiaeast'
  'swedencentral'
])
@metadata({
  azd: {
    type: 'location'
  }
})
@description('Location of the OpenAI service')
param openAiServiceLocation string // Set in main.parameters.json

@description('Version of the OpenAI API')
param openAiApiVersion string // Set in main.parameters.json

var aiConfig = loadYamlContent('ai.yaml')

// List of models we know how to deploy
var allDeployments = array(aiConfig.?deployments ?? [])

@description('Name of the log analytics workspace')
param logAnalyticsName string = ''

@description('Name of the application insights')
param applicationInsightsName string = ''

@description('Name of the container registry')
param containerRegistryName string = ''

@description('Name of the managed identity')
param identityName string = ''

@description('Use Application Insights')
param useApplicationInsights bool // Set in main.parameters.json

@description('Use Container Registry')
param useContainerRegistry bool // Set in main.parameters.json

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

@description('Whether the deployment is running on Azure DevOps Pipeline')
param runningOnAdo string = ''

var abbrs = loadJsonContent('abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'

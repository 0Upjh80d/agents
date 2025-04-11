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
param resourceGroupName string = ''

@description('Name of the AI hub')
param aiHubName string = ''

@description('Name of the AI project')
param aiProjectName string = ''

@description('Name of the Azure Key Vault')
param keyVaultName string = ''

@description('Name of the Azure Storage Account')
param storageAccountName string = ''

@description('Name of the Azure OpenAI service')
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
@description('Location of the Azure OpenAI service')
param openAiServiceLocation string // Set in main.parameters.json

@description('Version of the OpenAI API')
param openAiApiVersion string // Set in main.parameters.json

var aiConfig = loadYamlContent('ai.yaml')

// List of models we know how to deploy
var allDeployments = array(aiConfig.?deployments ?? [])

@description('Name of the Azure Cosmos DB Account')
param cosmosDbAccountName string = ''

@description('Name of the Azure Cosmos DB database for audit logs')
param auditDatabaseName string = 'audit_events'

@description('Name of the Azure Cosmos DB collection for audit logs')
param auditCollectionName string = 'audit_events'

@description('Name of the Log Analytics Workspace')
param logAnalyticsName string = ''

@description('Name of the Application Insights')
param applicationInsightsName string = ''

@description('Name of the Azure Container Registry')
param containerRegistryName string = ''

@description('Name of the Managed Identity')
param identityName string = ''

@description('Use Application Insights')
param useApplicationInsights bool // Set in main.parameters.json

@description('Use Container Registry')
param useContainerRegistry bool // Set in main.parameters.json

@description('Whether to deploy an Azure Cosmos DB Account')
param deployCosmosDb bool // Set in main.parameters.json

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
  location: location
  tags: tags
}

// USER ROLES
var principalType = empty(runningOnGh) && empty(runningOnAdo) ? 'User' : 'ServicePrincipal'

module managedIdentity './core/security/managed-identity.bicep' = {
  name: 'managed-identity'
  scope: resourceGroup
  params: {
    name: !empty(identityName) ? identityName : '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
    location: location
    tags: tags
  }
}

module openAiRoleUser './core/security/role.bicep' = if (!empty(principalId)) {
  scope: resourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalType: principalType
  }
}

module openAiRoleContributor './core/security/role.bicep' = if (!empty(principalId)) {
  scope: resourceGroup
  name: 'openai-role-contributor'
  params: {
    principalId: principalId
    roleDefinitionId: 'a001fd3d-188f-4b5d-821b-7da978bf7442' // Cognitive Services OpenAI Contributor
    principalType: principalType
  }
}

module appInsightsAccountRole 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'appinsights-account-role'
  params: {
    principalId: managedIdentity.outputs.principalId
    roleDefinitionId: '3913510d-42f4-4e42-8a64-420c390055eb' // Monitoring Metrics Publisher
    principalType: 'ServicePrincipal'
  }
}

module groupKeyVaultAccess './core/security/keyvault-access.bicep' = {
  name: 'group-keyvault-access'
  scope: resourceGroup
  params: {
    keyVaultName: aiEnvironment.outputs.keyVaultName
    principalId: groupPrincipalId
  }
}

module aiEnvironment './core/ai/ai-environment.bicep' = {
  name: 'ai-environment'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    aiHubName: !empty(aiHubName) ? aiHubName : 'hub-${resourceToken}'
    aiProjectName: !empty(aiProjectName) ? aiProjectName : 'proj-${resourceToken}'
    keyVaultName: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    storageAccountName: !empty(storageAccountName)
      ? storageAccountName
      : '${abbrs.storageStorageAccounts}${resourceToken}'
    openAiServiceName: !empty(openAiServiceName)
      ? openAiServiceName
      : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    openAiServiceLocation: openAiServiceLocation
    openAiConnectionName: !empty(openAiConnectionName)
      ? openAiConnectionName
      : '${abbrs.cognitiveServicesAccounts}connection'
    openAiApiVersion: openAiApiVersion
    deployments: allDeployments
    logAnalyticsName: !useApplicationInsights
      ? ''
      : !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !useApplicationInsights
      ? ''
      : !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
    containerRegistryName: !useContainerRegistry
      ? ''
      : !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
  }
}

module mongoDbAudit './core/database/cosmos/mongo/cosmos-mongo-db.bicep' = {
  name: 'mongo-db-audit'
  scope: resourceGroup
  params: {
    name: !empty(cosmosDbAccountName) ? cosmosDbAccountName : '${abbrs.documentDBMongoDatabaseAccounts}${resourceToken}'
    location: location
    tags: tags
    databaseName: auditDatabaseName
    collections: [
      {
        id: auditCollectionName
        name: auditCollectionName
        shardKey: 'id'
        indexKey: '_id'
      }
    ]
    reuseCosmosDb: true
    existingCosmosDbResourceGroupName: '${abbrs.resourcesResourceGroups}${environmentName}' // rg-agents
    existingCosmosDbAccountName: '${abbrs.documentDBMongoDatabaseAccounts}${resourceToken}' // cosmon-zw3uvhgul6x4g
    deployCosmosDb: deployCosmosDb
    keyVaultName: keyVaultName
    secretName: 'cosmosdbConnectionString'
  }
}

output AZURE_LOCATION string = location
output AZURE_PRINCIPAL_ID string = principalId
output AZURE_GROUP_PRINCIPAL_ID string = groupPrincipalId
output AZURE_TENANT_ID string = tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_AI_FOUNDRY_HUB_NAME string = aiEnvironment.outputs.hubName
output AZURE_AI_FOUNDRY_PROJECT_NAME string = aiEnvironment.outputs.projectName
output AZURE_KEYVAULT_NAME string = aiEnvironment.outputs.keyVaultName
output AZURE_STORAGE_ACCOUNT_NAME string = aiEnvironment.outputs.storageAccountName
output AZURE_OPENAI_SERVICE string = aiEnvironment.outputs.openAiServiceName
output AZURE_OPENAI_SERVICE_LOCATION string = aiEnvironment.outputs.openAiServiceLocation
output AZURE_OPENAI_API_VERSION string = openAiApiVersion

output AZURE_LOGANALYTICS_NAME string = aiEnvironment.outputs.logAnalyticsWorkspaceName
output AZURE_APPLICATIONINSIGHTS_NAME string = aiEnvironment.outputs.applicationInsightsName
output APPINSIGHTS_CONNECTIONSTRING string = aiEnvironment.outputs.applicationInsightsConnectionString

output AZURE_CONTAINERREGISTRY_NAME string = aiEnvironment.outputs.containerRegistryName

output AZURE_AUDIT_DATABASE string = mongoDbAudit.outputs.databaseName

output USE_APPLICATION_INSIGHTS bool = useApplicationInsights
output USE_CONTAINER_REGISTRY bool = useContainerRegistry
output DEPLOY_COSMOS_DB bool = deployCosmosDb

// Environment variables are exported during post-processing because Bicep cannot conditionally define outputs
// The names of the outputs for deployments depend on whether the platforn is openai or serverless
// For openai => AZURE_OPENAI_DEPLOYMENT and AZURE_OPENAI_ENDPOINT
// For serverless => OPENAI_DEPLOYMENT and OPENAI_BASE_URL
output DEPLOYMENTS array = aiEnvironment.outputs.deployments

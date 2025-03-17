metadata description = 'The AI Foundry Hub Resource name'
param name string
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsId string
param containerRegistryId string
param displayName string = name
param keyVaultId string
param openAiConnectionName string
param openAiServiceName string
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Enabled'
param skuName string = 'Basic'
@allowed(['Basic', 'Free', 'Premium', 'Standard'])
param skuTier string = 'Basic'
param storageAccountId string

resource openAi 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: openAiServiceName
}

resource hub 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuTier
  }
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: displayName
    applicationInsights: applicationInsightsId
    containerRegistry: empty(containerRegistryId) ? null : containerRegistryId
    keyVault: keyVaultId
    storageAccount: storageAccountId
    hbiWorkspace: false
    managedNetwork: {
      isolationMode: 'Disabled'
    }
    v1LegacyMode: false
    publicNetworkAccess: publicNetworkAccess
  }

  resource openAiConnection 'connections' = {
    name: openAiConnectionName
    properties: {
      category: 'AzureOpenAI'
      authType: 'AAD'
      isSharedToAll: true
      target: openAi.properties.endpoints['OpenAI Language Model Instance API']
      metadata: {
        ApiVersion: '2024-10-01'
        ApiType: 'azure'
        ResourceId: openAi.id
      }
    }
  }
}

output id string = hub.id
output name string = hub.name
output principalId string = hub.identity.principalId

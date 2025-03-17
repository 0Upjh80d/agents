metadata description = 'Creates an Azure Container Registry'
param name string
param location string = resourceGroup().location
param tags object = {}

param adminUserEnabled bool = false
param anonymousPullEnabled bool = false
param azureADAuthenticationAsArmPolicy object = {
  status: 'enabled'
}
param dataEndpointEnabled bool = false
param encryption object = {
  status: 'disabled'
}
param exportPolicy object = {
  status: 'enabled'
}
param metadataSearch string = 'Disabled'
param networkRuleBypassOptions string = 'AzureServices'
param publicNetworkAccess string = 'Enabled'
param quarantinePolicy object = {
  status: 'disabled'
}
param retentionPolicy object = {
  days: 7
  status: 'disabled'
}
param scopeMaps array = []
param skuName string = 'Basic'

param softDeletePolicy object = {
  retentionDays: 7
  status: 'disabled'
}
param trustPolicy object = {
  type: 'Notary'
  status: 'disabled'
}
param workspaceId string = ''
param zoneRedundancy string = 'Disabled'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2024-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    anonymousPullEnabled: anonymousPullEnabled
    dataEndpointEnabled: dataEndpointEnabled
    encryption: encryption
    metadataSearch: metadataSearch
    networkRuleBypassOptions: networkRuleBypassOptions
    policies: {
      quarantinePolicy: quarantinePolicy
      trustPolicy: trustPolicy
      retentionPolicy: retentionPolicy
      exportPolicy: exportPolicy
      azureADAuthenticationAsArmPolicy: azureADAuthenticationAsArmPolicy
      softDeletePolicy: softDeletePolicy
    }
    publicNetworkAccess: publicNetworkAccess
    zoneRedundancy: zoneRedundancy
  }

  resource scopeMap 'scopeMaps' = [
    for scopeMap in scopeMaps: {
      name: scopeMap.name
      properties: scopeMap.properties
    }
  ]
}

// TODO: Update diagnostics to be its own module
// Blocking issue: https://github.com/Azure/bicep/issues/622
// Unable to pass in a `resource` scope or unable to use string interpolation in resource types
resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(workspaceId)) {
  name: 'registry-diagnostics-settings'
  scope: containerRegistry
  properties: {
    workspaceId: workspaceId
    logs: [
      {
        category: 'ContainerRegistryRepositoryEvents'
        enabled: true
      }
      {
        category: 'ContainerRegistryLoginEvents'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        timeGrain: 'PT1M'
      }
    ]
  }
}

output id string = containerRegistry.id
output name string = containerRegistry.name
output loginServer string = containerRegistry.properties.loginServer

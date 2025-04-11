metadata description = 'Creates an Azure Storage Account'
param name string
param location string = resourceGroup().location
param tags object = {}

@allowed([
  'Premium'
  'Hot'
  'Cool'
])
param accessTier string = 'Hot'
param allowBlobPublicAccess bool = false
param allowCrossTenantReplication bool = true
param allowSharedKeyAccess bool = true
param containers array = []
param corsRules array = []
param defaultToOAuthAuthentication bool = false
param deleteRetentionPolicy object = {}
@allowed(['AzureDnsZone', 'Standard'])
param dnsEndpointType string = 'Standard'
param files array = []
@allowed([
  'Storage'
  'StorageV2'
  'BlobStorage'
  'FileStorage'
  'BlockBlobStorage'
])
param kind string = 'StorageV2'
param minimumTlsVersion string = 'TLS1_2'
param networkAcls object = {
  // New default case that enables the firewall by default
  bypass: 'AzureServices'
  defaultAction: 'Allow'
}
@allowed([
  ''
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'
param queues array = []
param shareDeleteRetentionPolicy object = {}
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
  'Standard_ZRS'
  'Premium_LRS'
  'Premium_ZRS'
  'Standard_GZRS'
  'Standard_RAGZRS'
])
param skuName string = 'Standard_GRS'
param supportsHttpsTrafficOnly bool = true
param tables array = []

resource storageAccount 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  sku: {
    name: skuName
  }
  properties: {
    accessTier: accessTier
    allowBlobPublicAccess: allowBlobPublicAccess
    allowCrossTenantReplication: allowCrossTenantReplication
    allowSharedKeyAccess: allowSharedKeyAccess
    defaultToOAuthAuthentication: defaultToOAuthAuthentication
    dnsEndpointType: dnsEndpointType
    minimumTlsVersion: minimumTlsVersion
    networkAcls: networkAcls
    publicNetworkAccess: publicNetworkAccess
    supportsHttpsTrafficOnly: supportsHttpsTrafficOnly
  }

  resource blobServices 'blobServices' = if (!empty(containers)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      deleteRetentionPolicy: deleteRetentionPolicy
    }

    resource container 'containers' = [
      for container in containers: {
        name: container.name
        properties: {
          publicAccess: container.?publicAccess ?? 'None'
        }
      }
    ]
  }

  resource fileServices 'fileServices' = if (!empty(files)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      shareDeleteRetentionPolicy: shareDeleteRetentionPolicy
    }
  }

  resource queueServices 'queueServices' = if (!empty(queues)) {
    name: 'default'
    properties: {}
    resource queue 'queues' = [
      for queue in queues: {
        name: queue.name
        properties: {
          metadata: {}
        }
      }
    ]
  }

  resource tableServices 'tableServices' = if (!empty(tables)) {
    name: 'default'
    properties: {}
  }
}

output id string = storageAccount.id
output name string = storageAccount.name
output primaryEndpoints object = storageAccount.properties.primaryEndpoints

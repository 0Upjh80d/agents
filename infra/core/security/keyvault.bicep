metadata description = 'Creates an Azure Key Vault'
param name string
param location string = resourceGroup().location
param tags object = {}

param principalId string = ''

resource keyVault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: !empty(principalId)
      ? [
          {
            objectId: principalId
            tenantId: subscription().tenantId
            permissions: {
              secrets: ['get', 'list', 'set']
            }
          }
        ]
      : []
  }
}

output id string = keyVault.id
output name string = keyVault.name
output endpoint string = keyVault.properties.vaultUri

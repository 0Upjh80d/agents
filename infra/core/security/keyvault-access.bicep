metadata description = 'Assigns an Azure Key Vault access policy'
param name string = 'add'

param keyVaultName string
param permissions object = { secrets: ['get', 'list', 'set'] }
param principalId string

resource keyVault 'Microsoft.KeyVault/vaults@2024-12-01-preview' existing = {
  name: keyVaultName
}

resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2024-12-01-preview' = {
  parent: keyVault
  name: name
  properties: {
    accessPolicies: [
      {
        objectId: principalId
        tenantId: subscription().tenantId
        permissions: permissions
      }
    ]
  }
}

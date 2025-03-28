metadata description = 'Assigns an Azure Key Vault access policy'
param name string = 'add'

param keyVaultName string
param permissions object = { secrets: ['get', 'list'] }
param principalId string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
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

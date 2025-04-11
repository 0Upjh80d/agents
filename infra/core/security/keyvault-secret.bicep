metadata description = 'Creates or updates a secret in an Azure Key Vault'
param name string
param tags object = {}

param contentType string = 'string'
param enabled bool = true
param exp int = 0
param keyVaultName string
param nbf int = 0
@secure()
param secretValue string

resource keyVault 'Microsoft.KeyVault/vaults@2024-12-01-preview' existing = {
  name: keyVaultName
}

resource keyVaultSecret 'Microsoft.KeyVault/vaults/secrets@2024-12-01-preview' = {
  parent: keyVault
  name: name
  tags: tags
  properties: {
    attributes: {
      enabled: enabled
      exp: exp
      nbf: nbf
    }
    contentType: contentType
    value: secretValue
  }
}

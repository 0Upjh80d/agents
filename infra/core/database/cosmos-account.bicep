metadata description = 'Creates an Azure Cosmos DB Account'
param name string
param location string = resourceGroup().location
param tags object = {}

@allowed(['GlobalDocumentDB', 'MongoDB', 'Parse'])
param kind string

param reuseCosmosDb bool = false
param existingCosmosDbResourceGroupName string = ''
param existingCosmosDbAccountName string = ''
param deployCosmosDb bool = true

param keyVaultName string = ''
param secretName string

resource existingAccount 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' existing = if (reuseCosmosDb && deployCosmosDb) {
  scope: resourceGroup(existingCosmosDbResourceGroupName)
  name: existingCosmosDbAccountName
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    // See: https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/feature-support-70
    apiProperties: (kind == 'MongoDB') ? { serverVersion: '7.0' } : {}
    capabilities: [
      {
        name: 'EnableMongo'
      }
    ]
  }
}

module keyVaultSecret '../security/keyvault-secret.bicep' = if (!empty(keyVaultName) && !empty(secretName) && deployCosmosDb) {
  name: secretName
  params: {
    name: secretName
    tags: tags
    keyVaultName: keyVaultName
    contentType: 'string'
    enabled: true
    exp: 0
    nbf: 0
    secretValue: reuseCosmosDb
      ? existingAccount.listConnectionStrings().connectionStrings[0].connectionString
      : cosmos.listConnectionStrings().connectionStrings[0].connectionString
  }
}

output name string = !deployCosmosDb ? '' : reuseCosmosDb ? existingAccount.name : cosmos.name

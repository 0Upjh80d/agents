metadata description = 'Creates the database and collection for Mongo DB'
param name string
param location string = resourceGroup().location
param tags object = {}

param databaseName string
param collections array = []

param reuseCosmosDb bool = false
param existingCosmosDbResourceGroupName string = ''
param existingCosmosDbAccountName string = ''
param deployCosmosDb bool = true

param keyVaultName string = ''
param secretName string

module cosmos './cosmos-mongo-account.bicep' = {
  name: 'cosmos-mongo-account'
  params: {
    name: name
    location: location
    tags: tags
    reuseCosmosDb: reuseCosmosDb
    existingCosmosDbResourceGroupName: existingCosmosDbResourceGroupName
    existingCosmosDbAccountName: existingCosmosDbAccountName
    deployCosmosDb: deployCosmosDb
    keyVaultName: keyVaultName
    secretName: secretName
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases@2024-12-01-preview' = {
  name: '${name}/${databaseName}'
  properties: {
    resource: { id: databaseName }
  }

  resource list 'collections' = [
    for collection in collections: {
      name: collection.name
      properties: {
        resource: {
          id: collection.id
          shardKey: { _id: collection.shardKey }
          indexes: [{ key: { keys: [collection.indexKey] } }]
        }
      }
    }
  ]
  dependsOn: [
    cosmos
  ]
}

output databaseName string = databaseName
output collectionNames array = [for collection in collections: collection.id]

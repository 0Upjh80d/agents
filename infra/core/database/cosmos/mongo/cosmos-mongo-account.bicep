metadata description = 'Creates an Azure Cosmos DB Account for Mongo DB'
param name string
param location string = resourceGroup().location
param tags object = {}

param reuseCosmosDb bool = false
param existingCosmosDbResourceGroupName string = ''
param existingCosmosDbAccountName string = ''
param deployCosmosDb bool = true

param keyVaultName string = ''
param secretName string

module cosmos '../../cosmos-account.bicep' = {
  name: 'cosmos-account'
  params: {
    name: name
    location: location
    tags: tags
    kind: 'MongoDB'
    reuseCosmosDb: reuseCosmosDb
    existingCosmosDbResourceGroupName: existingCosmosDbResourceGroupName
    existingCosmosDbAccountName: existingCosmosDbAccountName
    deployCosmosDb: deployCosmosDb
    keyVaultName: keyVaultName
    secretName: secretName
  }
}

output name string = cosmos.name

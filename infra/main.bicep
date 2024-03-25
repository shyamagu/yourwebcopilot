targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param appServicePlanName string = ''
param backendServiceName string = ''
param resourceGroupName string = ''

@description('Use Application Insights for monitoring and performance tracing')
param useApplicationInsights bool = false
param applicationInsightsDashboardName string = ''
param applicationInsightsName string = ''
param logAnalyticsName string = ''

param backendExists bool
@secure()
param backendDefinition object

param bingName string = ''
param bingApiKey string = ''

param openAiServiceName string = ''
param openAiResourceGroupName string = ''
@description('Location for the OpenAI resource group, but you can not use gpt-4-turbo in japaneast.')
@allowed(['canadaeast', 'eastus', 'eastus2', 'francecentral', 'uksouth', 'japaneast', 'australiaeast', 'swedencentral'])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiResourceGroupLocation string  // southcentralus or another region can use gpt-4
param openAiSkuName string = 'S0'
param openAiApiKey string = ''
param openAiApiEndpoint string = ''

param chatGptDeploymentName string = '' // Set in main.parameters.json
param chatGptDeploymentCapacity int = 30
param chatGptModelName string = 'gpt-35-turbo'  // or gpt-4-turbo
param chatGptModelVersion string = '0613'

@description('Id of the user or app to assign application roles')
param principalId string

// Tags that should be applied to all resources.
//
// Note that 'azd-service-name' tags should be applied separately to service host resources.
// Example usage:
//   tags: union(tags, { 'azd-service-name': <service name in azure.yaml> })
var tags = {
  'azd-env-name': environmentName
}

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

resource resourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

module openAi './modules/cognitiveservices.bicep' = {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiServiceName) ? openAiServiceName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openAiResourceGroupLocation
    tags: tags
    sku: {
      name: openAiSkuName
    }
    deployments: [
      {
        name: chatGptDeploymentName
        model: {
          format: 'OpenAI'
          name: chatGptModelName
          version: chatGptModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: chatGptDeploymentCapacity
        }
      }
    ]
  }
}

module bingSearch './modules/bing.bicep' = {
  name: 'bing'
  scope: resourceGroup
  params: {
    name: !empty(bingName) ? bingName : '${abbrs.bingSearch}${resourceToken}'
    location: 'global'
    tags: tags
    kind: 'Bing.Search.v7'
    skuName: 'S1'
  }
}

module monitoring './shared/monitoring.bicep' = if (useApplicationInsights) {
  name: 'monitoring'
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
  }
  scope: resourceGroup
}

module dashboard './shared/dashboard-web.bicep' = if (useApplicationInsights) {
  name: 'dashboard'
  params: {
    name: !empty(applicationInsightsDashboardName) ? applicationInsightsDashboardName : '${abbrs.portalDashboards}${resourceToken}'
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    location: location
    tags: tags
  }
  scope: resourceGroup
}

module appServicePlan './modules/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: resourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'B1'
      capacity: 1
    }
    kind: 'linux'
  }
}

module backend './modules/appservice.bicep' = {
  name: 'web'
  scope: resourceGroup
  params: {
    name: !empty(backendServiceName) ? backendServiceName : '${abbrs.webSitesAppService}yourwebcopilot-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'backend' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.11'
    appCommandLine: 'startup.sh'
    scmDoBuildDuringDeployment: true
    managedIdentity: true
    appSettings: {
      APPLICATIONINSIGHTS_CONNECTION_STRING: useApplicationInsights ? monitoring.outputs.applicationInsightsConnectionString : ''
      BING_API_KEY: !empty(bingApiKey) ? bingApiKey: 'dummy'
      AOAI_API_KEY: !empty(openAiApiKey) ? openAiApiKey: 'dummy'
      AOAI_ENDPOINT: !empty(openAiApiEndpoint) ? openAiApiEndpoint: openAi.outputs.endpoint
      AOAI_MODEL: chatGptDeploymentName
      SCM_DO_BUILD_DURING_DEPLOYMENT: 1
    }
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_CHATGPT_MODEL string = chatGptModelName
output AZURE_OPENAI_SERVICE string = openAi.outputs.name
output AZURE_OPENAI_RESOURCE_GROUP string = openAiResourceGroup.name
output AZURE_OPENAI_CHATGPT_DEPLOYMENT string = chatGptDeploymentName

output BACKEND_URI string = backend.outputs.uri

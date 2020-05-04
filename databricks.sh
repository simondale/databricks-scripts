#!/bin/bash
RESOURCE_GROUP=$1
DATABRICKS_ID=$(az resource list --resource-group $RESOURCE_GROUP --resource-type Microsoft.Databricks/workspaces --query [0].id -otsv)
DATABRICKS_URL="https://"$(az resource list --resource-group $RESOURCE_GROUP --resource-type Microsoft.Databricks/workspaces --query [0].location -otsv)".azuredatabricks.net"
TENANT_ID=$(az account show --query tenantId -otsv)

GLOBAL_DATABRICKS_APPID=2ff814a6-3304-4ab8-85cb-cd0e6f879c1d
AZURE_MANAGEMENT=https://management.azure.com

aztoken=$(az account get-access-token --resource $AZURE_MANAGEMENT --query accessToken -otsv)

az rest --method POST --resource $GLOBAL_DATABRICKS_APPID --uri $DATABRICKS_URL/api/2.0/token/create \
  --headers X-Databricks-Azure-SP-Management-Token="$aztoken" X-Databricks-Azure-Workspace-Resource-Id="$DATABRICKS_ID" \
  --body '{"comment":"CI/CD"}' \
  --query token_value \
  -otsv


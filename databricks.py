from msrestazure.azure_active_directory import AdalAuthentication
from azure.common.client_factory import get_client_from_json_dict
from azure.mgmt.resource import ResourceManagementClient
import argparse
import requests
import json
import adal


def get_client(tenant_id, subscription_id, client_id, client_secret):
    config_dict = {
        'clientId': client_id,
        'clientSecret': client_secret,
        'subscriptionId': subscription_id,
        'tenantId': tenant_id,
        'activeDirectoryEndpointUrl': 'https://login.microsoftonline.com',
        'resourceManagerEndpointUrl': 'https://management.azure.com/',
        'activeDirectoryGraphResourceId': 'https://graph.windows.net/',
        'sqlManagementEndpointUrl': 'https://management.core.windows.net:8443/',
        'galleryEndpointUrl': 'https://gallery.azure.com/',
        'managementEndpointUrl': 'https://management.core.windows.net/'
    }
    client = get_client_from_json_dict(ResourceManagementClient, config_dict)
    return client


def get_access_tokens(tenant_id, client_id, client_secret):
    context = adal.AuthenticationContext(f'https://login.microsoftonline.com/{tenant_id}', validate_authority=True)
    cred1 = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        'https://management.core.windows.net/',
        client_id,
        client_secret)
    cred2 = AdalAuthentication(
        context.acquire_token_with_client_credentials,
        '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d',
        client_id,
        client_secret)
    return \
        cred1.signed_session(None).headers.get(cred1.header).replace('Bearer ', ''), \
        cred2.signed_session(None).headers.get(cred2.header).replace('Bearer ', '')


def main(args):
    client = get_client(args.tenant, args.subscription, args.client_id, args.client_secret)
    databricks_workspaces = client.resources.list_by_resource_group(
        args.resource_group,
        filter=f"resourceType eq 'Microsoft.Databricks/workspaces' and name eq '{args.name}'")

    databricks = list(databricks_workspaces)[0]
    databricks_id = databricks.id
    databricks_location = databricks.location

    management_token, databricks_token = get_access_tokens(args.tenant, args.client_id, args.client_secret)

    db_uri = f'https://{databricks_location}.azuredatabricks.net/api/2.0/token/create'

    headers = {
        'Authorization': f'Bearer {databricks_token}',
        'X-Databricks-Azure-SP-Management-Token': management_token,
        'X-Databricks-Azure-Workspace-Resource-Id': databricks_id
    }

    body = json.dumps({
        'comment': 'CI/CD token'
    })

    response = requests.post(url=db_uri, data=body, headers=headers)
    if args.output.lower() == 'full':
        print(response.json())
    else:
        print(response.json().get('token_value'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenant', help='', type=str)
    parser.add_argument('--subscription', help='', type=str)
    parser.add_argument('--client-id', help='', type=str)
    parser.add_argument('--client-secret', help='', type=str)
    parser.add_argument('--resource-group', help='', type=str)
    parser.add_argument('--name', help='', type=str)
    parser.add_argument('--output', help='', type=str, default='full')
    args = parser.parse_args()
    main(args)

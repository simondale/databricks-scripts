# Databricks Scripts

Create a PAT token using the Azure CLI for the authenticated user (databricks.sh)

Create a PAT token for the specified Service Principal (Client ID & Client Secret) by running the following commands:


```python
python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install -r requirements.txt
python databricks.py \
  --tenant <tenant id> \
  --subscription <subscription id> \
  --client-id <client id> \
  --client-secret <client-secret> \
  --resource-group <resource group> \
  --name <databricks workspace>
```

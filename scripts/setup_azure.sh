#!/usr/bin/env bash
# Provision the Azure resources used as the DVC remote.
# Creates: resource group, storage account (private), blob container,
# and grants YOUR signed-in user the "Storage Blob Data Contributor" role.
#
# Usage: ./scripts/setup_azure.sh            (uses defaults below)
#        RG=my-rg LOC=westeurope ./scripts/setup_azure.sh
set -euo pipefail

# Git Bash on Windows rewrites args starting with "/" (e.g. the /subscriptions/...
# role scope) into Windows paths, which Azure rejects as MissingSubscription.
export MSYS_NO_PATHCONV=1

RG="${RG:-rg-dvc-lab}"
LOC="${LOC:-centralindia}"
SA="${SA:-dvclab$RANDOM$RANDOM}"        # globally unique, lowercase, 3-24 chars
CONTAINER="${CONTAINER:-dvc-data}"

echo "Using subscription: $(az account show --query name -o tsv)"

az group create -n "$RG" -l "$LOC" -o none

az storage account create -n "$SA" -g "$RG" -l "$LOC" \
  --sku Standard_LRS --kind StorageV2 \
  --allow-blob-public-access false \
  --min-tls-version TLS1_2 -o none

# Safety net: recover accidentally deleted or overwritten blobs for 7 days.
az storage account blob-service-properties update \
  --account-name "$SA" -g "$RG" \
  --enable-delete-retention true --delete-retention-days 7 -o none

# Data-plane access: Owner/Contributor roles do NOT grant blob data access.
SCOPE=$(az storage account show -n "$SA" -g "$RG" --query id -o tsv)
USER_ID=$(az ad signed-in-user show --query id -o tsv)
az role assignment create --assignee "$USER_ID" \
  --role "Storage Blob Data Contributor" --scope "$SCOPE" -o none

echo "Waiting 120s for the role assignment to propagate..."
sleep 120

az storage container create --account-name "$SA" -n "$CONTAINER" --auth-mode login -o none

cat <<EOF

Done. Use these values when configuring the DVC remote:
  storage account : $SA
  container       : $CONTAINER
  resource group  : $RG

  dvc remote add -d azremote azure://$CONTAINER/datasets
  dvc remote modify azremote account_name $SA

Cleanup when finished:  az group delete -n $RG --yes --no-wait
EOF

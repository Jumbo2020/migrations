import os
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
PROJECT_ID = os.environ["PROJECT_ID"]
REGIONS = ['us-central1', 'europe-west1', 'asia-east1']

# Restore credentials file if provided as base64
if "GOOGLE_CREDENTIALS_B64" in os.environ:
    with open("service-account.json", "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_B64"]))

def list_gpu_instances():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account.json', scopes=SCOPES
    )
    compute = build('compute', 'v1', credentials=credentials)

    for zone in REGIONS:
        request = compute.instances().aggregatedList(project=PROJECT_ID)
        while request is not None:
            response = request.execute()
            for zone_info in response.get('items', {}).values():
                for instance in zone_info.get('instances', []):
                    gpus = [a for a in instance.get('guestAccelerators', [])]
                    if gpus:
                        print(f"{instance['name']} - {instance['zone']} - GPUs: {gpus}")
            request = compute.instances().aggregatedList_next(
                previous_request=request, previous_response=response)

if __name__ == '__main__':
    try:
        print("🚀 Starting GCP GPU fetch script...")
        list_gpu_instances()
        print("✅ Done.")
    except Exception as e:
        print(f"❌ Error: {e}")

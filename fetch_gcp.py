import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
PROJECT_ID = os.environ["PROJECT_ID"]
REGIONS = ['us-central1', 'europe-west1', 'asia-east1']

# כתיבת קובץ האימות
if "GOOGLE_CREDENTIALS_B64" in os.environ:
    with open("service-account.json", "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_B64"]))

def list_gpu_instances():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account.json', scopes=SCOPES
    )
    compute = build('compute', 'v1', credentials=credentials)

    results = []
    log_lines = []
    print("📡 Fetching GPU-enabled instances...")

    request = compute.instances().aggregatedList(project=PROJECT_ID)
    while request is not None:
        response = request.execute()
        for zone_info in response.get('items', {}).values():
            for instance in zone_info.get('instances', []):
                gpus = instance.get('guestAccelerators', [])
                if gpus:
                    result = {
                        "name": instance["name"],
                        "zone": instance["zone"].split("/")[-1],
                        "machineType": instance["machineType"].split("/")[-1],
                        "status": instance["status"],
                        "gpus": gpus
                    }
                    msg = f"✅ Found GPU VM: {result['name']} in {result['zone']}"
                    print(msg)
                    log_lines.append(msg)
                    results.append(result)
        request = compute.instances().aggregatedList_next(
            previous_request=request, previous_response=response)

    with open("output.json", "w") as out_file:
        json.dump(results, out_file, indent=2)

    with open("output.txt", "w") as log_file:
        log_file.write("\n".join(log_lines) + f"\n📁 Saved {len(results)} GPU instances.\n")

    print(f"📁 Saved {len(results)} GPU instances to output.json")

if __name__ == "__main__":
    try:
        print("🚀 Starting GPU instance scan...")
        list_gpu_instances()
        print("✅ Script completed.")
    except Exception as e:
        print(f"❌ Error: {e}")

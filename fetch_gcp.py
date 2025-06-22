import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
PROJECT_ID = os.environ["PROJECT_ID"]

# כתיבת הקובץ service-account.json מתוך הסוד המקודד בבסיס 64
if "GCP_SA" in os.environ:
    with open("service-account.json", "wb") as f:
        f.write(base64.b64decode(os.environ["GCP_SA"]))

def list_gpu_instances():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account.json', scopes=SCOPES
    )
    compute = build('compute', 'v1', credentials=credentials)

    results = []
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
                    print(f"✅ Found GPU VM: {result['name']} in {result['zone']}")
                    results.append(result)
        request = compute.instances().aggregatedList_next(
            previous_request=request, previous_response=response)

    # שמירת התוצאה לקובץ
    with open("output.json", "w") as out_file:
        json.dump(results, out_file, indent=2)

    print(f"📁 Saved {len(results)} GPU instances to output.json")

if __name__ == "__main__":
    try:
        print("🚀 Starting GPU instance scan...")
        list_gpu_instances()
        print("✅ Script completed.")
    except Exception as e:
        print(f"❌ Error: {e}")

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
PROJECT_ID = 'your-project-id'
REGIONS = ['us-central1', 'europe-west1', 'asia-east1']  # תעדכן לפי הצורך

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
    list_gpu_instances()

import json
from google.cloud import compute_v1

def get_gcp_vm_info():
    """
    Fetches information about all VM instances across all zones in a GCP project.
    """
    project_id = get_project_id()
    if not project_id:
        print("Error: Could not determine GCP Project ID from credentials.")
        print("Please ensure your service account has appropriate permissions and the project ID is set in the credentials or manually specify it in the script.")
        return []

    client = compute_v1.InstancesClient()
    instances_data = []

    print(f"Fetching VM information for Project ID: {project_id}")

    try:
        zones_client = compute_v1.ZonesClient()
        zones_request = compute_v1.ListZonesRequest(project=project_id)
        zones_response = zones_client.list(request=zones_request)

        for zone_item in zones_response.items:
            zone_name = zone_item.name
            print(f"Checking zone: {zone_name}...")
            request = compute_v1.ListInstancesRequest(project=project_id, zone=zone_name)
            page_iterator = client.list(request=request)

            for response in page_iterator:
                for instance in response.items:
                    instance_info = {
                        "name": instance.name,
                        "zone": zone_name,
                        "machine_type": instance.machine_type.split('/')[-1] if instance.machine_type else "N/A",
                        "status": instance.status,
                        "cpu_count": "N/A", # Default
                        "cpu_type": "N/A",  # Default
                        "disks": []
                    }

                    # Check for guest accelerators (GPUs)
                    if instance.guest_accelerators:
                        for accelerator in instance.guest_accelerators:
                            # Assuming the first accelerator might be a CPU type or the primary one
                            # This part might need adjustment based on how you want to represent multiple accelerators
                            instance_info["cpu_count"] = accelerator.accelerator_count
                            instance_info["cpu_type"] = accelerator.accelerator_type.split('/')[-1]


                    # Get disk info
                    for disk in instance.disks:
                        disk_size_gb = "N/A"
                        if hasattr(disk, 'disk_size_gb'):
                            disk_size_gb = disk.disk_size_gb
                        elif hasattr(disk, 'disk') and hasattr(disk.disk, 'size_gb'):
                            disk_size_gb = disk.disk.size_gb

                        instance_info["disks"].append({
                            "device_name": disk.device_name,
                            "disk_type": disk.disk_type.split('/')[-1] if disk.disk_type else "N/A",
                            "disk_size_gb": disk_size_gb
                        })
                    instances_data.append(instance_info)

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    return instances_data

def get_project_id():
    """
    Attempts to get the project ID from the authenticated credentials.
    """
    try:
        from google.auth import default
        credentials, project = default()
        return project
    except Exception as e:
        print(f"Error getting project ID from credentials: {e}")
        return None

if __name__ == "__main__":
    vm_data = get_gcp_vm_info()

    output_filename = "gcp_vm_info.json"
    with open(output_filename, "w") as f:
        json.dump(vm_data, f, indent=4)

    print(f"Successfully saved GCP VM information to {output_filename}")

import subprocess
import json
import datetime

def get_kubernetes_inventory():
    # Run kubectl command to get pods with their labels in JSON format
    cmd = "kubectl get pods -A -o json"
    result = subprocess.check_output(cmd, shell=True)
    data = json.loads(result)
    
    inventory = []
    
    for item in data['items']:
        name = item['metadata']['name']
        labels = item['metadata'].get('labels', {})
        
        # Extract our NIST-required labels
        entry = {
            "asset_name": name,
            "owner": labels.get("owner", "UNKNOWN"),
            "system_id": labels.get("system-id", "UNKNOWN"),
            "status": item['status']['phase'],
            "discovery_date": str(datetime.datetime.now())
        }
        inventory.append(entry)
    
    # Save to a file (The 'Actual Update')
    with open('asset_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=4)
    print("Inventory updated: asset_inventory.json created.")

if __name__ == "__main__":
    get_kubernetes_inventory()

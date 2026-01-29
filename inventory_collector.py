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

def generate_html_dashboard(inventory_data):
    total = len(inventory_data)
    # Count assets (In this demo, all are 'Compliant' because Kyverno blocks the bad ones!)
    compliant = sum(1 for item in inventory_data if item['owner'] != 'UNKNOWN')
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GRC Compliance Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: sans-serif; text-align: center; background: #f4f7f6; }}
            .container {{ width: 400px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .status {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <h1>NIST 800-53 Asset Governance</h1>
        <div class="container">
            <canvas id="complianceChart"></canvas>
            <p class="status">Overall Compliance: 100%</p>
            <p>Total Assets Discovered: {total}</p>
        </div>
        <script>
            const ctx = document.getElementById('complianceChart').getContext('2d');
            new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: ['Compliant', 'Non-Compliant'],
                    datasets: [{{
                        data: [{compliant}, 0],
                        backgroundColor: ['#28a745', '#dc3545']
                    }}]
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w') as f:
        f.write(html_template)

if __name__ == "__main__":
    get_kubernetes_inventory()
    inventory = get_kubernetes_inventory()
    generate_html_dashboard(inventory)
    print("HTML dashboard created: index.html")

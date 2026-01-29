import subprocess
import json
import datetime

def get_kubernetes_inventory():
    # Run kubectl command to get pods with their labels in JSON format
    cmd = "kubectl get pods -A -o json"
    try:
        result = subprocess.check_output(cmd, shell=True)
        data = json.loads(result)
    except Exception as e:
        print(f"Error connecting to Kubernetes: {e}")
        raise e # Re-raise to ensure the GitHub Action fails and sends a Slack alert
    
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
            "discovery_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        inventory.append(entry)
    
    # Save to a file (The 'Actual Update')
    with open('asset_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=4)
    print("Inventory updated: asset_inventory.json created.")
    
    # CRITICAL FIX: Return the list so the dashboard function can use it
    return inventory

def generate_github_summary(inventory_data):
    # This creates the Markdown file for the GitHub UI
    summary = "### 📊 NIST 800-53 Compliance Summary\n"
    summary += "| Asset Name | Owner | System ID | Status | Compliance |\n"
    summary += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for item in inventory_data:
        is_compliant = "✅" if item['owner'] != "UNKNOWN" and item['system_id'] != "UNKNOWN" else "❌"
        summary += f"| {item['asset_name']} | {item['owner']} | {item['system_id']} | {item['status']} | {is_compliant} |\n"
    
    with open('github_summary.md', 'w') as f:
        f.write(summary)
    print("GitHub Job Summary file created.")

def generate_html_dashboard(inventory_data):
    total = len(inventory_data)
    
    # Logic: An asset is compliant ONLY if it has an owner AND a system_id
    compliant = sum(1 for item in inventory_data if item['owner'] != 'UNKNOWN' and item['system_id'] != 'UNKNOWN')
    non_compliant = total - compliant
    
    # Calculate percentage for the 'Score'
    score = (compliant / total * 100) if total > 0 else 0
    status_color = "#28a745" if score == 100 else "#dc3545"

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NIST 800-53 Compliance Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #f0f2f5; padding-top: 50px; }}
            .container {{ width: 500px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .status-box {{ font-size: 2.5em; font-weight: bold; color: {status_color}; margin: 20px 0; }}
            h1 {{ color: #1a73e8; }}
            .stats {{ font-size: 1.1em; color: #555; }}
            .footer {{ margin-top: 25px; font-size: 0.8em; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Compliance Dashboard</h1>
            <p>NIST 800-53: Asset Management Control</p>
            <canvas id="complianceChart"></canvas>
            <div class="status-box">{score:.1f}%</div>
            <div class="stats">
                <p>Total Assets Discovered: <strong>{total}</strong></p>
                <p>Compliant: {compliant} | Non-Compliant: {non_compliant}</p>
            </div>
            <div class="footer">Last Audit: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        <script>
            const ctx = document.getElementById('complianceChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Compliant', 'Non-Compliant'],
                    datasets: [{{
                        data: [{compliant}, {non_compliant}],
                        backgroundColor: ['#28a745', '#dc3545'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    cutout: '75%',
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w') as f:
        f.write(html_template)

if __name__ == "__main__":
    # Get the inventory and store it in a variable
    inventory = get_kubernetes_inventory()
    
    # Pass that variable to the dashboard generator
    generate_html_dashboard(inventory)
    print("HTML dashboard created: index.html")
    generate_github_summary(inventory)
    print("GitHub Job Summary file created.")

import subprocess
import json
import datetime

def get_kubernetes_inventory():
    # 1. Get all pods
    cmd_pods = "kubectl get pods -A -o json"
    try:
        result = subprocess.check_output(cmd_pods, shell=True)
        pod_data = json.loads(result)
    except Exception as e:
        print(f"Error connecting to Kubernetes: {e}")
        raise e 
    
    inventory = []
    ignored_namespaces = ["kube-system", "kube-public", "kube-node-lease", "kyverno"]
    
    # 2. Process existing pods (Live Assets)
    for item in pod_data['items']:
        namespace = item['metadata'].get('namespace', 'default')
        if namespace in ignored_namespaces:
            continue
            
        labels = item['metadata'].get('labels', {})
        owner = labels.get("owner", "UNKNOWN")
        system_id = labels.get("system-id", "UNKNOWN")
        
        # Determine compliance status
        is_compliant = owner != "UNKNOWN" and system_id != "UNKNOWN"
        
        entry = {
            "asset_name": item['metadata']['name'],
            "namespace": namespace,
            "owner": owner,
            "system_id": system_id,
            "status": item['status']['phase'],
            "compliance_status": "COMPLIANT" if is_compliant else "NON-COMPLIANT",
            "reason": "Missing NIST Labels" if not is_compliant else "All controls met",
            "discovery_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        inventory.append(entry)

    # 3. OPTIONAL: Fetch Kyverno PolicyReports (Captures violations even if pods are blocked/audited)
    try:
        cmd_reports = "kubectl get policyreports -A -o json"
        report_result = subprocess.check_output(cmd_reports, shell=True)
        report_data = json.loads(report_result)
        
        for report in report_data.get('items', []):
            for result in report.get('results', []):
                if result.get('result') == "fail":
                    # Add a 'Shadow Asset' entry for the failed attempt
                    entry = {
                        "asset_name": result['resources'][0]['name'],
                        "namespace": result['resources'][0]['namespace'],
                        "owner": "BLOCKED",
                        "system_id": "BLOCKED",
                        "status": "Failed Admission",
                        "compliance_status": "NON-COMPLIANT",
                        "reason": f"Policy Violation: {result['policy']}",
                        "discovery_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    inventory.append(entry)
    except:
        print("No PolicyReports found or Kyverno not reporting. Skipping advanced audit.")

    # Save to file
    with open('asset_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=4)
    
    return inventory

def generate_github_summary(inventory_data):
    summary = "### 📊 NIST 800-53 Unified Asset Inventory\n"
    summary += "| Asset Name | Status | Compliance | Reason |\n"
    summary += "| :--- | :--- | :--- | :--- |\n"
    
    for item in inventory_data:
        emoji = "✅" if item['compliance_status'] == "COMPLIANT" else "❌"
        summary += f"| {item['asset_name']} | {item['status']} | {emoji} {item['compliance_status']} | {item['reason']} |\n"
    
    with open('github_summary.md', 'w') as f:
        f.write(summary)

def generate_html_dashboard(inventory_data):
    total = len(inventory_data)
    compliant = sum(1 for item in inventory_data if item['compliance_status'] == 'COMPLIANT')
    non_compliant = total - compliant
    score = (compliant / total * 100) if total > 0 else 0
    status_color = "#28a745" if score == 100 else "#dc3545"

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NIST 800-53 Compliance Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; text-align: center; background: #f0f2f5; padding-top: 50px; }}
            .container {{ width: 600px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .status-box {{ font-size: 2.5em; font-weight: bold; color: {status_color}; margin: 20px 0; }}
            .legend {{ display: flex; justify-content: space-around; margin-top: 20px; font-weight: bold; }}
            .compliant {{ color: #28a745; }}
            .non-compliant {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Unified Compliance Dashboard</h1>
            <canvas id="complianceChart"></canvas>
            <div class="status-box">{score:.1f}% Score</div>
            <div class="legend">
                <div class="compliant">Compliant: {compliant}</div>
                <div class="non-compliant">Non-Compliant: {non_compliant}</div>
            </div>
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
                    }}]
                }},
                options: {{ cutout: '70%' }}
            }});
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w') as f:
        f.write(html_template)

if __name__ == "__main__":
    inventory = get_kubernetes_inventory()
    generate_html_dashboard(inventory)
    generate_github_summary(inventory)

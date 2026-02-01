# 🛡️ Automated NIST 800-53 Asset Inventory & Remediation

[![Weekly Asset Review](https://github.com/vivekpyadav/Automated_GRC_Asset_Inventory/actions/workflows/compliance-schedule.yml/badge.svg)](https://github.com/vivekpyadav/Automated_GRC_Asset_Inventory/actions/workflows/compliance-schedule.yml)

This project implements an automated **Continuous Monitoring (CA-7)** and **Incident Response (IR-4)** pipeline for Kubernetes clusters. It ensures all cloud assets are accounted for and tagged with mandatory accountability labels (`owner` and `system-id`) as required by **NIST 800-53 (CM-8)**.



## 🚀 Key Features

* **Real-time Asset Discovery**: Automatically scans Kubernetes namespaces to identify pods and services.
* **Compliance Scoring**: Evaluates assets against NIST-standard labeling policies using Kyverno.
* **Human-in-the-Loop (HITL) Remediation**: Provides a manual "Remediate" trigger to authorize the automated removal of non-compliant assets, preventing unintended downtime.
* **Audit Evidence Generation**: Generates version-controlled JSON logs and a live HTML dashboard for auditors.
* **Automated Alerting**: Integrates with Slack to notify security teams of critical control failures.

## 🏗️ Architecture & Workflow

The system operates in a closed-loop governance cycle:

1.  **Policy Engine (Kyverno)**: Watches the cluster for pods missing labels. Set to `Audit` mode to track violations without blocking developer workflows.
2.  **GitHub Action (The Orchestrator)**: Triggers the Python logic on a schedule or via manual dispatch.
3.  **Python Logic**:
    * **Audit Mode**: Discovers assets and generates the compliance report.
    * **Remediate Mode**: Actively deletes non-compliant assets to restore the security baseline.
4.  **Reporting**: Pushes evidence to the `master` branch and hosts the visual dashboard on `gh-pages`.



## 📊 NIST 800-53 Control Mapping

| Control ID | Control Name | Project Implementation |
| :--- | :--- | :--- |
| **CM-8** | Information System Component Inventory | Automated JSON/HTML inventory of all Kubernetes pods. |
| **IA-3** | Device Identification and Authentication | Enforced through mandatory `owner` and `system-id` labels. |
| **CA-7** | Continuous Monitoring | GitHub Actions running on a cron schedule for ongoing audits. |
| **IR-4** | Incident Handling | Automated "Remediation" mode to contain and eradicate non-compliant assets. |
| **AU-2** | Audit Events | Version-controlled Git history documenting discovery and remediation actions. |

## 🛠️ How to Use

### 1. Discovery (Audit Only)
To view the current compliance posture without making changes:
1.  Navigate to the **Actions** tab in this repository.
2.  Select **Weekly Asset Review**.
3.  Click **Run workflow**, choose **audit**, and click the green button.

### 2. Response (Auto-Remediate)
To clean up the cluster and achieve a 100% compliance score:
1.  Click **Run workflow**.
2.  Select **remediate** from the dropdown menu.
3.  The system will delete all non-compliant pods, re-scan the cluster, and update the dashboard to 100%.



## 📈 Dashboard Preview
The live dashboard provides a real-time view of the compliance score and detailed reasons for any "Non-Compliant" status.



## 📝 Project Impact
* **Reduced Manual Toil**: Replaced manual asset tracking with automated discovery.
* **Risk-Informed Response**: Balanced automation with human review to ensure operational stability.
* **Audit Readiness**: Built a project that provides immutable evidence of security controls in action.

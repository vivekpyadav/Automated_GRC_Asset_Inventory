# Automated GRC Asset Inventory (NIST 800-53)

[![Weekly Asset Review](https://github.com/vivekpyadav/Automated_GRC_Asset_Inventory/actions/workflows/compliance-schedule.yml/badge.svg)](https://github.com/vivekpyadav/Automated_GRC_Asset_Inventory/actions/workflows/compliance-schedule.yml)

## Project Overview
This project automates the **Asset Inventory (IA-3)** and **Accountability** controls as defined by **NIST 800-53**. By integrating Kubernetes Admission Controllers (Kyverno) with a Python-based Discovery Engine, this system ensures 100% visibility into running assets.

### Key Features
* **Preventative Control:** Kyverno policy blocks any resource deployment missing accountability labels (`owner`, `system-id`).
* **Continuous Discovery:** Python script running on a self-hosted runner audits the cluster via API.
* **Audit Trail:** Automated Pull Requests create an immutable record of inventory changes.
* **Incident Response:** Real-time Slack alerts for control failures (e.g., runner/cluster downtime).

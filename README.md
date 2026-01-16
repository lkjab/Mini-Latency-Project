🚀 AWS Latency Probing for HFT
Determining the optimal AWS Availability Zone for low-latency Quantitative Trading.

📌 Project Overview
In High-Frequency Trading (HFT), the "race to the top of the book" is won in microseconds. This project is a technical simulation designed to identify which AWS Availability Zone (AZ) provides the lowest latency path to a centralized "Mock Exchange" endpoint.

By deploying parallelized probers across multiple AWS regions and zones, this tool collects, analyzes, and visualizes network round-trip times (RTT) to inform infrastructure placement decisions.

🛠️ Tech Stack
Cloud: AWS (EC2, VPC, Security Groups)

Measurement: nping (Nmap Network Tool)

Data Analysis: Pandas & Plotly

Infrastructure as Code: Terraform (used for standardized deployment)

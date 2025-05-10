# Scalable AWS System for Student Performance Analytics

## Description
A scalable, fault-tolerant platform deployed on AWS for analyzing student performance data through a **Streamlit-based interactive dashboard**. Designed with high availability, auto-scaling, and real-time visualization in mind, this platform provides insights into student performance across various factors such as hours studied, attendance, and parental involvement.

## Overview

This **Scalable AWS System** is a **high-availability platform** deployed on AWS that provides insights into factors influencing student performance. It features a **Streamlit-based dashboard** for interactive data visualization and analysis, leveraging Python's data science stack. The system is designed with scalability, fault tolerance, and ease of use in mind.

## Features

- **AWS Integration**: Deployed on AWS with a custom VPC, EC2 Auto Scaling, and an Application Load Balancer.
- **Data Upload + S3 Fallback**: Upload CSV datasets or load defaults from an S3 bucket.
- **Fault Tolerance**: Ensures high availability with EC2 instances and health monitoring.
- **Scalability**: Automatically scales based on traffic demands.
- **Interactive Dashboard**: Visualize student performance through scatter plots, heatmaps, and histograms.
- **Dynamic Filtering**: Apply adaptive filters for focused data exploration.
- **Performance Categorization**: Classify students into performance tiers based on exam scores.
- **Missing Data Summary**: Automatically detect and visualize missing data in the dashboard.
- **Correlation Insights**: Display top 3 factors most correlated with exam scores.
- **Advanced Visualizations**: Explore relationships between factors using scatter plots, heatmaps, and trendlines.


## Architecture

![AWS Student Analytics System Architecture](images/aws-student-analytics-architecture.png)  
*Fig 1: AWS Student Analytics System Architecture*
*Diagram designed using draw.io*

### Architecture Components:
The system architecture utilizes the following AWS components:

1. **Custom VPC**:
   - VPC CIDR block: `10.0.0.0/16`
   - Public and private subnets for security and isolation.

2. **Application Load Balancer (ALB)**:
   - Name: `StudentAnalyticsLB`
   - Routes HTTP/HTTPS traffic to healthy EC2 instances.
   - Health checks on port `8501`.

3. **Auto Scaling Group (ASG)**:
   - Name: `StudentAnalyticsASG`
   - Maintains 2–4 EC2 instances based on CPU usage.

4. **EC2 Instances**:
   - Name: `StudentAnalyticsInstance`
   - Private subnets, run the Streamlit app, auto-managed.
   - **User Data Script**: Downloads the `app.py` and `StudentPerformanceFactors.csv` dataset from the S3 bucket at instance startup and runs the Streamlit app.

5. **S3 Bucket**:
   - Name: `student-performance-app-files`
   - Stores the app code (`app.py`) and dataset (`StudentPerformanceFactors.csv`).
   - EC2 instances retrieve these files at startup to deploy the application.

6. **Security Groups**:
   - Load Balancer SG: `StudentAnalytics-LB-SG`
   - App SG: `StudentAnalytics-App-SG`

7. **Key Pair**:
   - Name: `studentanalyst_keypair`

8. **IAM Role**:
   - Name: `StudentAnalyticsRole`
   - S3 read access and SSM permissions.


## Application Interface

The interactive Streamlit dashboard allows users to explore student exam performance through a clean, multi-tab layout:

![Student Analytics Dashboard](images/streamlit_dashboard.png)  
*Fig 2: Student Performance Analytics Dashboard Interface – Accessed via Public DNS*

Dashboard components include:

- Data Source Panel: Upload your dataset or use the S3 default.
- Dynamic Sidebar Filters: Up to 3 filters, auto-detected from categorical variables.
- Overview Tab: Data preview, key metrics, and missing value diagnostics.
- Performance Analysis Tab:
  - Score histograms and category pie chart
  - Category-wise bar charts and boxplots
- Factor Impact Tab:
  - Correlation chart with exam score
  - Scatter plots with trendline and category color
  - Top positive/negative factor insights
- Relationship Explorer Tab:
  - Multi-variable scatter plots
  - Correlation matrix heatmap
  - Strong pairwise factor detection and interpretation

## Deployment Process

1. Create VPC and subnets (`10.0.0.0/16`)
2. Configure public subnets for the ALB and private subnets for EC2
3. Create S3 bucket: `student-performance-app-files`
4. Upload app.py and dataset to S3
5. Launch EC2 using a template (`StudentAnalyticsTemplate`) with user data to pull app files and run Streamlit
6. Create ALB (`StudentAnalyticsLB`) and target group (`StudentAnalyticsTargets`) on port 8501
7. Set up Auto Scaling Group (`StudentAnalyticsASG`) for 2–4 instances

## Auto Scaling and High Availability

- Minimum: 2 instances
- Maximum: 4 instances
- Scaling based on 70% CPU threshold
- Health checks via ALB ensure only healthy instances serve traffic

## Exploratory Data Analysis (Jupyter Notebook)

- Summary stats, missing data, and outlier detection
- Histograms, boxplots, scatter plots, and heatmaps
- Feature correlations and pairplots
- Performance distribution visualized with KDE

## How to Run the app Locally

```bash
git clone https://github.com/yourusername/Scalable-AWS-System-for-Student-Performance-Analysis.git
cd Scalable-AWS-System-for-Student-Performance-Analysis
pip install -r requirements.txt
streamlit run app/app.py


4. Open the application in your browser at [http://localhost:8501](http://localhost:8501).


## Accessing the Application

Once the application is deployed, you can access it via the public DNS of your **Application Load Balancer**:

```
http://StudentAnalyticsLB-1743129080.eu-north-1.elb.amazonaws.com
```





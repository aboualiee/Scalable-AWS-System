# Deployment Scripts

This directory contains scripts and configurations used for deploying the Student Analytics System on AWS.

## EC2 Launch Template User Data

The `launch_template_user_data.sh` script is used in the EC2 launch template to configure newly launched instances. This script runs automatically when a new EC2 instance is provisioned by the Auto Scaling Group.

### What the script does:

1. **System Configuration**
   - Sets up error logging to `/var/log/user-data.log`
   - Updates the system packages
   - Installs required dependencies (Python, pip, git, AWS CLI)

2. **Application Setup**
   - Creates application directory structure
   - Downloads application files from S3 with retry logic
   - Sets up a Python virtual environment
   - Installs required Python packages with specific versions

3. **Service Configuration**
   - Creates a systemd service for the Streamlit application
   - Configures the service for automatic restarts and proper logging
   - Sets the Streamlit server to listen on port 8501

4. **Service Management**
   - Enables the service to start on system boot
   - Starts the Streamlit service
   - Verifies the service is running

### Usage

This script is automatically executed by AWS when a new EC2 instance is launched using the `StudentAnalyticsTemplate` launch template. The script relies on the instance having the `StudentAnalyticsRole` IAM role with appropriate S3 access permissions.

### Dependencies

- AWS IAM Role with S3 read access permissions
- S3 bucket `student-performance-app-files` containing:
  - `app.py` (Streamlit application code)
  - `StudentPerformanceFactors.csv` (dataset file)

## SSH Key Pair

For secure SSH access to EC2 instances (when needed for troubleshooting), the project uses a key pair named `studentanalyst_keypair`.

### Important Security Notes:

- The private key file (`.pem`) should **never** be committed to version control
- Store the private key securely on your local machine with restricted permissions (`chmod 400`)
- SSH access is only needed for debugging or advanced configuration
- For routine management, AWS Systems Manager (SSM) is preferred over direct SSH

### SSH Connection Example:

```bash
ssh -i /path/to/studentanalyst_keypair.pem ec2-user@instance-public-ip
```

Note that instances in private subnets are not directly accessible via SSH from the internet. Access would require using a bastion host or AWS Systems Manager Session Manager
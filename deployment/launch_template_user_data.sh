#!/bin/bash
# Enable error logging
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting setup at $(date)"

# Update and install packages
yum update -y
yum install -y python3 python3-pip git awscli

# Create app directory
echo "Creating application directory..."
mkdir -p /app
cd /app

# Download app files with a retry logic
echo "Downloading application files..."
for i in {1..3}; do
  aws s3 cp s3://student-performance-app-files/app.py /app/app.py && break
  echo "Retry $i downloading app.py..."
  sleep 5
done

for i in {1..3}; do
  aws s3 cp s3://student-performance-app-files/StudentPerformanceFactors.csv /app/StudentPerformanceFactors.csv && break
  echo "Retry $i downloading CSV..."
  sleep 5
done

# Create and activate a Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv /app/venv

# Install Python packages with correct versions in the virtual environment
echo "Installing Python packages..."
/app/venv/bin/pip install --upgrade pip
/app/venv/bin/pip install --no-cache-dir streamlit==1.44.1 matplotlib==3.9.4 seaborn==0.13.2 plotly==6.0.1 pandas==2.2.3 boto3 statsmodels

# Create a systemd service with correct path to Python executable
echo "Creating Streamlit service..."
cat > /etc/systemd/system/streamlit.service << 'EOF'
[Unit]
Description=Streamlit Application Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app
ExecStartPre=/bin/sleep 10
ExecStart=/app/venv/bin/streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "Enabling and starting Streamlit service..."
systemctl daemon-reload
systemctl enable streamlit
systemctl start streamlit

# Wait for service to start and verify it's running
echo "Waiting for service to start..."
sleep 30
systemctl status streamlit
echo "Setup completed at $(date)"
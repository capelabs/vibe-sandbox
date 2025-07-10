#!/bin/sh

# 0. Check if tracee is already installed
if command -v tracee-ebpf >/dev/null 2>&1; then
    echo "Tracee is already installed. Exiting."
    exit 0
fi

# 1. Download tracee release and extract it
echo "Downloading tracee release..."
curl -L -o tracee.tar.gz https://github.com/aquasecurity/tracee/releases/download/v0.23.1/tracee-x86_64.v0.23.1.tar.gz

echo "Extracting tracee..."
mkdir -p tracee
tar -xzf tracee.tar.gz -C tracee
rm tracee.tar.gz

# 2. Move tracee to /usr/local/bin
echo "Moving tracee to /usr/local/bin..."
sudo mv tracee/dist/tracee-ebpf-static /usr/local/bin/tracee-ebpf
sudo chmod +x /usr/local/bin/tracee-ebpf

# 3. Create a systemd service for tracee
read -p "Enter the webhook URL for tracee output (e.g., http://localhost:8080): " WEBHOOK_URL

echo "Creating systemd service for tracee..."
sudo tee /etc/systemd/system/tracee.service > /dev/null <<EOF
[Unit]
Description=Tracee eBPF Service
After=network.target

[Service]
ExecStart=/usr/local/bin/tracee-ebpf --output json --output webhook:$WEBHOOK_URL
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 4. Enable and start the tracee service
echo "Enabling and starting the tracee service..."
sudo systemctl enable tracee.service
sudo systemctl start tracee.service

# 5. Verify the service status
echo "Verifying the tracee service status..."
sudo systemctl status tracee.service

if [ $? -ne 0 ]; then
    echo "Tracee service failed to start. Please check the logs."
    exit 1
else 
    echo "Tracee service is running successfully."
fi

# 6. Clean up
echo "Cleaning up..."
rm -rf tracee

echo "Setup completed successfully."
echo "You can now use tracee to monitor system events."
echo "Run 'sudo journalctl -u tracee.service' to view the logs."

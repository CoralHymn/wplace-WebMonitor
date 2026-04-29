# wplace-WebMonitor

A monitoring system for wplace.live pixel canvas - captures real-time color distribution of specified regions, records historical data, and provides a visualization dashboard.


<div align="center">

### [🇺🇸 English](README-EN.md) | [🇨🇳 简体中文](README.md)

</div>

## 📋 Overview

This project is a region monitoring tool for [wplace.live](https://wplace.live) (a collaborative pixel canvas platform similar to r/place). It provides:

- **Real-time Monitoring**: Periodically captures complete screenshots of specified regions
- **Color Analysis**: Calculates the percentage distribution of each color in the monitored area
- **Historical Records**: Maintains multi-dimensional historical data (24h/3d/7d/long-term)
- **Visualization Dashboard**: Web-based interface for real-time viewing and trend analysis
- **Auto-cleanup**: Regularly removes expired screenshots to save storage space

### Use Case Example

Monitor the territory around Qinghai Lake on wplace.live, track color distribution trends, and provide data support for team collaboration.

[青海湖监控](https://qh.wplace.icu)

## ✨ Features

- 🎯 **Precise Region Selection**: Tile-based coordinate system for accurate positioning of any rectangular area
- ⚡ **Efficient Concurrent Downloads**: Async concurrent tile downloads for fast screenshot generation
- 📊 **Multi-dimensional Data Analysis**:
  - Real-time data (last 24 hours, sampled every 5 minutes)
  - Short-term data (last 3 days)
  - Mid-term data (last 7 days)
  - Long-term data (daily noon snapshots, up to 180 days)
- 🌐 **Modern Web Interface**:
  - CRT scanline retro-style display
  - ECharts interactive charts (pie + line graphs)
  - Multiple time range switching
  - Custom date range queries (max 30 days)
  - Legend visibility control (persisted via localStorage)
  - Responsive design
- 🔄 **Automated Operation**: Runs continuously in the background without manual intervention
- 💾 **Lightweight Architecture**: No database required, pure file-based storage

## 🏗️ Project Structure

```
wplace-WebMonitor/
├── capture.py              # Tile downloader and screenshot generator
├── monitor.py              # Main monitoring service (scheduler)
├── config.py               # Configure
├── index.html              # Web visualization dashboard
├── requirements.txt        # Python dependencies
├── README.md               # Chinese documentation
├── README-EN.md            # English documentation
├── captures/               # [Auto-generated] Screenshot storage
│   ├── wplace_capture_20260428_120000.png
│   └── ...
├── data/                   # [Auto-generated] Analysis results
│   ├── realtime_colors.json    # 24-hour real-time data
│   ├── three_days.json         # 3-day data
│   ├── seven_days.json         # 7-day data
│   └── history_colors.json     # Long-term historical data
└── latest.png              # [Auto-generated] Symlink to latest screenshot
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Network access to `backend.wplace.live`
- Sufficient disk space for screenshots (several MB to tens of MB per day, depending on region size)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/coralhymn/wplace-WebMonitor.git
cd wplace-WebMonitor
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `pillow`: Image processing library for tile stitching and color analysis
- `aiohttp`: Async HTTP client for concurrent tile downloads

#### 3. Configure Monitoring Region

Edit `config.py` to modify the tile coordinates of the monitored region:

```python
# Format: (tile_x, tile_y, pixel_offset_x, pixel_offset_y)
LEFT_TILE_X = 1590
LEFT_TILE_Y = 795
LEFT_PX = 800
LEFT_PY = 400

RIGHT_TILE_X = 1593
RIGHT_TILE_Y = 797
RIGHT_PX = 811
RIGHT_PY = 405
```

**How to get tile coordinates:**
1. Open [wplace.live](https://wplace.live)
2. Navigate to the region you want to monitor
3. Get tile coordinates through browser DevTools or URL parameters
4. Fill top-left coordinates into `LEFT_*` variables, bottom-right into `RIGHT_*` variables

#### 4. Start the Monitoring Service

```bash
python monitor.py
```

Once started, the service will:
- Execute the first screenshot immediately
- Capture a screenshot every 2 minutes automatically
- Analyze color distribution every 5 minutes
- Clean up expired screenshots daily at 8 AM

Press `Ctrl+C` to stop the service.

#### 5. Start the Web Server

Start a simple HTTP server in the project root directory:

```bash
python -m http.server 8000
```

Then visit in your browser: `http://localhost:8000/index.html`

**Note**: You can also use Nginx, Apache, or other web servers to host the `index.html` file.

## ⚙️ Configuration Details

All configuration options are centralized in the `config.py` file. Changes take effect after restarting the service.

### Monitoring Region Configuration

```python
# Top-left tile coordinates and pixel offset
LEFT_TILE_X = 1590
LEFT_TILE_Y = 795
LEFT_PX = 800
LEFT_PY = 400

# Bottom-right tile coordinates and pixel offset
RIGHT_TILE_X = 1593
RIGHT_TILE_Y = 797
RIGHT_PX = 811
RIGHT_PY = 405
```

**How to get tile coordinates:**
1. Open [wplace.live](https://wplace.live)
2. Navigate to the region you want to monitor
3. Get tile coordinates through browser DevTools or URL parameters
4. Fill top-left coordinates into `LEFT_*` variables, bottom-right into `RIGHT_*` variables

### Screenshot Frequency Configuration

```python
# Screenshot interval (seconds), default 120s (2 minutes)
CAPTURE_INTERVAL_SEC = 120
```

**Adjustment Recommendations:**
- Lower values increase screenshot frequency but also server load and storage usage
- Recommended minimum: 60 seconds to avoid being banned by the target website
- Higher values reduce resource consumption, suitable for long-term low-power operation

### Color Analysis Frequency Configuration

```python
# Color analysis interval (seconds), default 300s (5 minutes)
ANALYSIS_INTERVAL_SEC = 300
```

**Adjustment Recommendations:**
- Must be greater than or equal to `CAPTURE_INTERVAL_SEC`
- Lower values provide finer-grained color data but increase CPU usage
- Recommended to keep at 300 seconds (5 minutes) for balanced precision and performance

### Auto-Cleanup Configuration

```python
# Enable auto-cleanup of previous day's screenshots (True/False)
AUTO_CLEANUP_ENABLED = True

# Daily cleanup time (hour, 0-23), default 8 AM
CLEANUP_HOUR = 8
```

**Description:**
- `AUTO_CLEANUP_ENABLED`: Set to `False` to disable automatic cleanup
- `CLEANUP_HOUR`: Choose off-peak hours for cleanup to avoid affecting normal monitoring
- Cleanup rule: Delete all screenshots from the previous day at the specified time

### Advanced Configuration

```python
# Tile server URL
TILE_BASE_URL = "https://backend.wplace.live/files/s0/tiles"

# Tile size (pixels)
TILE_SIZE = 1000

# Request headers (simulate browser to avoid bans)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Referer": "https://wplace.live/",
    "Accept": "image/png,image/*,*/*;q=0.8"
}
```

**Adjustment Recommendations:**
- Generally no need to modify `TILE_BASE_URL` and `TILE_SIZE`
- If encountering 403 errors, try changing the `User-Agent` string

### Web Interface Configuration (`index.html`)

```html
<!-- Title and subtitle -->
<h1>Peace Army</h1>
<p>Qinghai Lake Region • LIVE</p>

<!-- Auto-update indicator -->
<span class="text-[10px] opacity-60">Auto-updates every 5 minutes</span>
```

Simply edit the HTML file to modify display text.

## 📊 Data File Formats

### Real-time Data Structure (`data/realtime_colors.json`)

```json
{
  "timestamp": "2026-04-28T12:05:00",
  "total_pixels": 1234567,
  "colors": {
    "#FF0000": {"count": 123456, "percentage": 10.0},
    "#00FF00": {"count": 234567, "percentage": 19.0},
    ...
  }
}
```

### Historical Data Structure (`data/history_colors.json`)

```json
[
  {
    "date": "2026-04-28",
    "time": "12:00:00",
    "colors": {
      "#FF0000": 10.0,
      "#00FF00": 19.0,
      ...
    }
  },
  ...
]
```

## 🌐 Server Deployment

### Option 1: Linux Server Deployment (Recommended)

#### 1. Environment Setup

```bash
# Install Python 3.7+
sudo apt update
sudo apt install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

#### 2. Deploy Application

```bash
# Upload project files to server (e.g., /opt/wplace-monitor)
scp -r wplace-WebMonitor user@server:/opt/wplace-monitor

# Or clone via Git
ssh user@server
cd /opt
git clone https://github.com/coralhymn/wplace-WebMonitor.git wplace-monitor
cd wplace-monitor

# Install dependencies
pip3 install -r requirements.txt
```

#### 3. Configure as systemd Service (Auto-start on Boot)

Create service file `/etc/systemd/system/wplace-monitor.service`:

```ini
[Unit]
Description=wplace.live Region Monitor Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/wplace-monitor
ExecStart=/usr/bin/python3 /opt/wplace-monitor/monitor.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/wplace-monitor/output.log
StandardError=append:/var/log/wplace-monitor/error.log

# Environment variables (optional)
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable wplace-monitor

# Start the service
sudo systemctl start wplace-monitor

# Check service status
sudo systemctl status wplace-monitor

# View logs
sudo journalctl -u wplace-monitor -f
```

#### 4. Configure Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install nginx
```

Create site configuration `/etc/nginx/sites-available/wplace-monitor`:

```nginx
server {
    listen 80;
    server_name monitor.example.com;  # Change to your domain

    root /opt/wplace-monitor;
    index index.html;

    # Cache static files
    location ~* \.(png|jpg|jpeg|gif)$ {
        expires 1m;
        add_header Cache-Control "public, immutable";
    }

    # Don't cache JSON data
    location ~* \.json$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
    }

    # HTML files
    location / {
        try_files $uri $uri/ =404;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/wplace-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Configure HTTPS (Optional, Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Automatically configure SSL certificate
sudo certbot --nginx -d monitor.example.com

# Set up automatic renewal
sudo crontab -e
# Add the following line:
# 0 3 * * * /usr/bin/certbot renew --quiet
```

### Option 2: Windows Server Deployment

#### 1. Install Python

Download and install Python 3.7+ from [Python Official Website](https://www.python.org/downloads/), check "Add to PATH".

#### 2. Deploy Application

```powershell
# Enter project directory
cd C:\wplace-WebMonitor

# Install dependencies
pip install -r requirements.txt
```

#### 3. Create Windows Service Using NSSM

Download [NSSM](https://nssm.cc/download), then:

```powershell
# Install service
nssm install wplace-monitor

# Configure service parameters (in the GUI that appears):
# Path: C:\Python39\python.exe
# Startup directory: C:\wplace-WebMonitor
# Arguments: monitor.py

# Start service
nssm start wplace-monitor
```

#### 4. Host Web Interface with IIS

1. Open IIS Manager
2. Add new website, physical path pointing to project root
3. Configure bindings and ports
4. Ensure IUSR has read permissions on `captures/` and `data/` directories

### Option 3: One-Click Cloud Server Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

# Configuration variables
PROJECT_DIR="/opt/wplace-monitor"
DOMAIN="monitor.example.com"
EMAIL="admin@example.com"

echo "🚀 Starting wplace-WebMonitor deployment..."

# 1. Install dependencies
echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx git

# 2. Clone project
echo "📥 Cloning project..."
sudo git clone https://github.com/coralhymn/wplace-WebMonitor.git $PROJECT_DIR
cd $PROJECT_DIR

# 3. Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo pip3 install -r requirements.txt

# 4. Create systemd service
echo "⚙️ Configuring systemd service..."
sudo tee /etc/systemd/system/wplace-monitor.service > /dev/null <<EOF
[Unit]
Description=wplace.live Region Monitor Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/monitor.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/wplace-monitor/output.log
StandardError=append:/var/log/wplace-monitor/error.log
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable wplace-monitor
sudo systemctl start wplace-monitor

# 5. Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/wplace-monitor > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    root $PROJECT_DIR;
    index index.html;

    location ~* \.(png|jpg|jpeg|gif)$ {
        expires 1m;
        add_header Cache-Control "public, immutable";
    }

    location ~* \.json$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/wplace-monitor /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 6. Configure SSL
echo "🔒 Configuring SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL

echo "✅ Deployment complete!"
echo "📊 Access URL: https://$DOMAIN"
echo "📝 View logs: sudo journalctl -u wplace-monitor -f"
```

Usage:

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Screenshots Are Black or Blank

**Cause**: Incorrect tile coordinates or tile server unreachable

**Solution**:
```bash
# Test tile download
python3 -c "
import asyncio
from capture import download_tile
result = asyncio.run(download_tile(1590, 795))
print('Success' if result else 'Failed')
"
```

#### 2. 403 Forbidden Error

**Cause**: Request rejected by server

**Solution**:
- Check `HEADERS` in `capture.py`, change `User-Agent`
- Increase retry count
- Reduce request frequency

#### 3. Web Interface Cannot Load Data

**Cause**: JSON file permission issues or incorrect paths

**Solution**:
```bash
# Check file permissions
ls -la data/

# Fix permissions
chmod 644 data/*.json
chmod 755 data/

# Check browser console for CORS errors
```

#### 4. High Memory Usage

**Cause**: Too many accumulated screenshots or oversized data files

**Solution**:
```bash
# Manually clean old screenshots
find captures/ -name "*.png" -mtime +1 -delete

# Compress data files
python3 -c "
import json, os
for f in ['realtime_colors.json', 'three_days.json', 'seven_days.json']:
    path = f'data/{f}'
    if os.path.exists(path):
        with open(path) as file:
            data = json.load(file)
        # Keep recent data
        if isinstance(data, list):
            data = data[-100:]
        with open(path, 'w') as file:
            json.dump(data, file)
"
```

#### 5. Service Fails to Restart After Crash

**Solution**:
```bash
# Check systemd logs
sudo journalctl -u wplace-monitor -n 100

# Manual restart
sudo systemctl restart wplace-monitor

# Check Python version
python3 --version
```

### Log Viewing

```bash
# Real-time monitoring service logs
sudo journalctl -u wplace-monitor -f

# View last 100 lines
sudo journalctl -u wplace-monitor -n 100

# View today's logs
sudo journalctl -u wplace-monitor --since today

# View error logs
sudo tail -f /var/log/wplace-monitor/error.log
```

## 📈 Performance Optimization Tips

### 1. Storage Optimization

```bash
# Regularly clean screenshots (keep last 3 days)
0 2 * * * find /opt/wplace-monitor/captures -name "*.png" -mtime +3 -delete

# Compress historical data
0 3 * * 0 python3 /opt/wplace-monitor/compress_data.py
```

### 2. Network Optimization

- Use CDN to accelerate static resources (ECharts, TailwindCSS, etc.)
- Enable Nginx Gzip compression
- Configure browser caching policies

### 3. Monitoring and Alerting

Create health check script `health_check.py`:

```python
#!/usr/bin/env python3
import os
import time
import smtplib
from email.mime.text import MIMEText

def check_health():
    # Check if latest screenshot is outdated
    latest = 'latest.png'
    if not os.path.exists(latest):
        send_alert('Monitoring service异常: Latest screenshot not found')
        return
    
    mtime = os.path.getmtime(latest)
    if time.time() - mtime > 600:  # More than 10 minutes without update
        send_alert('Monitoring service异常: Screenshot update stalled')

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'wplace-monitor Alert'
    msg['From'] = 'alert@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)

if __name__ == '__main__':
    check_health()
```

Configure cron job:

```bash
*/10 * * * * python3 /opt/wplace-monitor/health_check.py
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer

- This project is for educational and research purposes only
- Please comply with the target website's Terms of Service and robots.txt policy
- Set reasonable request frequencies to avoid putting excessive pressure on servers
- Users assume all risks associated with using this software

## 📮 Contact

For questions or suggestions, please submit an [Issue](https://github.com/coralhymn/wplace-WebMonitor/issues)

---

**Happy Monitoring! 🎉**

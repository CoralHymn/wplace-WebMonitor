# wplace-WebMonitor

wplace.live 像素画布区域监控系统 - 实时捕获指定区域的像素颜色分布，记录历史数据并提供可视化查看界面。


<div align="center">

### [🇺🇸 English](README-EN.md) | [🇨🇳 简体中文](README.md)

</div>

## 📋 项目简介

本项目是一个针对 [wplace.live](https://wplace.live)（类似 r/place 的协作像素画布平台）的区域监控工具。它可以：

- **实时监控**：定时捕获指定区域的完整截图
- **颜色分析**：统计区域内各颜色的占比分布
- **历史记录**：保存多时间维度的历史数据（24小时/3天/7天/长期）
- **可视化展示**：提供 Web 仪表板，支持实时查看和趋势分析
- **自动清理**：定期清理过期截图，节省存储空间

### 应用场景示例

监控在青海湖区域的领地变化，追踪颜色分布趋势，为团队协作提供数据支持。

[青海湖监控](https://qh.wplace.icu)

## ✨ 功能特性

- 🎯 **精准区域选择**：基于瓦片坐标系统，可精确定位任意矩形区域
- ⚡ **高效并发下载**：异步并发下载瓦片图片，快速生成完整截图
- 📊 **多维度数据分析**：
  - 实时数据（最近24小时，每5分钟采样）
  - 短期数据（最近3天）
  - 中期数据（最近7天）
  - 长期数据（每日中午12点快照，最多180天）
- 🌐 **现代化 Web 界面**：
  - CRT 扫描线复古风格显示
  - ECharts 交互式图表（饼图 + 折线图）
  - 多时间范围切换
  - 自定义日期范围查询（最大30天）
  - 图例显隐控制（本地存储记忆）
  - 响应式设计
- 🔄 **自动化运行**：后台持续运行，无需人工干预
- 💾 **轻量级架构**：无数据库依赖，纯文件存储

## 🏗️ 项目结构

```
wplace-WebMonitor/
├── capture.py              # 瓦片下载与截图生成模块
├── monitor.py              # 主监控服务（调度器）
├── config.py               # 配置
├── index.html              # Web 可视化仪表板
├── requirements.txt        # Python 依赖列表
├── README.md               # 中文说明文档
├── README-EN.md            # English documentation
├── captures/               # [自动生成] 截图存储目录
│   ├── wplace_capture_20260428_120000.png
│   └── ...
├── data/                   # [自动生成] 数据分析结果目录
│   ├── realtime_colors.json    # 24小时实时数据
│   ├── three_days.json         # 3天数据
│   ├── seven_days.json         # 7天数据
│   └── history_colors.json     # 长期历史数据
└── latest.png              # [自动生成] 最新截图软链接
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 能够访问 `backend.wplace.live` 的网络环境
- 足够的磁盘空间存储截图（根据区域大小，每天约几MB到几十MB）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/coralhymn/wplace-WebMonitor.git
cd wplace-WebMonitor
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

依赖说明：
- `pillow`：图像处理库，用于拼接瓦片和颜色分析
- `aiohttp`：异步 HTTP 客户端，用于并发下载瓦片

#### 3. 配置监控区域

编辑 `config.py` 文件，修改监控区域的瓦片坐标：

```python
# 格式：(瓦片X, 瓦片Y, 像素偏移X, 像素偏移Y)
LEFT_TILE_X = 1590
LEFT_TILE_Y = 795
LEFT_PX = 800
LEFT_PY = 400

RIGHT_TILE_X = 1593
RIGHT_TILE_Y = 797
RIGHT_PX = 811
RIGHT_PY = 405
```

**如何获取瓦片坐标：**
1. 打开 [wplace.live](https://wplace.live)
2. 定位到想要监控的区域
3. 通过浏览器开发者工具或观察 URL 参数获取瓦片坐标
4. 左上角坐标填入 `LEFT_*` 变量，右下角坐标填入 `RIGHT_*` 变量

#### 4. 启动监控服务

```bash
python monitor.py
```

服务启动后会：
- 立即执行首次截图
- 每 2 分钟自动捕获一次截图
- 每 5 分钟分析一次颜色分布
- 每天上午 8 点自动清理过期截图

按 `Ctrl+C` 可停止服务。

#### 5. 启动 Web 服务

在项目根目录下启动一个简单的 HTTP 服务器：

```bash
python -m http.server 8000
```

然后在浏览器中访问：`http://localhost:8000/index.html`

**注意**：也可以使用 Nginx、Apache 或其他 Web 服务器托管 `index.html` 文件。

## ⚙️ 配置项详解

所有配置项已集中到 `config.py` 文件中，修改后重启服务即可生效。

### 监控区域配置

```python
# 左上角瓦片坐标及像素偏移
LEFT_TILE_X = 1590
LEFT_TILE_Y = 795
LEFT_PX = 800
LEFT_PY = 400

# 右下角瓦片坐标及像素偏移
RIGHT_TILE_X = 1593
RIGHT_TILE_Y = 797
RIGHT_PX = 811
RIGHT_PY = 405
```

**如何获取瓦片坐标：**
1. 打开 [wplace.live](https://wplace.live)
2. 定位到想要监控的区域
3. 通过浏览器开发者工具或观察 URL 参数获取瓦片坐标
4. 左上角坐标填入 `LEFT_*` 变量，右下角坐标填入 `RIGHT_*` 变量

### 截图频率配置

```python
# 截图间隔（秒），默认120秒（2分钟）
CAPTURE_INTERVAL_SEC = 120
```

**调整建议：**
- 降低此值可提高截图频率，但会增加服务器负载和存储占用
- 建议不低于 60 秒，避免被目标网站封禁
- 提高此值可减少资源消耗，适合长期低功耗运行

### 颜色分析频率配置

```python
# 颜色分析间隔（秒），默认300秒（5分钟）
ANALYSIS_INTERVAL_SEC = 300
```

**调整建议：**
- 必须大于等于 `CAPTURE_INTERVAL_SEC`
- 降低此值可获得更细粒度的颜色数据，但会增加 CPU 使用率
- 建议保持 300 秒（5分钟）以平衡精度和性能

### 自动清理配置

```python
# 是否启用自动清理前一天的旧截图（True/False）
AUTO_CLEANUP_ENABLED = True

# 每日清理时间（小时，0-23），默认早上8点
CLEANUP_HOUR = 8
```

**说明：**
- `AUTO_CLEANUP_ENABLED`：设置为 `False` 可禁用自动清理功能
- `CLEANUP_HOUR`：选择业务低峰期进行清理，避免影响正常监控
- 清理规则：每天在指定时间删除前一天的所有截图

### 高级配置

```python
# 瓦片服务器地址
TILE_BASE_URL = "https://backend.wplace.live/files/s0/tiles"

# 瓦片尺寸（像素）
TILE_SIZE = 1000

# 请求头（模拟浏览器，避免被封禁）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Referer": "https://wplace.live/",
    "Accept": "image/png,image/*,*/*;q=0.8"
}
```

**调整建议：**
- 一般情况下无需修改 `TILE_BASE_URL` 和 `TILE_SIZE`
- 如遇到 403 错误，可尝试更换 `User-Agent` 字符串

### Web 界面配置（`index.html`）

```html
<!-- 标题和副标题 -->
<h1>和平之师</h1>
<p>青海湖区域• LIVE</p>

<!-- 自动更新提示 -->
<span class="text-[10px] opacity-60">5分钟自动更新</span>
```

直接编辑 HTML 文件即可修改显示文本。

## 📊 数据文件格式

### 实时数据结构（`data/realtime_colors.json`）

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

### 历史数据结构（`data/history_colors.json`）

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

## 🌐 部署到服务器

### 方案一：Linux 服务器部署（推荐）

#### 1. 环境准备

```bash
# 安装 Python 3.7+
sudo apt update
sudo apt install python3 python3-pip

# 验证安装
python3 --version
pip3 --version
```

#### 2. 部署应用

```bash
# 上传项目文件到服务器（例如 /opt/wplace-monitor）
scp -r wplace-WebMonitor user@server:/opt/wplace-monitor

# 或通过 Git 克隆
ssh user@server
cd /opt
git clone https://github.com/coralhymn/wplace-WebMonitor.git wplace-monitor
cd wplace-monitor

# 安装依赖
pip3 install -r requirements.txt
```

#### 3. 配置为 systemd 服务（开机自启）

创建服务文件 `/etc/systemd/system/wplace-monitor.service`：

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

# 环境变量（可选）
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable wplace-monitor

# 启动服务
sudo systemctl start wplace-monitor

# 查看服务状态
sudo systemctl status wplace-monitor

# 查看日志
sudo journalctl -u wplace-monitor -f
```

#### 4. 配置 Nginx 反向代理

安装 Nginx：

```bash
sudo apt install nginx
```

创建站点配置文件 `/etc/nginx/sites-available/wplace-monitor`：

```nginx
server {
    listen 80;
    server_name monitor.example.com;  # 修改为你的域名

    root /opt/wplace-monitor;
    index index.html;

    # 静态文件缓存
    location ~* \.(png|jpg|jpeg|gif)$ {
        expires 1m;
        add_header Cache-Control "public, immutable";
    }

    # JSON 数据不缓存
    location ~* \.json$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
    }

    # HTML 文件
    location / {
        try_files $uri $uri/ =404;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/wplace-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. 配置 HTTPS（可选，推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 自动配置 SSL 证书
sudo certbot --nginx -d monitor.example.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 3 * * * /usr/bin/certbot renew --quiet
```

### 方案二：Windows 服务器部署

#### 1. 安装 Python

从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.7+，勾选 "Add to PATH"。

#### 2. 部署应用

```powershell
# 进入项目目录
cd C:\wplace-WebMonitor

# 安装依赖
pip install -r requirements.txt
```

#### 3. 使用 NSSM 创建 Windows 服务

下载 [NSSM](https://nssm.cc/download)，然后：

```powershell
# 安装服务
nssm install wplace-monitor

# 配置服务参数（在弹出的 GUI 中设置）：
# Path: C:\Python39\python.exe
# Startup directory: C:\wplace-WebMonitor
# Arguments: monitor.py

# 启动服务
nssm start wplace-monitor
```

#### 4. 使用 IIS 托管 Web 界面

1. 打开 IIS 管理器
2. 添加新网站，物理路径指向项目根目录
3. 配置绑定和端口
4. 确保 IUSR 用户对 `captures/` 和 `data/` 目录有读取权限

### 方案三：云服务器一键部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash

# 配置变量
PROJECT_DIR="/opt/wplace-monitor"
DOMAIN="monitor.example.com"
EMAIL="admin@example.com"

echo "🚀 开始部署 wplace-WebMonitor..."

# 1. 安装依赖
echo "📦 安装系统依赖..."
sudo apt update && sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx git

# 2. 克隆项目
echo "📥 克隆项目..."
sudo git clone https://github.com/coralhymn/wplace-WebMonitor.git $PROJECT_DIR
cd $PROJECT_DIR

# 3. 安装 Python 依赖
echo "🐍 安装 Python 依赖..."
sudo pip3 install -r requirements.txt

# 4. 创建 systemd 服务
echo "⚙️ 配置 systemd 服务..."
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

# 5. 配置 Nginx
echo "🌐 配置 Nginx..."
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

# 6. 配置 SSL
echo "🔒 配置 SSL 证书..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL

echo "✅ 部署完成！"
echo "📊 访问地址：https://$DOMAIN"
echo "📝 查看日志：sudo journalctl -u wplace-monitor -f"
```

使用方法：

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

## 🔧 故障排查

### 常见问题

#### 1. 截图全黑或空白

**原因**：瓦片坐标配置错误或瓦片服务器不可达

**解决**：
```bash
# 测试瓦片下载
python3 -c "
import asyncio
from capture import download_tile
result = asyncio.run(download_tile(1590, 795))
print('Success' if result else 'Failed')
"
```

#### 2. 403 Forbidden 错误

**原因**：请求被服务器拒绝

**解决**：
- 检查 `capture.py` 中的 `HEADERS`，更换 `User-Agent`
- 增加重试次数
- 降低请求频率

#### 3. Web 界面无法加载数据

**原因**：JSON 文件权限问题或路径错误

**解决**：
```bash
# 检查文件权限
ls -la data/

# 修复权限
chmod 644 data/*.json
chmod 755 data/

# 检查浏览器控制台是否有 CORS 错误
```

#### 4. 内存占用过高

**原因**：截图积累过多或数据文件过大

**解决**：
```bash
# 手动清理旧截图
find captures/ -name "*.png" -mtime +1 -delete

# 压缩数据文件
python3 -c "
import json, os
for f in ['realtime_colors.json', 'three_days.json', 'seven_days.json']:
    path = f'data/{f}'
    if os.path.exists(path):
        with open(path) as file:
            data = json.load(file)
        # 保留最近的数据
        if isinstance(data, list):
            data = data[-100:]
        with open(path, 'w') as file:
            json.dump(data, file)
"
```

#### 5. 服务崩溃后自动重启失败

**解决**：
```bash
# 检查 systemd 日志
sudo journalctl -u wplace-monitor -n 100

# 手动重启
sudo systemctl restart wplace-monitor

# 检查 Python 版本
python3 --version
```

### 日志查看

```bash
# 实时查看监控服务日志
sudo journalctl -u wplace-monitor -f

# 查看最近 100 行日志
sudo journalctl -u wplace-monitor -n 100

# 查看今天的日志
sudo journalctl -u wplace-monitor --since today

# 查看错误日志
sudo tail -f /var/log/wplace-monitor/error.log
```

## 📈 性能优化建议

### 1. 存储优化

```bash
# 定期清理截图（保留最近 3 天）
0 2 * * * find /opt/wplace-monitor/captures -name "*.png" -mtime +3 -delete

# 压缩历史数据
0 3 * * 0 python3 /opt/wplace-monitor/compress_data.py
```

### 2. 网络优化

- 使用 CDN 加速静态资源（ECharts、TailwindCSS 等）
- 启用 Nginx Gzip 压缩
- 配置浏览器缓存策略

### 3. 监控告警

创建健康检查脚本 `health_check.py`：

```python
#!/usr/bin/env python3
import os
import time
import smtplib
from email.mime.text import MIMEText

def check_health():
    # 检查最新截图是否过时
    latest = 'latest.png'
    if not os.path.exists(latest):
        send_alert('监控服务异常：未找到最新截图')
        return
    
    mtime = os.path.getmtime(latest)
    if time.time() - mtime > 600:  # 超过 10 分钟未更新
        send_alert('监控服务异常：截图更新停滞')

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'wplace-monitor 告警'
    msg['From'] = 'alert@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)

if __name__ == '__main__':
    check_health()
```

配置定时任务：

```bash
*/10 * * * * python3 /opt/wplace-monitor/health_check.py
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

- 本项目仅供学习和研究使用
- 请遵守目标网站的使用条款和 robots.txt 协议
- 合理设置请求频率，避免对服务器造成过大压力
- 使用者需自行承担使用风险

## 📮 联系方式

如有问题或建议，请提交 [Issue](https://github.com/coralhymn/wplace-WebMonitor/issues)

---

**Happy Monitoring! 🎉**

# ==================== wplace-WebMonitor 配置文件 ===================

# ========== 监控区域配置 ==========
# 格式：(瓦片X, 瓦片Y, 像素偏移X, 像素偏移Y)
# Format: (tile_x, tile_y, pixel_offset_x, pixel_offset_y)

# 左上角瓦片坐标及像素偏移
# Top-left tile coordinates and pixel offset
LEFT_TILE_X = 1590
LEFT_TILE_Y = 795
LEFT_PX = 800
LEFT_PY = 400

# 右下角瓦片坐标及像素偏移
# Bottom-right tile coordinates and pixel offset
RIGHT_TILE_X = 1593
RIGHT_TILE_Y = 797
RIGHT_PX = 811
RIGHT_PY = 405

# ========== 截图频率配置 ==========
# 截图间隔（秒），默认120秒（2分钟）
# 建议不低于60秒，避免被目标网站封禁
# Screenshot interval (seconds), default 120s (2 minutes)

CAPTURE_INTERVAL_SEC = 120

# ========== 颜色分析频率配置 ==========
# 颜色分析间隔（秒），默认300秒（5分钟）
# 必须大于等于 CAPTURE_INTERVAL_SEC
# Color analysis interval (seconds), default 300s (5 minutes)
ANALYSIS_INTERVAL_SEC = 300

# ========== 自动清理配置 =========
# 是否启用自动清理前一天的旧截图（True/False）
# Enable auto-cleanup of previous day's screenshots (True/False)
AUTO_CLEANUP_ENABLED = True

# 每日清理时间（小时，0-23），默认早上8点
# Daily cleanup time (hour, 0-23), default 8 AM
CLEANUP_HOUR = 8

# ========== 服务器配置 ==========
# 瓦片服务器地址（请不要随意修改！！！）
# Tile server URL (do not modify randomly!!!)
TILE_BASE_URL = "https://backend.wplace.live/files/s0/tiles"

# 瓦片尺寸（像素）（请不要随意修改！！！）
# Tile size (pixels) (do not modify randomly!!!)
TILE_SIZE = 1000

# ========== 请求头配置 ==========
# 模拟浏览器请求头，防止被服务器识别为脚本而拦截（请不要随意修改！！！）
# Simulate browser request header to prevent server recognition as script and interception (do not modify randomly!!!)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://wplace.live/",
    "Accept": "image/png,image/*,*/*;q=0.8"
}

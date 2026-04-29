import os
import sys
import json
import time
import asyncio
from datetime import datetime, timedelta
import shutil
from collections import defaultdict
from PIL import Image

# 导入配置文件
import config

# 导入截图模块（你的原逻辑，严格保留）
import importlib.util
script_dir = os.path.dirname(os.path.abspath(__file__))
capture_path = os.path.join(script_dir, "capture.py")
spec = importlib.util.spec_from_file_location("capture_module", capture_path)
capture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture_module)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

REALTIME_JSON = os.path.join(DATA_DIR, "realtime_colors.json")   # 实时 + 最近24小时
HISTORY_JSON  = os.path.join(DATA_DIR, "history_colors.json")    # 每日中午记录
THREE_DAYS_JSON = os.path.join(DATA_DIR, "three_days.json")      # 最近72小时
SEVEN_DAYS_JSON = os.path.join(DATA_DIR, "seven_days.json")      # 新增：最近7天

def get_precise_color_stats(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        total_pixels = width * height
        if total_pixels == 0:
            return {}

        pixels = img.getdata()
        color_counts = defaultdict(int)
        for r, g, b in pixels:
            key = f"#{r:02x}{g:02x}{b:02x}"
            color_counts[key] += 1

        stats = {}
        for color, count in color_counts.items():
            stats[color] = round((count / total_pixels) * 100, 4)

        sorted_stats = dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))
        return sorted_stats
    except Exception as e:
        print(f"❌ 颜色分析失败: {e}")
        return {}

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    if "three_days" in filepath or "seven_days" in filepath:
        return {"records": []}
    return {"records": []} if "realtime" in filepath else {"daily_noon": []}

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cleanup_old_images():
    """清理前一天的旧截图（如果启用）"""
    if not config.AUTO_CLEANUP_ENABLED:
        return
    
    now = datetime.now()
    target_date = (now - timedelta(days=1)).date()
    output_dir = capture_module.OUTPUT_DIR
    if not os.path.exists(output_dir):
        return
    deleted_count = 0
    for filename in os.listdir(output_dir):
        if not filename.endswith(".png"):
            continue
        try:
            date_str = filename.replace("wplace_capture_", "").replace(".png", "")[:8]
            file_date = datetime.strptime(date_str, "%Y%m%d").date()
            if file_date == target_date:
                os.remove(os.path.join(output_dir, filename))
                deleted_count += 1
        except:
            continue
    if deleted_count > 0:
        print(f"🧹 已清理 {deleted_count} 张来自 {target_date} 的旧截图")

def update_realtime_json(stats, img_path):
    """实时JSON：记录最近24小时的所有记录（每5分钟一次）"""
    data = load_json(REALTIME_JSON)
    now = datetime.now()
    record = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "stats": stats,
        "image_path": img_path
    }
    data["records"].append(record)
    cutoff = now - timedelta(hours=24)
    data["records"] = [r for r in data["records"] if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") > cutoff]
    save_json(REALTIME_JSON, data)
    print(f"✅ 实时JSON更新完成（当前记录数: {len(data['records'])}）")

def update_three_days_json(stats, img_path):
    """记录最近72小时的所有记录"""
    data = load_json(THREE_DAYS_JSON)
    now = datetime.now()
    record = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "stats": stats,
        "image_path": img_path
    }
    data["records"].append(record)
    cutoff = now - timedelta(hours=72)
    data["records"] = [r for r in data["records"] if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") > cutoff]
    save_json(THREE_DAYS_JSON, data)
    print(f"✅ 三天JSON更新完成（当前记录数: {len(data['records'])}）")

def update_seven_days_json(stats, img_path):
    """新增：记录最近7天（168小时）的所有记录"""
    data = load_json(SEVEN_DAYS_JSON)
    now = datetime.now()
    record = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "stats": stats,
        "image_path": img_path
    }
    data["records"].append(record)
    cutoff = now - timedelta(days=7)
    data["records"] = [r for r in data["records"] if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") > cutoff]
    save_json(SEVEN_DAYS_JSON, data)
    print(f"✅ 七天JSON更新完成（当前记录数: {len(data['records'])}）")

def update_daily_history(stats, img_path):
    """每日历史JSON：只记录每天中午12点（若当天无记录且已过12点，则用最新记录替代）"""
    data = load_json(HISTORY_JSON)
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    has_today = any(r.get("date") == today_str for r in data.get("daily_noon", []))
    should_record = False
    if now.hour == 12 and now.minute < 10:
        should_record = True
    elif now.hour > 12 and not has_today:
        should_record = True
    if should_record:
        record = {
            "date": today_str,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats,
            "image_path": img_path
        }
        data["daily_noon"] = [r for r in data.get("daily_noon", []) if r.get("date") != today_str]
        data.setdefault("daily_noon", []).append(record)
        if len(data["daily_noon"]) > 180:
            data["daily_noon"] = sorted(data["daily_noon"], key=lambda x: x["date"])[-180:]
        save_json(HISTORY_JSON, data)
        print(f"✅ 每日历史JSON更新：{today_str}")

async def main_loop():
    last_analysis_time = 0
    last_cleanup_check_date = None
    print("🔄 wplace 区域监测服务已启动（已启用7天记录）...")
    
    while True:
        now = time.time()
        current_dt = datetime.now()

        print(f"[{current_dt.strftime('%H:%M:%S')}] 正在截取区域...")
        img_path = None
        try:
            img_path = await capture_module.capture_region()
        except Exception as e:
            print(f"❌ 截图出错: {e}")

        if img_path and (now - last_analysis_time >= config.ANALYSIS_INTERVAL_SEC):
            print("📊 正在分析颜色占比...")
            stats = get_precise_color_stats(img_path)
            
            update_realtime_json(stats, img_path)
            update_daily_history(stats, img_path)
            update_three_days_json(stats, img_path)
            update_seven_days_json(stats, img_path)   # ← 新增7天
            
            if img_path and os.path.exists(img_path):
                try:
                    shutil.copy2(img_path, os.path.join(SCRIPT_DIR, "latest.png"))
                    print("✅ 已更新 latest.png")
                except Exception as e:
                    print(f"⚠️ 复制 latest.png 失败: {e}")
            
            last_analysis_time = now
            print("✅ 数据分析与JSON更新完成")

        if config.AUTO_CLEANUP_ENABLED and current_dt.hour == config.CLEANUP_HOUR and last_cleanup_check_date != current_dt.date():
            print("⏰ 执行每日清理任务...")
            cleanup_old_images()
            last_cleanup_check_date = current_dt.date()

        await asyncio.sleep(config.CAPTURE_INTERVAL_SEC)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n🛑 监控服务已停止。")
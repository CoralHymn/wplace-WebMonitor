import asyncio
import aiohttp
import io
import os
from datetime import datetime
from PIL import Image

# 导入配置文件
import config

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "captures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_tile(session, tile_x, tile_y, retries=3):
    """
    下载单个瓦片，带重试机制以解决网络波动或服务器临时拒绝问题
    """
    url = f"{config.TILE_BASE_URL}/{tile_x}/{tile_y}.png"

    # 使用配置文件中的请求头
    headers = config.HEADERS

    for attempt in range(retries):
        try:
            async with session.get(url, timeout=15, headers=headers) as resp:
                if resp.status != 200:
                    # 如果是404，通常意味着该区域未绘制，直接返回None，不重试
                    if resp.status == 404:
                        return None
                    # 其他错误（如503, 429）等待后重试
                    if attempt < retries - 1:
                        wait_time = 2 * (attempt + 1)
                        print(f"  [重试 {attempt+1}/{retries}] 状态码 {resp.status}，{wait_time}秒后重试...")
                        await asyncio.sleep(wait_time)
                        continue
                    print(f"  ❌ 最终下载失败: {resp.status} @ Tile({tile_x},{tile_y})")
                    return None
                
                data = await resp.read()
                # 简单的完整性检查，避免下载到一个空的或错误的文件
                if len(data) < 50: 
                    if attempt < retries - 1:
                        await asyncio.sleep(2)
                        continue
                    return None

                return Image.open(io.BytesIO(data)).convert("RGBA")
                
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2)
                continue
            print(f"  ❌ 下载异常: {e} @ Tile({tile_x},{tile_y})")
            return None
    return None

async def capture_region():
    start_tx = min(config.LEFT_TILE_X, config.RIGHT_TILE_X)
    end_tx   = max(config.LEFT_TILE_X, config.RIGHT_TILE_X)
    start_ty = min(config.LEFT_TILE_Y, config.RIGHT_TILE_Y)
    end_ty   = max(config.LEFT_TILE_Y, config.RIGHT_TILE_Y)

    # 计算最终画布尺寸
    width  = (end_tx - start_tx) * config.TILE_SIZE + (config.RIGHT_PX - config.LEFT_PX + 1)
    height = (end_ty - start_ty) * config.TILE_SIZE + (config.RIGHT_PY - config.LEFT_PY + 1)

    # 创建透明背景画布
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    print(f"📸 开始截取区域: Tile({start_tx},{start_ty}) 至 ({end_tx},{end_ty})")
    
    async with aiohttp.ClientSession() as session:
        # 构建所有下载任务
        tasks = []
        for ty in range(start_ty, end_ty + 1):
            for tx in range(start_tx, end_tx + 1):
                tasks.append(fetch_tile(session, tx, ty))
        
        # 并发下载所有瓦片
        tiles = await asyncio.gather(*tasks)

        # 处理每个瓦片并拼贴
        index = 0
        for ty in range(start_ty, end_ty + 1):
            for tx in range(start_tx, end_tx + 1):
                tile_img = tiles[index]
                index += 1

                if tile_img is None:
                    continue

                # === 计算裁剪区域 (Source) 和 粘贴位置 (Dest) ===
                sx, sy = 0, 0
                sw, sh = config.TILE_SIZE, config.TILE_SIZE
                
                # 初始粘贴坐标
                dx = (tx - start_tx) * config.TILE_SIZE - config.LEFT_PX
                dy = (ty - start_ty) * config.TILE_SIZE - config.LEFT_PY
                
                dw, dh = config.TILE_SIZE, config.TILE_SIZE

                # 1. 处理左边界 (Left Edge)
                if tx == config.LEFT_TILE_X:
                    sx = config.LEFT_PX
                    sw = config.TILE_SIZE - config.LEFT_PX
                    dx = 0
                    dw = sw
                
                # 2. 处理上边界 (Top Edge)
                if ty == config.LEFT_TILE_Y:
                    sy = config.LEFT_PY
                    sh = config.TILE_SIZE - config.LEFT_PY
                    dy = 0
                    dh = sh

                # 3. 处理右边界 (Right Edge)
                if tx == config.RIGHT_TILE_X:
                    relative_left = (tx - start_tx) * config.TILE_SIZE - config.LEFT_PX
                    relative_right_limit = (config.RIGHT_TILE_X - start_tx) * config.TILE_SIZE - config.LEFT_PX + config.RIGHT_PX + 1
                    
                    max_sw = relative_right_limit - relative_left
                    if max_sw < sw:
                        sw = max_sw
                        dw = sw

                # 4. 处理下边界 (Bottom Edge)
                if ty == config.RIGHT_TILE_Y:
                    relative_top = (ty - start_ty) * config.TILE_SIZE - config.LEFT_PY
                    relative_bottom_limit = (config.RIGHT_TILE_Y - start_ty) * config.TILE_SIZE - config.LEFT_PY + config.RIGHT_PY + 1
                    
                    max_sh = relative_bottom_limit - relative_top
                    if max_sh < sh:
                        sh = max_sh
                        dh = sh

                # 安全检查
                if sw <= 0 or sh <= 0 or dw <= 0 or dh <= 0:
                    continue

                try:
                    cropped = tile_img.crop((sx, sy, sx + sw, sy + sh))
                    canvas.paste(cropped, (dx, dy))
                except Exception as e:
                    print(f"  ⚠️ 拼贴错误: {e}")

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wplace_capture_{timestamp}.png"
    save_path = os.path.join(OUTPUT_DIR, filename)
    
    # 确保以 PNG 格式保存，无损
    canvas.save(save_path, "PNG")
    
    print(f"✅ 截图完成！尺寸: {width} × {height}")
    print(f"💾 保存至: {save_path}")
    return save_path

if __name__ == "__main__":
    print("🚀 Wplace 截图工具启动")
    print(f"📍 左上: Tile({config.LEFT_TILE_X},{config.LEFT_TILE_Y}) Pixel({config.LEFT_PX},{config.LEFT_PY})")
    print(f"📍 右下: Tile({config.RIGHT_TILE_X},{config.RIGHT_TILE_Y}) Pixel({config.RIGHT_PX},{config.RIGHT_PY})")
    asyncio.run(capture_region())
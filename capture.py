import asyncio
import aiohttp
import io
import os
from datetime import datetime
from PIL import Image

# ==================== 配置区 ===================
# 左上角瓦片坐标及像素偏移
LEFT_TILE_X, LEFT_TILE_Y, LEFT_PX, LEFT_PY = 1590, 795, 800, 400
# 右下角瓦片坐标及像素偏移
RIGHT_TILE_X, RIGHT_TILE_Y, RIGHT_PX, RIGHT_PY = 1593, 797, 811, 405

import os

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "captures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TILE_BASE_URL = "https://backend.wplace.live/files/s0/tiles"
TILE_SIZE = 1000
# ==============================================

async def fetch_tile(session, tile_x, tile_y, retries=3):
    """
    下载单个瓦片，带重试机制以解决网络波动或服务器临时拒绝问题
    """
    url = f"{TILE_BASE_URL}/{tile_x}/{tile_y}.png"
    
    # 模拟浏览器请求头，防止被服务器识别为脚本而拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://wplace.live/",
        "Accept": "image/png,image/*,*/*;q=0.8"
    }

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
    start_tx = min(LEFT_TILE_X, RIGHT_TILE_X)
    end_tx   = max(LEFT_TILE_X, RIGHT_TILE_X)
    start_ty = min(LEFT_TILE_Y, RIGHT_TILE_Y)
    end_ty   = max(LEFT_TILE_Y, RIGHT_TILE_Y)

    # 计算最终画布尺寸
    width  = (end_tx - start_tx) * TILE_SIZE + (RIGHT_PX - LEFT_PX + 1)
    height = (end_ty - start_ty) * TILE_SIZE + (RIGHT_PY - LEFT_PY + 1)

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
                sw, sh = TILE_SIZE, TILE_SIZE
                
                # 初始粘贴坐标
                dx = (tx - start_tx) * TILE_SIZE - LEFT_PX
                dy = (ty - start_ty) * TILE_SIZE - LEFT_PY
                
                dw, dh = TILE_SIZE, TILE_SIZE

                # 1. 处理左边界 (Left Edge)
                if tx == LEFT_TILE_X:
                    sx = LEFT_PX
                    sw = TILE_SIZE - LEFT_PX
                    dx = 0
                    dw = sw
                
                # 2. 处理上边界 (Top Edge)
                if ty == LEFT_TILE_Y:
                    sy = LEFT_PY
                    sh = TILE_SIZE - LEFT_PY
                    dy = 0
                    dh = sh

                # 3. 处理右边界 (Right Edge)
                if tx == RIGHT_TILE_X:
                    # 目标宽度不能超过 RIGHT_PX 相对于该瓦片起始的位置
                    # 注意：RIGHT_PX 是全局像素坐标，sx 是该瓦片内的起始偏移
                    # 我们需要保留从 sx 到 (RIGHT_PX - (tx * TILE_SIZE - start_tx * TILE_SIZE + LEFT_PX)) ? 
                    # 更简单的逻辑：右侧截断点
                    target_right_edge = RIGHT_PX + 1
                    # 当前瓦片在全局X轴上的起始位置
                    global_tile_x_start = (tx - start_tx) * TILE_SIZE + LEFT_PX # 这里的逻辑有点绕，用相对坐标更简单
                    
                    # 让我们用相对坐标逻辑：
                    # 在该瓦片内，我们最多只能取到 RIGHT_PX 对应的位置
                    # 但该瓦片的 dx 已经计算好了。
                    # 如果 dx + dw > 目标总宽度，则截断
                    # 目标总宽度 = width
                    # 其实上面的 Left/Top 逻辑已经处理了起始点。
                    # 对于 Right/Bottom，我们限制 sw/sh
                    
                    # 重新计算右边界截断：
                    # 该瓦片右侧在全局坐标系中的位置应该是: dx + TILE_SIZE
                    # 我们希望它不超过: (RIGHT_TILE_X - start_tx) * TILE_SIZE + (RIGHT_PX + 1) - LEFT_PX ?
                    # 不，最简单的做法是：
                    # 如果这是最右边的瓦片，sw = RIGHT_PX - (该瓦片左侧在全局的相对位置) + 1
                    
                    # 该瓦片左侧在全局相对位置 (相对于画布左边0点):
                    relative_left = (tx - start_tx) * TILE_SIZE - LEFT_PX
                    # 我们希望截取的右边界是:
                    relative_right_limit = (RIGHT_TILE_X - start_tx) * TILE_SIZE - LEFT_PX + RIGHT_PX + 1
                    
                    max_sw = relative_right_limit - relative_left
                    if max_sw < sw:
                        sw = max_sw
                        dw = sw

                # 4. 处理下边界 (Bottom Edge)
                if ty == RIGHT_TILE_Y:
                    relative_top = (ty - start_ty) * TILE_SIZE - LEFT_PY
                    relative_bottom_limit = (RIGHT_TILE_Y - start_ty) * TILE_SIZE - LEFT_PY + RIGHT_PY + 1
                    
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
    print(f"📍 左上: Tile({LEFT_TILE_X},{LEFT_TILE_Y}) Pixel({LEFT_PX},{LEFT_PY})")
    print(f"📍 右下: Tile({RIGHT_TILE_X},{RIGHT_TILE_Y}) Pixel({RIGHT_PX},{RIGHT_PY})")
    asyncio.run(capture_region())
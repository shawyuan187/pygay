######################載入套件######################
import pygame  # 載入 pygame 套件，用於遊戲開發
import sys  # 載入 sys 套件，用於系統相關操作
import random  # 載入 random 套件，用於隨機生成平台
import os  # 載入 os 套件，用於處理檔案路徑


######################全域變數######################
# 設定執行路徑為目前檔案位置
os.chdir(sys.path[0])
score = 0  # 紀錄當前分數
highest_score = 0  # 紀錄最高分數
game_over = False  # 紀錄遊戲是否結束
initial_player_y = 0  # 紀錄玩家的初始高度，用於計算分數
spring_chance = 0.2  # 彈簧生成機率 20%
special_platform_chance = 0.2  # 特殊平台生成機率 20%（只在分數超過100時生效）
springs = []  # 存放所有彈簧的列表


######################函式定義######################
def load_doodle_sprites():
    """
    載入遊戲所需的圖片資源\n
    - 從source圖片切割各種平台和彈簧精靈\n
    - 載入玩家角色四個方向的圖片\n
    return: 包含所有精靈的字典\n
    """
    # 載入主要圖片資源
    img_path = os.path.join("pic", "src.png")  # image/src.png
    source_image = pygame.image.load(
        img_path
    ).convert_alpha()  # 載入圖片並轉換為帶Alpha通道的格式

    # 定義精靈在原始圖片中的座標和尺寸
    sprite_data = {
        # 各種平台的座標和尺寸 (x, y, 寬, 高)
        "std_platform": (0, 0, 116, 30),  # 標準平台
        "break_platform": (0, 145, 124, 33),  # 可破壞平台
        # 彈簧
        "spring_normal": (376, 188, 71, 35),  # 普通彈簧
        # 玩家角色圖片路徑
        "player_left_jumping": os.path.join("pic", "l.png"),  # 左跳躍
        "player_left_falling": os.path.join("pic", "ls.png"),  # 左下落
        "player_right_jumping": os.path.join("pic", "r.png"),  # 右跳躍
        "player_right_falling": os.path.join("pic", "rs.png"),  # 右下落
    }  # 切割精靈圖片並存入字典
    sprites = {}
    for name, data in sprite_data.items():
        if name.startswith("player_"):
            # 直接從檔案載入玩家角色圖片
            try:
                sprites[name] = pygame.image.load(data).convert_alpha()
            except Exception as e:
                print(f"無法載入玩家圖片 {name}: {e}")
        else:
            try:
                # 從主圖片切割出所需的精靈
                x, y, width, height = data  # 這裡正確解包四個值
                sprites[name] = source_image.subsurface(
                    pygame.Rect(x, y, width, height)
                )
            except ValueError as e:
                print(f"無法切割 {name}: {e}")  # 如果切割失敗，輸出錯誤訊息

    return sprites  # 返回包含所有精靈的字典


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height, color, sprites=None):
        """
        初始化主角\n
        x, y: 主角的左上角座標\n
        width, height: 主角的寬度和高度\n
        color: 主角的顏色 (RGB格式)\n
        sprites: 包含玩家精靈的字典，如果為None則使用矩形繪製\n
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立主角的矩形區域
        self.color = color
        self.speed = 5  # 設定主角的水平移動速度
        self.velocity_y = 0  # 垂直速度
        self.jump_power = -12  # 跳躍初始力量（負值表示向上）
        self.gravity = 0.5  # 重力加速度
        self.on_platform = False  # 是否站在平台上
        self.sprites = sprites  # 保存精靈字典
        self.facing_right = True  # 角色面向方向，預設向右
        self.jumping = True  # 跳躍狀態，預設為跳躍中

    def draw(self, display_area):
        """
        繪製主角\n
        display_area: 繪製主角的目標視窗\n
        """
        if self.sprites:  # 如果有載入精靈圖片
            # 根據角色當前狀態選擇適合的精靈圖片
            direction = "right" if self.facing_right else "left"
            state = "jumping" if self.jumping else "falling"
            sprite_key = f"player_{direction}_{state}"

            # 確認該精靈存在
            if sprite_key in self.sprites:  # 計算圖片位置，確保角色中心點對齊
                sprite = self.sprites[sprite_key]
                # 調整精靈大小為角色的實際尺寸
                sprite = pygame.transform.scale(
                    sprite, (self.rect.width, self.rect.height)
                )
                sprite_rect = sprite.get_rect(center=self.rect.center)
                # 繪製精靈
                display_area.blit(sprite, sprite_rect)
            else:
                # 如果找不到對應的精靈，使用矩形繪製
                pygame.draw.rect(display_area, self.color, self.rect)
        else:
            # 如果沒有載入精靈，使用矩形繪製
            pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        移動主角並處理穿牆效果\n
        direction: 移動方向 (1為右移, -1為左移)\n
        bg_x: 遊戲視窗寬度，用於計算穿牆位置\n
        """
        # 根據方向和速度移動主角
        self.rect.x += direction * self.speed

        # 更新角色面向方向
        if direction > 0:
            self.facing_right = True  # 向右移動時面向右
        elif direction < 0:
            self.facing_right = False  # 向左移動時面向左

        # 穿牆功能處理
        if self.rect.right < 0:  # 當主角完全移出左邊界時
            self.rect.left = bg_x  # 從右側重新出現
        elif self.rect.left > bg_x:  # 當主角完全移出右邊界時
            self.rect.right = 0  # 從左側重新出現

    def apply_gravity(self):
        """
        應用重力效果\n
        更新垂直速度和位置\n
        """
        self.velocity_y += self.gravity  # 加入重力加速度
        self.rect.y += self.velocity_y  # 更新垂直位置

        # 根據垂直速度更新跳躍/下落狀態
        self.jumping = self.velocity_y < 0  # 垂直速度小於0表示上升（跳躍中）

    def check_spring_collision(self, springs):
        """
        檢查與所有彈簧的碰撞\n
        springs: 要檢查碰撞的彈簧物件列表\n
        return: 是否碰到彈簧\n
        """
        # 只在玩家往下掉的時候檢查碰撞
        if self.velocity_y > 0:
            # 計算檢測點數量，根據垂直速度決定檢測點的數量
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points

            for spring in springs:
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y

                    # 檢查是否與彈簧發生碰撞
                    if (
                        test_rect.bottom >= spring.rect.top
                        and test_rect.bottom <= spring.rect.bottom
                        and test_rect.right >= spring.rect.left
                        and test_rect.left <= spring.rect.right
                    ):
                        self.rect.bottom = spring.rect.top  # 將玩家放在彈簧上
                        self.velocity_y = (
                            self.jump_power * 2
                        )  # 給予更強的向上跳躍力（兩倍跳躍力）

                        # 播放彈簧音效
                        if use_sounds and "spring" in sounds:
                            sounds["spring"].play()
                        return True
        return False

    def check_platform_collision(self, platforms):
        """
        檢查與所有平台的碰撞\n
        platforms: 要檢查碰撞的平台物件列表\n
        """
        # 只在玩家往下掉的時候檢查碰撞
        if self.velocity_y > 0:
            # 計算檢測點數量，根據垂直速度決定檢測點的數量
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points

            for platform in platforms:
                if platform.is_special and platform.is_touched:
                    continue  # 如果是特殊平台且已被踩過，跳過檢查

                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y

                    # 檢查是否與平台發生碰撞
                    if (
                        test_rect.bottom >= platform.rect.top
                        and test_rect.bottom <= platform.rect.bottom
                        and test_rect.right >= platform.rect.left
                        and test_rect.left <= platform.rect.right
                    ):

                        # 在與平台碰撞時，標記特殊平台為已被踩過
                        if platform.is_special:
                            platform.is_touched = (
                                True  # 標記特殊平台已被踩過，之後會消失
                            )

                        self.rect.bottom = platform.rect.top  # 將玩家放在平台上
                        self.velocity_y = self.jump_power  # 給予向上的力量
                        self.on_platform = True

                        # 播放跳躍音效
                        if use_sounds and "jump" in sounds:
                            sounds["jump"].play()
                        return True
        return False


class Platform:
    def __init__(self, x, y, width, height, color, is_special=False, sprites=None):
        """
        初始化平台\n
        x, y: 平台的左上角座標\n
        width, height: 平台的寬度和高度\n
        color: 平台的顏色 (RGB格式)\n
        is_special: 是否為特殊平台（只能踩一次的平台）\n
        sprites: 包含平台精靈的字典，如果為None則使用矩形繪製\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_special = is_special  # 標記是否為特殊平台
        self.is_touched = False  # 記錄特殊平台是否被踩過
        self.sprites = sprites  # 保存精靈字典

    def draw(self, display_area):
        """
        繪製平台\n
        display_area: 繪製平台的目標視窗\n
        """
        # 如果是特殊平台且已被踩過，就不繪製
        if self.is_special and self.is_touched:
            return

        if self.sprites:  # 如果有載入精靈圖片
            # 根據平台類型選擇適合的精靈圖片
            sprite_key = "break_platform" if self.is_special else "std_platform"

            # 確認該精靈存在
            if sprite_key in self.sprites:
                # 調整精靈大小以符合平台尺寸
                sprite = pygame.transform.scale(
                    self.sprites[sprite_key], (self.rect.width, self.rect.height)
                )
                # 繪製精靈
                display_area.blit(sprite, self.rect)
            else:
                # 如果找不到對應的精靈，使用矩形繪製
                pygame.draw.rect(display_area, self.color, self.rect)
        else:
            # 如果沒有載入精靈，使用矩形繪製
            pygame.draw.rect(display_area, self.color, self.rect)


class Spring:
    def __init__(self, x, y, width, height, color, sprites=None):
        """
        初始化彈簧道具\n
        x, y: 彈簧的左上角座標\n
        width, height: 彈簧的寬度和高度\n
        color: 彈簧的顏色 (RGB格式)\n
        sprites: 包含彈簧精靈的字典，如果為None則使用矩形繪製\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.sprites = sprites  # 保存精靈字典

    def draw(self, display_area):
        """
        繪製彈簧\n
        display_area: 繪製彈簧的目標視窗\n
        """
        if self.sprites and "spring_normal" in self.sprites:
            # 載入彈簧圖片並調整至適當大小
            sprite = pygame.transform.scale(
                self.sprites["spring_normal"], (self.rect.width, self.rect.height)
            )
            display_area.blit(sprite, self.rect)
        else:
            # 如果沒有載入精靈或找不到彈簧圖片，使用矩形繪製
            pygame.draw.rect(display_area, self.color, self.rect)

    def move_with_platform(self, dy):
        """
        跟隨平台移動\n
        dy: 垂直移動的距離\n
        """
        self.rect.y += dy


######################初始化設定######################
pygame.init()  # 初始化 pygame

# 音效初始化與載入（只保留 jump.mp3 和 spring.mp3）
use_sounds = False
sounds = {}
try:
    pygame.mixer.init()
    sounds["jump"] = pygame.mixer.Sound(os.path.join("sounds", "jump.mp3"))
    sounds["spring"] = pygame.mixer.Sound(os.path.join("sounds", "spring.mp3"))
    for s in sounds.values():
        s.set_volume(0.5)
    use_sounds = True
    print("音效載入成功")
except Exception as e:
    print(f"音效載入失敗: {e}")
    use_sounds = False

FPS = pygame.time.Clock()  # 創建時鐘物件，用於控制遊戲更新速率

######################遊戲視窗設定######################
bg_x = 400  # 設定視窗寬度
bg_y = 600  # 設定視窗高度
bg_size = (bg_x, bg_y)  # 視窗尺寸元組
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 創建遊戲視窗

######################載入圖片######################
try:
    # 載入遊戲所需的所有精靈圖片（需要在設置視窗模式後進行）
    sprites = load_doodle_sprites()
    use_sprites = True  # 標記是否使用精靈圖片
    print(f"成功載入 {len(sprites)} 個精靈圖片")
except Exception as e:
    # 如果載入失敗，使用簡單的幾何圖形代替
    print(f"載入精靈圖片時發生錯誤: {e}")
    print("將使用簡單圖形進行遊戲")
    sprites = None
    use_sprites = False  # 標記不使用精靈圖片

######################主角設定######################
player_w = 50  # 主角寬度
player_h = 50  # 主角高度
player_x = (bg_x - player_w) // 2  # 計算主角的初始X座標（置中）
player_y = bg_y - player_h - 50  # 計算主角的初始Y座標（底部上方50像素）
# 創建主角物件，設定為綠色，並傳入精靈圖片集合
player = Player(player_x, player_y, player_w, player_h, (0, 255, 0), sprites)

######################平台設定######################
platform_w = 80  # 平台寬度
platform_h = 20  # 平台高度
platforms = []  # 建立平台列表
# 創建底部平台，確保玩家不會掉出畫面
platform_x = (bg_x - platform_w) // 2  # 平台X座標（置中）
platform_y = bg_y - platform_h - 10  # 平台Y座標（底部上方10像素）
# 創建平台物件，設定為深灰色，並傳入精靈圖片集合
platform = Platform(
    platform_x, platform_y, platform_w, platform_h, (100, 100, 100), False, sprites
)
platforms.append(platform)

# 隨機生成其他平台
platform_count = random.randint(8, 10) + 10  # 隨機決定平台數量
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)  # 隨機生成平台的X座標
    y = (bg_y - 100) - (i * 60)  # 確保平台間距60像素
    platform = Platform(x, y, platform_w, platform_h, (100, 100, 100), False, sprites)
    platforms.append(platform)


######################字型設定######################
font = pygame.font.Font(
    "C:/Windows/Fonts/msjh.ttc", 24
)  # 設定字型和大小為微軟正黑體24點


######################主程式######################
# 更新相機位置的函式
def update_camera():
    """
    更新相機位置和平台\n
    - 當玩家上升到螢幕的一半高度以上時，固定玩家在螢幕中間\n
    - 將所有平台往下移動，製造出玩家繼續往上的錯覺\n
    - 移除超出畫面底部的平台\n
    - 在上方生成新的平台\n
    - 更新所有彈簧的位置，並移除超出畫面的彈簧\n
    """
    global score, initial_player_y, springs  # 使用全域變數
    screen_middle = bg_y // 2  # 螢幕中間的Y座標
    # 如果玩家位置高於螢幕中間，更新相機位置
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        # 計算分數：每上升10像素加1分
        score += int(camera_move / 10)

        # 更新所有平台的位置
        for platform in platforms:
            platform.rect.y += camera_move

        # 更新所有彈簧的位置
        for spring in springs:
            spring.move_with_platform(camera_move)

        # 移除超出畫面底部的平台
        y_min = bg_y
        for platform in platforms[:]:  # 使用切片創建副本以避免在迭代時修改列表
            if platform.rect.top > bg_y:
                platforms.remove(platform)
            if platform.rect.top < y_min:
                y_min = platform.rect.top

        # 移除超出畫面底部的彈簧
        for spring in springs[:]:  # 使用切片創建副本以避免在迭代時修改列表
            if spring.rect.top > bg_y:
                springs.remove(spring)

        # 在上方生成新的平台
        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60  # 確保新平台在最上方

            # 當分數超過100分時，有機會生成特殊平台（紅色，只能踩一次）
            if score > 100 and random.random() < special_platform_chance:
                platform = Platform(
                    x, y, platform_w, platform_h, (255, 0, 0), True, sprites
                )  # 紅色特殊平台
            else:
                platform = Platform(
                    x, y, platform_w, platform_h, (100, 100, 100), False, sprites
                )  # 一般深灰色平台
            platforms.append(platform)

            # 隨機在新平台上生成彈簧（20%機率）
            if random.random() < spring_chance:
                spring_w = 35  # 彈簧寬度
                spring_h = 20  # 彈簧高度
                spring_x = (
                    platform.rect.x + (platform_w - spring_w) // 2
                )  # 彈簧X座標（置中）
                spring_y = platform.rect.y - spring_h  # 彈簧Y座標（平台上方）
                spring = Spring(
                    spring_x, spring_y, spring_w, spring_h, (255, 215, 0), sprites
                )  # 建立黃色彈簧
                springs.append(spring)


def reset_game():
    """
    重置遊戲狀態\n
    - 重設玩家位置\n
    - 清空並重新生成平台\n
    - 清空並重置彈簧\n
    - 重設分數和遊戲狀態\n
    """
    global score, game_over, platforms, initial_player_y, highest_score, springs

    # 不再播放 gameover 音效

    # 重設玩家位置
    player.rect.x = (bg_x - player_w) // 2
    player.rect.y = bg_y - player_h - 50
    player.velocity_y = 0

    # 清空平台列表與彈簧列表
    platforms.clear()
    springs.clear()  # 清空所有彈簧

    # 重新生成底部平台
    platform_x = (bg_x - platform_w) // 2
    platform_y = bg_y - platform_h - 10
    platform = Platform(
        platform_x, platform_y, platform_w, platform_h, (100, 100, 100), False, sprites
    )
    platforms.append(platform)

    # 重新生成其他平台
    for i in range(platform_count - 1):
        x = random.randint(0, bg_x - platform_w)
        y = (bg_y - 100) - (i * 60)
        platform = Platform(
            x, y, platform_w, platform_h, (100, 100, 100), False, sprites
        )
        platforms.append(platform)

        # 隨機在新平台上生成彈簧
        if random.random() < spring_chance:
            spring_w = 35
            spring_h = 20
            spring_x = platform.rect.x + (platform_w - spring_w) // 2
            spring_y = platform.rect.y - spring_h
            spring = Spring(
                spring_x, spring_y, spring_w, spring_h, (255, 215, 0), sprites
            )
            springs.append(spring)

    # 重設遊戲相關變數
    score = 0
    game_over = False
    initial_player_y = player.rect.y


while True:
    FPS.tick(60)  # 限制遊戲更新率為每秒60幀
    screen.fill((255, 255, 255))  # 用白色填充畫面背景

    # 處理事件（關閉視窗、遊戲結束時重新開始）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over:
            reset_game()

    if not game_over:
        update_camera()  # 更新相機位置和平台

        # 處理左右移動控制（支援持續按壓與A/D鍵）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move(-1, bg_x)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move(1, bg_x)

        # 應用重力效果和處理碰撞
        player.apply_gravity()
        # 先檢查彈簧碰撞，如果沒碰到彈簧才檢查平台碰撞
        if not player.check_spring_collision(springs):
            player.check_platform_collision(platforms)

        # 檢查遊戲結束條件（玩家掉出畫面）
        if player.rect.top > bg_y:
            game_over = True
            if score > highest_score:
                highest_score = score
    else:
        # 事件處理迴圈（遊戲結束時）

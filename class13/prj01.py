######################載入套件######################
import pygame  # 載入 pygame 套件，用於遊戲開發
import sys  # 載入 sys 套件，用於系統相關操作
import os  # 載入 os 套件，用於處理檔案路徑
from pygame.locals import *  # 載入 pygame 常用常數，如 QUIT 等

import random


# 載入PNG補給箱圖片
img_box1 = pygame.image.load(os.path.join("pygay", "class13", "image", "box1.png"))
img_box2 = pygame.image.load(os.path.join("pygay", "class13", "image", "box2.png"))
img_box3 = pygame.image.load(os.path.join("pygay", "class13", "image", "box3.png"))


# 補給箱類別
class SupplyBox:
    """
    補給箱類別，管理補給箱的生成、移動、繪製與屬性
    """

    def __init__(self, x, y, box_type, img):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.type = box_type  # 1:回血 2:連發 3:大範圍
        self.img = img
        self.active = True
        self.speed = 6

    def move(self):
        if self.active:
            self.rect.y += self.speed
            if self.rect.top > bg_y:
                self.active = False

    def draw(self, screen):
        if self.active and self.img:
            sprite = pygame.transform.scale(
                self.img, (self.rect.width, self.rect.height)
            )
            screen.blit(sprite, self.rect)


# ---補給箱設定---
supply_boxes = []  # 補給箱列表
supply_imgs = [img_box1, img_box2, img_box3]


######################定義函式######################
def roll_bg():
    """
    實現背景捲動效果\n
    - 持續更新 roll_y 變數\n
    - 繪製上下兩部分背景圖片實現連續捲動\n
    """
    global roll_y  # 使用全域變數

    # 繪製上半部背景圖片 (圖片1)
    screen.blit(img_bg, [0, roll_y - bg_y])
    # 繪製下半部背景圖片 (圖片2)
    screen.blit(img_bg, [0, roll_y])

    # 更新捲動位置
    roll_y = (
        roll_y + 10
    ) % bg_y  # 每次向下捲動20像素，並使用模運算保持在背景高度範圍內


######################初始化設定######################
# 初始化遊戲
os.chdir(sys.path[0])  # 設定當前工作目錄為程式所在位置
pygame.init()  # 初始化 pygame
clock = pygame.time.Clock()  # 建立時鐘物件，用於控制遊戲更新速率

######################載入圖片######################
# 載入背景圖片
img_bg = pygame.image.load("image/space.png")
# 載入太空船圖片
img_player_m = pygame.image.load("image/fighter_M.png")  # 載入太空船中間飛行圖片
img_player_l = pygame.image.load("image/fighter_L.png")  # 載入太空船左轉圖片
img_player_r = pygame.image.load("image/fighter_R.png")  # 載入太空船右轉圖片
# 載入火焰推進圖片（步驟4新增）
img_burner = pygame.image.load("image/starship_burner.png")  # 載入太空船火焰推進圖片
# 載入飛彈圖片（步驟5新增）
img_missile = pygame.image.load("image/bullet.png")  # 載入飛彈圖片


# 載入多種敵機圖片（步驟8新增）
img_enemy1 = pygame.image.load("image/enemy1.png")  # 載入敵機圖片1
img_enemy2 = pygame.image.load("image/enemy2.png")  # 載入敵機圖片2
# 建立敵機圖片列表，之後可隨機選擇
enemy_images = [img_enemy1, img_enemy2]

# 載入爆炸動畫圖片
explosion_images = [
    pygame.image.load("image/explosion1.png"),
    pygame.image.load("image/explosion2.png"),
    pygame.image.load("image/explosion3.png"),
    pygame.image.load("image/explosion4.png"),
    pygame.image.load("image/explosion5.png"),
]

# 載入 gameover 圖片
img_gameover = pygame.image.load("image/gameover.png")

# 建立太空船圖片字典，包含三種狀態
player_sprites = {
    "fighter_M": img_player_m,  # 直飛
    "fighter_L": img_player_l,  # 左轉
    "fighter_R": img_player_r,  # 右轉
}

######################遊戲視窗設定######################
# 設定視窗標題
pygame.display.set_caption("Galaxy Lancer")

# 取得背景圖片尺寸作為視窗大小
bg_x = img_bg.get_width()  # 背景圖片寬度
bg_y = img_bg.get_height()  # 背景圖片高度
bg_size = (bg_x, bg_y)  # 視窗尺寸元組

# 建立視窗
screen = pygame.display.set_mode(bg_size)

# 初始化背景捲動位置
roll_y = 0  # 背景圖片的Y軸位置


######################物件類別######################
class Player:
    """太空船類別，負責管理玩家太空船的所有行為"""

    def __init__(self, x, y, width, height, color, sprites=None, burner_img=None):
        """
        初始化太空船\n
        x, y: 太空船的左上角座標\n
        width, height: 太空船的寬度和高度\n
        color: 太空船的顏色 (RGB格式)\n
        sprites: 包含太空船精靈的字典，如果為None則使用矩形繪製\n
        burner_img: 火焰推進圖片（步驟4新增）\n
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立太空船的矩形區域
        self.color = color  # 設定顏色，用於無圖片時的顯示
        self.speed = 10  # 設定太空船的移動速度
        self.sprites = sprites  # 儲存太空船圖片
        self.facing_direction = "M"  # 方向狀態：'L'=左轉, 'R'=右轉, 'M'=直飛
        self.burner_img = burner_img  # 火焰推進圖片
        self.burn_shift = 0  # 火焰晃動位移（步驟4新增）
        # 生命值與無敵狀態
        self.hp = 100  # 初始生命值
        self.invincible = False  # 無敵狀態
        self.invincible_timer = 0  # 無敵計時
        self.visible = True  # 閃爍顯示

    def draw(self, screen):
        """
        在螢幕上繪製太空船\n
        根據當前方向狀態選擇正確的太空船圖片顯示\n
        並在太空船底部繪製火焰推進效果（步驟4新增）\n
        screen: pygame視窗物件\n
        """
        # 直接在這裡取得按鍵狀態
        keys = pygame.key.get_pressed()
        show_burner = True
        if keys[K_DOWN]:
            show_burner = False
        # 無敵時火焰也閃爍
        burner_visible = True
        if self.invincible:
            if pygame.time.get_ticks() // 100 % 2 == 0:
                burner_visible = False
        if self.burner_img and show_burner and burner_visible:
            # 取得火焰圖片原始尺寸
            burner_w = self.rect.width // 4  # 火焰寬度為太空船四分之一
            burner_h = self.rect.height // 2  # 火焰高度為太空船一半
            # 動態調整火焰晃動位移
            self.burn_shift = (self.burn_shift + 2) % 12  # 每次+2，循環0~11
            # 調整火焰圖片大小
            burner_img = pygame.transform.scale(self.burner_img, (burner_w, burner_h))
            # 計算火焰繪製位置（置於太空船底部中央，並上下晃動）
            burner_x = self.rect.centerx - burner_w // 2
            burner_y = self.rect.bottom - burner_h // 2 + self.burn_shift
            # 繪製火焰圖片
            screen.blit(burner_img, (burner_x, burner_y))
        # 閃爍顯示（無敵時）
        if self.invincible:
            # 每 100ms 閃爍一次
            if pygame.time.get_ticks() // 100 % 2 == 0:
                self.visible = False
            else:
                self.visible = True
        else:
            self.visible = True

        if self.visible:
            if self.sprites:
                # 根據方向狀態選擇對應圖片
                sprite_key = f"fighter_{self.facing_direction}"
                if sprite_key in self.sprites:
                    # 調整圖片大小以符合太空船尺寸
                    sprite = pygame.transform.scale(
                        self.sprites[sprite_key], (self.rect.width, self.rect.height)
                    )
                    # 繪製太空船圖片
                    screen.blit(sprite, self.rect)
                    return
            # 如果沒有圖片，就畫一個矩形代表太空船
            pygame.draw.rect(screen, self.color, self.rect)

    def update_invincible(self):
        """
        更新無敵狀態計時
        """
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def handle_input(self, keys):
        """
        處理玩家輸入並移動太空船\n
        根據左右鍵自動更新方向狀態，並處理四方向移動\n
        keys: pygame.key.get_pressed()返回的按鍵狀態\n
        """
        moved = False  # 用於判斷是否有左右移動
        # 檢查方向鍵輸入並移動太空船
        if keys[K_LEFT] and self.rect.left > 0:  # 左方向鍵且未超出左邊界
            self.rect.x -= self.speed
            self.facing_direction = "L"  # 設定為左轉
            moved = True
        if keys[K_RIGHT] and self.rect.right < bg_x:  # 右方向鍵且未超出右邊界
            self.rect.x += self.speed
            self.facing_direction = "R"  # 設定為右轉
            moved = True
        if not moved:
            self.facing_direction = "M"  # 沒有左右移動時顯示直飛
        if keys[K_UP] and self.rect.top > 0:  # 上方向鍵且未超出上邊界
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.bottom < bg_y:  # 下方向鍵且未超出下邊界
            self.rect.y += self.speed


class Missile:
    """
    飛彈類別，負責管理飛彈的發射、移動與繪製
    """

    def __init__(self, x, y, width, height, speed, img=None):
        """
        初始化飛彈
        x, y: 飛彈的左上角座標
        width, height: 飛彈的寬度和高度
        speed: 飛彈的垂直移動速度（負值表示向上）
        img: 飛彈圖片
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立飛彈的矩形區域
        self.speed = speed  # 設定飛彈速度
        self.active = False  # 飛彈是否正在飛行中
        self.img = img  # 飛彈圖片

    def launch(self, x, y):
        """
        發射飛彈，將飛彈移動到指定位置並啟動
        x, y: 飛彈發射的起始座標（通常為太空船中央上方）
        """
        self.rect.centerx = x
        self.rect.bottom = y
        self.active = True  # 啟動飛彈

    def move(self):
        """
        移動飛彈，並檢查是否飛出畫面
        """
        if self.active:
            self.rect.y += self.speed  # 垂直移動
            # 如果飛彈飛出畫面上方，則設為未啟動
            if self.rect.bottom < 0:
                self.active = False

    def draw(self, screen):
        """
        繪製飛彈
        screen: pygame視窗物件
        """
        if self.active:
            if self.img:
                # 調整圖片大小以符合飛彈尺寸
                sprite = pygame.transform.scale(
                    self.img, (self.rect.width, self.rect.height)
                )
                screen.blit(sprite, self.rect)
            else:
                # 沒有圖片時以黃色矩形顯示
                pygame.draw.rect(screen, (255, 255, 0), self.rect)


class Enemy:
    """
    敵機類別，負責管理敵機的生成、移動、繪製與重置
    - 支援多種敵機圖片，重置時隨機選擇圖片（步驟8新增）
    """

    def __init__(self, x, y, width, height, speed, enemy_images, explosion_images=None):
        """
        初始化敵機
        x, y: 敵機的左上角座標
        width, height: 敵機的寬度和高度
        speed: 敵機的垂直移動速度（正值表示向下）
        img: 敵機圖片（初始化時隨機選擇）
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立敵機的矩形區域
        self.speed = speed  # 設定敵機速度
        self.img = random.choice(enemy_images)
        self.enemy_images = enemy_images  # 儲存敵機圖片列表
        self.active = True  # 敵機是否啟動
        self.exploding = False  # 敵機是否正在爆炸
        self.explode_frame = 0  # 爆炸動畫幀數
        self.explosion_images = explosion_images if explosion_images else []

    def move(self, bg_y, bg_x):
        """
        移動敵機，並檢查是否飛出畫面底部，若超出則重置到畫面上方隨機位置
        """
        self.rect.y += self.speed  # 垂直向下移動
        # 如果敵機超出畫面底部，則重置到畫面上方隨機位置
        if self.rect.top > bg_y:
            self.reset(bg_x)

    def reset(self, bg_x):
        """重置敵機到畫面上方隨機位置
        參數:
            bg_x: 遊戲視窗寬度，用於計算隨機X座標範圍
        功能:
            - 重置敵機位置到畫面上方
            - 隨機選擇新的敵機圖片
            - 重設敵機狀態
        """
        # 隨機設定X座標，確保敵機不會超出畫面
        self.rect.x = random.randint(0, max(0, bg_x - self.rect.width))
        # 將Y座標設定在畫面上方外，並隨機分散高度避免同時出現
        self.rect.y = -self.rect.height - random.randint(0, bg_y // 2)
        # 從敵機圖片列表中隨機選擇一張
        self.img = random.choice(self.enemy_images) if self.enemy_images else None
        # 重置敵機狀態
        self.active = True
        self.exploding = False
        self.explode_frame = 0

    def draw(self, screen):
        """
        繪製敵機或爆炸動畫
        screen: pygame視窗物件
        """
        if self.exploding and self.explosion_images:
            # 爆炸動畫播放
            if self.explode_frame < len(self.explosion_images):
                exp_img = pygame.transform.scale(
                    self.explosion_images[self.explode_frame],
                    (self.rect.width, self.rect.height),
                )
                screen.blit(exp_img, self.rect)
                self.explode_frame += 1
            else:
                self.exploding = False
                self.active = False
        elif self.active:
            if self.img:
                # 調整圖片大小以符合敵機尺寸
                sprite = pygame.transform.scale(
                    self.img, (self.rect.width, self.rect.height)
                )
                screen.blit(sprite, self.rect)
            else:
                # 沒有圖片時以紅色矩形顯示
                pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def check_collision(self, missile):
        """
        檢查敵機與飛彈的碰撞
        若碰撞，則觸發爆炸動畫
        """
        if self.active and missile.active and self.rect.colliderect(missile.rect):
            self.exploding = True
            self.explode_frame = 0
            missile.active = False


######################玩家設定######################
# 建立玩家太空船
player_w = 80  # 太空船寬度
player_h = 80  # 太空船高度
# 設定太空船初始位置（畫面中央）
player_x = (bg_x - player_w) // 2
player_y = bg_y - player_h - 50
# 建立太空船物件，傳入火焰推進圖片（步驟4新增）
player = Player(
    player_x, player_y, player_w, player_h, (0, 255, 0), player_sprites, img_burner
)

######################飛彈設定（步驟5新增）######################
missile_w = 12  # 飛彈寬度
missile_h = 32  # 飛彈高度
missile_speed = -20  # 飛彈速度（負值向上）

######################飛彈連發設定（步驟6新增）######################
# 設定飛彈最大數量
MISSILE_MAX = 10  # 最多同時存在10顆飛彈
# 建立飛彈物件列表，使用 list comprehension 初始化
missiles = [
    Missile(0, 0, missile_w, missile_h, missile_speed, img_missile)
    for _ in range(MISSILE_MAX)
]
# 飛彈冷卻時間設定
msl_cooldown = 0  # 當前冷卻時間
msl_cooldown_max = 10  # 冷卻最大值（單位：幀，數字越小連發越快）

######################敵機設定（步驟7、9新增）######################
# 設定敵機群基本參數
EMY_NUM = 5  # 敵機總數量
EMY_W = 60  # 每台敵機寬度
EMY_H = 60  # 每台敵機高度
EMY_SPEED = 5  # 敵機下落速度

# 建立敵機物件列表
emy_list = []  # 用於儲存所有敵機物件

# 依序建立多個敵機物件，設定在畫面上方不同位置
for i in range(EMY_NUM):
    # 隨機產生X座標，確保敵機不會超出畫面邊界
    emy_x = random.randint(0, bg_x - EMY_W)
    # Y座標設定在畫面上方外，每台敵機的高度都不同，避免同時進入畫面
    emy_y = -EMY_H - random.randint(0, bg_y)
    # 建立新的敵機物件，傳入爆炸動畫圖片
    emy = Enemy(emy_x, emy_y, EMY_W, EMY_H, EMY_SPEED, enemy_images, explosion_images)
    # 將敵機加入列表
    emy_list.append(emy)

######################主程式######################
while True:  # 遊戲主迴圈
    # 補給箱效果狀態
    if "supply_effect" not in globals():
        supply_effect = None  # None/"rapid"/"spread"
        supply_timer = 0

    # 更新補給箱位置
    for box in supply_boxes:
        box.move()

    # 敵機被擊落時有機率掉落補給箱
    for enemy in emy_list:
        if enemy.exploding and enemy.explode_frame == 1:
            r = random.random()
            if r < 0.5:
                # 50% 機率掉落箱子1
                supply_boxes.append(
                    SupplyBox(enemy.rect.centerx, enemy.rect.centery, 1, img_box1)
                )
            elif r < 0.8:
                # 30% 機率掉落箱子2
                supply_boxes.append(
                    SupplyBox(enemy.rect.centerx, enemy.rect.centery, 2, img_box2)
                )
            elif r < 1.0:
                # 20% 機率掉落箱子3
                supply_boxes.append(
                    SupplyBox(enemy.rect.centerx, enemy.rect.centery, 3, img_box3)
                )

    # ---補給箱效果可重疊且不會自動結束---
    if "supply_effects" not in globals():
        supply_effects = {}

    # 玩家碰到補給箱
    for box in supply_boxes:
        if box.active and player.rect.colliderect(box.rect):
            if box.type == 1:
                player.hp = min(player.hp + 10, 100)
            elif box.type == 2:
                supply_effects["rapid"] = True
            elif box.type == 3:
                supply_effects["spread"] = True
            box.active = False

    # 只要玩家受傷或死亡，所有效果消失
    if player.invincible or player.hp <= 0:
        supply_effects.clear()
    clock.tick(60)  # 限制迴圈速度為每秒60次

    # 遊戲結束狀態
    gameover = False

    # 每幀自動減少飛彈冷卻時間（步驟6新增）
    if msl_cooldown > 0:
        msl_cooldown -= 1

    # 取得使用者輸入
    for event in pygame.event.get():
        if event.type == QUIT:  # 如果使用者按下視窗的關閉按鈕
            sys.exit()  # 結束程式

        # 遊戲結束時，按任意鍵重啟
        if gameover:
            if event.type == KEYDOWN:
                # 重設玩家狀態
                player.hp = 100
                player.invincible = False
                player.invincible_timer = 0
                for enemy in emy_list:
                    enemy.reset(bg_x)
                continue

        # 檢查按鍵事件
        elif event.type == KEYDOWN:
            if event.key == K_F1:  # 按F1切換全螢幕
                screen = pygame.display.set_mode(bg_size, FULLSCREEN)
            elif event.key == K_ESCAPE:  # 按ESC退出全螢幕
                screen = pygame.display.set_mode(bg_size)
            # 處理飛彈連發發射（步驟6新增）
            elif event.key == K_SPACE and msl_cooldown == 0 and not gameover:
                if "rapid" in supply_effects and "spread" in supply_effects:
                    # 連發+大範圍同時
                    for i, msl in enumerate(missiles):
                        if not msl.active:
                            msl.launch(player.rect.centerx, player.rect.centery)
                            msl_cooldown = 2
                            if i + 1 < len(missiles) and not missiles[i + 1].active:
                                missiles[i + 1].launch(
                                    player.rect.centerx - 30, player.rect.centery
                                )
                            if i + 2 < len(missiles) and not missiles[i + 2].active:
                                missiles[i + 2].launch(
                                    player.rect.centerx + 30, player.rect.centery
                                )
                            break
                elif "rapid" in supply_effects:
                    for msl in missiles:
                        if not msl.active:
                            msl.launch(player.rect.centerx, player.rect.centery)
                            msl_cooldown = 2
                            break
                elif "spread" in supply_effects:
                    for i, msl in enumerate(missiles):
                        if not msl.active:
                            msl.launch(player.rect.centerx, player.rect.centery)
                            msl_cooldown = msl_cooldown_max
                            if i + 1 < len(missiles) and not missiles[i + 1].active:
                                missiles[i + 1].launch(
                                    player.rect.centerx - 30, player.rect.centery
                                )
                            if i + 2 < len(missiles) and not missiles[i + 2].active:
                                missiles[i + 2].launch(
                                    player.rect.centerx + 30, player.rect.centery
                                )
                            break
                else:
                    for msl in missiles:
                        if not msl.active:
                            msl.launch(player.rect.centerx, player.rect.centery)
                            msl_cooldown = msl_cooldown_max
                            break

    # 取得按鍵狀態並更新玩家位置
    keys = pygame.key.get_pressed()  # 獲取當前按下的按鍵狀態
    if not gameover:
        player.handle_input(keys)  # 根據按鍵狀態更新太空船位置

    # 更新飛彈位置（步驟6新增）
    for msl in missiles:
        msl.move()

    # 更新敵機群位置（步驟9新增）
    for enemy in emy_list:
        enemy.move(bg_y, bg_x)

    # 檢查敵機與飛彈的碰撞
    for enemy in emy_list:
        for msl in missiles:
            enemy.check_collision(msl)

    # 檢查玩家與敵機碰撞
    if not player.invincible and not gameover:
        for enemy in emy_list:
            if enemy.active and player.rect.colliderect(enemy.rect):
                # 玩家受傷
                player.hp -= 20
                player.invincible = True
                player.invincible_timer = 60  # 1 秒無敵（60 幀）
                # 敵機爆炸
                enemy.exploding = True
                enemy.explode_frame = 0
                break

    # 更新無敵狀態
    player.update_invincible()

    # --- 若敵機被消滅或飛出畫面，立即重生 ---
    for enemy in emy_list:
        if not enemy.active and not enemy.exploding:
            enemy.reset(bg_x)

    # 更新遊戲畫面
    roll_bg()  # 更新背景捲動
    # 繪製所有飛彈
    for msl in missiles:
        msl.draw(screen)
    # 繪製補給箱
    for box in supply_boxes:
        box.draw(screen)
    player.draw(screen)  # 繪製玩家太空船
    # 繪製敵機群（步驟9新增）
    for enemy in emy_list:
        enemy.draw(screen)

    # 顯示生命值進度條
    bar_w = 200
    bar_h = 20
    bar_x = 20
    bar_y = 20
    hp_ratio = max(player.hp, 0) / 100
    pygame.draw.rect(
        screen, (255, 255, 255), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 2
    )
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

    # 判斷遊戲結束
    if player.hp <= 0:
        gameover = True
        # 顯示 gameover 圖片
        img_go = pygame.transform.scale(img_gameover, (bg_x, bg_y))
        screen.blit(img_go, (0, 0))
        pygame.display.update()
        # 等待按鍵重啟
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    # 重設玩家狀態
                    player.hp = 100
                    player.invincible = False
                    player.invincible_timer = 0
                    for enemy in emy_list:
                        enemy.reset(bg_x)
                    waiting = False
            clock.tick(30)
        continue

    pygame.display.update()  # 更新螢幕顯示

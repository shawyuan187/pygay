###################### 載入套件區塊 ######################
import pygame  # 遊戲開發主套件
import sys  # 系統相關操作
import os  # 處理檔案路徑
from pygame.locals import *  # 載入 Pygame 常數
import random  # 隨機數生成


###################### 定義函式區塊 ######################
def roll_bg(screen, bg_img, roll_y):
    """
    捲動背景函式
    參數:
        screen: 遊戲視窗 Surface
        bg_img: 背景圖片 Surface
        roll_y: 當前捲動的 Y 座標
    功能:
        讓背景圖片上下無縫捲動
    """
    bg_y = bg_img.get_height()
    # 先畫出主要背景
    screen.blit(bg_img, (0, roll_y - bg_y))
    # 再畫出補足的背景（讓畫面下方補滿）
    screen.blit(bg_img, (0, roll_y))
    # 無縫捲動效果


###################### 玩家類別區塊 ######################
class Player:
    def __init__(
        self, x, y, width, height, color, speed=10, sprites=None, burner_img=None
    ):
        """
        初始化玩家太空船
        x, y: 太空船左上角座標
        width, height: 太空船尺寸
        color: 太空船顏色 (RGB)
        speed: 移動速度（每次移動的像素數）
        sprites: 太空船圖片字典，包含三種方向（M/L/R），若為None則用顏色方塊
        burner_img: 火焰推進圖片 Surface，若為None則不顯示火焰
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        # sprites 字典包含三種方向的太空船圖片：M(直飛)、L(左轉)、R(右轉)
        self.sprites = sprites if isinstance(sprites, dict) else None
        self.facing_direction = "M"  # 當前太空船朝向，預設為直飛
        if self.sprites:
            for k in self.sprites:
                # 動態縮放每個方向的太空船圖片，確保尺寸一致
                self.sprites[k] = pygame.transform.scale(
                    self.sprites[k], (width, height)
                )
        # 火焰推進相關屬性
        self.burner_img = None  # 火焰圖片 Surface
        self.burner_w = width // 4  # 火焰寬度為太空船寬度的1/4
        self.burner_h = 0  # 火焰高度
        self.burn_shift = 0  # 火焰上下晃動的位移
        if burner_img:
            # 取得原始火焰圖片的寬高
            orig_w, orig_h = burner_img.get_width(), burner_img.get_height()
            # 動態縮放火焰圖片，保持寬高比例
            self.burner_h = int(self.burner_w * orig_h / orig_w)
            self.burner_img = pygame.transform.scale(
                burner_img, (self.burner_w, self.burner_h)
            )
            # 火焰圖片會根據太空船寬度自動縮放，確保比例正確

    def draw(self, screen):
        """
        在畫面上繪製太空船與火焰推進效果
        1. 先繪製火焰推進（若有火焰圖片）
        2. 再繪製太空船（根據方向顯示對應圖片，若無圖片則顯示顏色方塊）
        火焰會隨 burn_shift 變化產生晃動動畫
        """
        # 畫火焰推進效果
        if self.burner_img:
            # 火焰每幀上下晃動，產生推進動畫
            self.burn_shift = (self.burn_shift + 2) % 12  # 0~11循環
            # 火焰位置：太空船底部中央偏下，並有微小上下位移
            burner_x = self.rect.centerx - self.burner_w // 2
            # 火焰Y座標會隨 burn_shift 產生上下晃動，讓火焰更有動態感
            burner_y = self.rect.bottom - self.burner_h // 2 + (self.burn_shift // 3)
            screen.blit(self.burner_img, (burner_x, burner_y))
        # 畫太空船
        if self.sprites and self.facing_direction in self.sprites:
            # 根據目前方向狀態選擇對應的太空船圖片
            screen.blit(self.sprites[self.facing_direction], self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def handle_input(self, keys, bg_x, bg_y):
        """
        處理玩家輸入與移動，並自動更新方向狀態
        keys: pygame.key.get_pressed() 的結果
        bg_x, bg_y: 視窗寬高，用於邊界檢查
        """
        moved = False
        # 預設為直飛
        self.facing_direction = "M"
        if keys[K_LEFT]:
            self.rect.x -= self.speed
            self.facing_direction = "L"  # 按左鍵時顯示左轉圖片
            moved = True
        if keys[K_RIGHT]:
            self.rect.x += self.speed
            self.facing_direction = "R"  # 按右鍵時顯示右轉圖片
            moved = True
        if keys[K_UP]:
            self.rect.y -= self.speed
            moved = True
        if keys[K_DOWN]:
            self.rect.y += self.speed
            moved = True

        # 邊界檢查，不能超出畫面
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > bg_x:
            self.rect.right = bg_x
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > bg_y:
            self.rect.bottom = bg_y


###################### 飛彈類別區塊 ######################
class Missile:
    def __init__(self, width, height, speed, img=None):
        """
        初始化飛彈
        width, height: 飛彈尺寸
        speed: 飛彈移動速度（負值表示向上）
        img: 飛彈圖片 Surface，若為None則用顏色方塊
        """
        self.width = width
        self.height = height
        self.speed = speed
        self.img = img
        self.active = False  # 是否正在飛行
        self.rect = pygame.Rect(0, 0, width, height)  # 飛彈的矩形區域

    def launch(self, x, y):
        """
        發射飛彈，設定初始位置於玩家中心
        x, y: 發射起點（通常為玩家中心）
        """
        self.rect.centerx = x  # 設定飛彈水平中心與玩家對齊
        self.rect.bottom = y  # 設定飛彈底部在玩家頂部
        self.active = True  # 啟動飛彈狀態

    def handle_movement(self, bg_y):
        """
        處理飛彈移動與邊界檢查
        bg_y: 畫面高度，用於判斷是否飛出畫面
        """
        if self.active:
            self.rect.y += self.speed  # 依速度移動飛彈
            # 若飛彈飛出畫面上方則設為不活躍
            if self.rect.bottom < 0:
                self.active = False

    def draw(self, screen):
        """
        在畫面上繪製飛彈
        若有圖片則顯示圖片，否則以紅色方塊表示
        """
        if self.active:
            if self.img:
                screen.blit(self.img, self.rect)
            else:
                pygame.draw.rect(screen, (255, 0, 0), self.rect)  # 紅色方塊


###################### 敵人類別區塊 ######################
class Enemy:
    def __init__(self, x, y, width, height, speed, enemy_images, explode_imgs=None):
        """
        初始化敵人
        x, y: 敵人左上角座標
        width, height: 敵人尺寸
        speed: 敵人下落速度
        enemy_images: 敵人圖片列表，重生時隨機選擇
        explode_imgs: 爆炸動畫圖片列表
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.enemy_images = enemy_images
        self.img = random.choice(self.enemy_images) if self.enemy_images else None
        self.active = True  # 是否存活
        # 爆炸動畫相關
        self.explode_imgs = explode_imgs if explode_imgs else []
        self.exploding = False
        self.explode_frame = 0

    def move(self, bg_y, bg_x):
        """
        控制敵人自動往下移動，超出畫面下方則重生並隨機換圖
        bg_y: 畫面高度
        bg_x: 畫面寬度
        """
        if self.active and not self.exploding:
            self.rect.y += self.speed
            if self.rect.top > bg_y:
                self.reset(bg_x)

    def reset(self, bg_x):
        """
        敵人重生於畫面上方隨機位置，並隨機換一種圖片與重設狀態
        bg_x: 畫面寬度
        """
        # 隨機X座標，確保不會超出畫面
        self.rect.x = random.randint(0, max(0, bg_x - self.rect.width))
        # Y座標設為畫面上方外，並可隨機分布於更高處，避免同時出現
        self.rect.y = -self.rect.height - random.randint(0, bg_y // 2)
        # 隨機選擇一種敵人圖片
        self.img = random.choice(self.enemy_images) if self.enemy_images else None
        # 重設爆炸動畫狀態
        self.exploding = False
        self.explode_frame = 0
        self.active = True

    def draw(self, screen):
        """
        在畫面上繪製敵人或爆炸動畫
        """
        if self.active:
            if self.exploding and self.explode_imgs:
                idx = self.explode_frame // 3
                if idx < len(self.explode_imgs):
                    img = self.explode_imgs[idx]
                    img = pygame.transform.scale(
                        img, (self.rect.width, self.rect.height)
                    )
                    screen.blit(img, self.rect)
                    self.explode_frame += 1
                else:
                    self.active = False
            elif self.img and not self.exploding:
                img_scaled = pygame.transform.scale(
                    self.img, (self.rect.width, self.rect.height)
                )
                screen.blit(img_scaled, self.rect)
            elif not self.exploding:
                pygame.draw.rect(screen, (255, 128, 0), self.rect)

    def check_collision(self, missile):
        """
        檢查與飛彈的碰撞
        missile: Missile 物件
        若碰撞則敵人進入爆炸動畫，飛彈消失
        """
        if (
            self.active
            and not self.exploding
            and missile.active
            and self.rect.colliderect(missile.rect)
        ):
            self.exploding = True
            self.explode_frame = 0
            missile.active = False
            return True
        return False


###################### 敵人群系統區塊（步驟9） ######################
# 步驟9：實現敵機群系統，讓多台敵機分布於畫面上方外並持續下落
EMY_NUM = 5  # 敵機數量，可依需求調整
EMY_W = 60  # 敵機寬度
EMY_H = 60  # 敵機高度
EMY_SPEED = 5  # 敵機下落速度

emy_list = []  # 敵機物件列表

# 依序建立多個敵機物件，y座標分布於畫面上方外，避免同時出現
for i in range(EMY_NUM):
    emy_x = random.randint(0, bg_x - EMY_W)
    emy_y = -EMY_H - random.randint(0, bg_y)
    emy = Enemy(emy_x, emy_y, EMY_W, EMY_H, EMY_SPEED, enemy_images, explode_imgs)
    emy_list.append(emy)


###################### 初始化設定區塊 ######################
# 設定執行路徑為目前檔案位置，避免路徑錯誤
os.chdir(sys.path[0])

pygame.init()  # 初始化 pygame
clock = pygame.time.Clock()  # 建立時鐘物件，用於控制遊戲速度

###################### 載入圖片區塊 ######################
# 載入太空背景圖片，請確保 image/space.png 存在
bg_img = pygame.image.load(os.path.join("image", "space.png"))
# 載入太空船三方向圖片，組成 sprites 字典
player_sprites = {}
try:
    player_sprites["M"] = pygame.image.load(os.path.join("image", "fighter_M.png"))
except Exception as e:
    print(f"載入直飛圖片失敗: {e}")
try:
    player_sprites["L"] = pygame.image.load(os.path.join("image", "fighter_L.png"))
except Exception as e:
    print(f"載入左轉圖片失敗: {e}")
try:
    player_sprites["R"] = pygame.image.load(os.path.join("image", "fighter_R.png"))
except Exception as e:
    print(f"載入右轉圖片失敗: {e}")
if not player_sprites:
    player_sprites = None
# 載入火焰推進圖片
try:
    burner_img = pygame.image.load(os.path.join("image", "starship_burner.png"))
except Exception as e:
    print(f"載入火焰圖片失敗: {e}")
    burner_img = None
# 載入飛彈圖片
try:
    missile_img = pygame.image.load(os.path.join("image", "bullet.png"))
except Exception as e:
    print(f"載入飛彈圖片失敗: {e}")
    missile_img = None
# 載入多種敵人圖片
enemy_images = []
try:
    img_enemy1 = pygame.image.load(os.path.join("image", "enemy1.png"))
    enemy_images.append(img_enemy1)
except Exception as e:
    print(f"載入敵人圖片 enemy1.png 失敗: {e}")
try:
    img_enemy2 = pygame.image.load(os.path.join("image", "enemy2.png"))
    enemy_images.append(img_enemy2)
except Exception as e:
    print(f"載入敵人圖片 enemy2.png 失敗: {e}")
# 若 enemy_images 為空，則 fallback
if not enemy_images:
    enemy_images = [enemy_img] if enemy_img else []
# 載入爆炸動畫圖片（假設檔名為 explode1.png, explode2.png, ...）
explode_imgs = []
for i in range(1, 6):
    try:
        img = pygame.image.load(os.path.join("image", f"explode{i}.png"))
        explode_imgs.append(img)
    except Exception as e:
        # 若有缺圖可略過
        pass

###################### 遊戲視窗設定區塊 ######################
bg_x = bg_img.get_width()  # 取得背景圖片寬度
bg_y = bg_img.get_height()  # 取得背景圖片高度
screen = pygame.display.set_mode((bg_x, bg_y))  # 設定遊戲視窗大小
pygame.display.set_caption("Galaxy Lancer")  # 設定視窗標題

roll_y = 0  # 捲動背景的 Y 座標初始值

###################### 玩家設定區塊 ######################
# 太空船尺寸與初始位置
player_w = 80
player_h = 80
player_x = (bg_x - player_w) // 2  # 畫面中央
player_y = (bg_y - player_h) // 2
player_color = (0, 255, 255)  # 青色，若無圖片時用
player = Player(
    player_x, player_y, player_w, player_h, player_color, 10, player_sprites, burner_img
)
# 建立飛彈物件（單發，重複利用）
missile_w = 16
missile_h = 32
missile_speed = -20  # 負值表示往上
missile = Missile(missile_w, missile_h, missile_speed, missile_img)  # 建立飛彈物件

# 敵人設定
enemy_w = 64
enemy_h = 64
enemy_speed = 8  # 敵人下落速度
ENEMY_MAX = 5  # 畫面上同時最多敵人數
enemies = []  # 敵人列表

# 預先生成 ENEMY_MAX 數量的敵人，並分散在畫面上方不同位置
for _ in range(ENEMY_MAX):
    x = random.randint(0, bg_x - enemy_w)
    y = -enemy_h - random.randint(0, bg_y)
    enemies.append(
        Enemy(x, y, enemy_w, enemy_h, enemy_speed, enemy_images, explode_imgs)
    )


def spawn_enemy():
    """
    隨機生成一個敵人，出現在畫面上方隨機位置，並隨機選擇一種外觀
    """
    x = random.randint(0, bg_x - enemy_w)
    y = -enemy_h
    return Enemy(x, y, enemy_w, enemy_h, enemy_speed, enemy_images, explode_imgs)


###################### 飛彈連發功能區塊 ######################
# 步驟6：實現飛彈連發功能
# 1. 設定最大飛彈數量
MISSILE_MAX = 10  # 同時最多10顆飛彈
# 2. 建立飛彈物件列表，每個物件皆為 Missile 實例
missiles = [
    Missile(missile_w, missile_h, missile_speed, missile_img)
    for _ in range(MISSILE_MAX)
]
# 3. 設定飛彈冷卻時間
msl_cooldown = 0
msl_cooldown_max = 10  # 冷卻時間（單位：幀，數字越小可連發越快）


###################### 主程式區塊 ######################
while True:
    # 控制遊戲速度為每秒 60 幀
    clock.tick(60)

    # 處理事件（關閉視窗、切換全螢幕/視窗模式、發射飛彈）
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_F1:
                # 切換全螢幕
                screen = pygame.display.set_mode((bg_x, bg_y), FULLSCREEN)
            elif event.key == K_ESCAPE:
                # 返回視窗模式
                screen = pygame.display.set_mode((bg_x, bg_y))
            # 移除這裡的 K_SPACE 處理，改用下方持續偵測

    # --- 新增：持續偵測空白鍵是否按下，支援長按連發 ---
    keys = pygame.key.get_pressed()
    if keys[K_SPACE] and msl_cooldown == 0:
        for msl in missiles:
            if not msl.active:
                msl.launch(player.rect.centerx, player.rect.top)
                msl_cooldown = msl_cooldown_max
                break

    # 每幀自動遞減飛彈冷卻時間
    if msl_cooldown > 0:
        msl_cooldown -= 1

    # 更新捲動背景的 Y 座標
    roll_y = (roll_y + 10) % bg_y  # 每次往下捲動 10 像素，超過一張圖高度就循環

    # 更新所有飛彈狀態
    for msl in missiles:
        msl.handle_movement(bg_y)

    # 持續生成敵人：若場上敵人數量小於 ENEMY_MAX，則補足
    while len([e for e in enemies if e.active]) < ENEMY_MAX:
        enemies.append(spawn_enemy())

    # 更新所有敵人狀態
    for enemy in enemies:
        enemy.move(bg_y, bg_x)
        # 檢查所有飛彈與敵人碰撞
        for msl in missiles:
            enemy.check_collision(msl)

    # --- 敵機群系統：每幀更新所有敵機 ---
    for emy in emy_list:
        emy.move(bg_y, bg_x)
        # 檢查所有飛彈與敵機碰撞
        for msl in missiles:
            emy.check_collision(msl)

    # --- 若敵機被消滅或飛出畫面，立即重生 ---
    for emy in emy_list:
        if not emy.active:
            emy.reset(bg_x)

    # 畫出捲動背景
    roll_bg(screen, bg_img, roll_y)

    # 先畫所有飛彈，再畫所有敵機，再畫玩家
    for msl in missiles:
        msl.draw(screen)
    for emy in emy_list:
        emy.draw(screen)
    player.draw(screen)
    player.handle_input(pygame.key.get_pressed(), bg_x, bg_y)

    # 更新畫面顯示
    pygame.display.update()
    pygame.display.update()

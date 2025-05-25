###################### 載入套件區塊 ######################
import pygame  # 遊戲開發主套件
import sys  # 系統相關操作
import os  # 處理檔案路徑
from pygame.locals import *  # 載入 Pygame 常數


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
        self.sprites = sprites if isinstance(sprites, dict) else None
        self.facing_direction = "M"
        if self.sprites:
            for k in self.sprites:
                self.sprites[k] = pygame.transform.scale(
                    self.sprites[k], (width, height)
                )
        # 火焰推進相關屬性
        self.burner_img = None  # 火焰圖片 Surface
        self.burner_w = width // 4  # 火焰寬度為太空船寬度的1/4
        self.burner_h = 0  # 火焰高度
        self.burn_shift = 0  # 火焰上下晃動的位移
        if burner_img:
            # 動態縮放火焰圖片，保持寬高比例
            orig_w, orig_h = burner_img.get_width(), burner_img.get_height()
            self.burner_h = int(self.burner_w * orig_h / orig_w)
            self.burner_img = pygame.transform.scale(
                burner_img, (self.burner_w, self.burner_h)
            )

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
            burner_y = self.rect.bottom - self.burner_h // 2 + (self.burn_shift // 3)
            screen.blit(self.burner_img, (burner_x, burner_y))
        # 畫太空船
        if self.sprites and self.facing_direction in self.sprites:
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
            self.facing_direction = "L"
            moved = True
        if keys[K_RIGHT]:
            self.rect.x += self.speed
            self.facing_direction = "R"
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
        self.rect = pygame.Rect(0, 0, width, height)

    def launch(self, x, y):
        """
        發射飛彈，設定初始位置於玩家中心
        x, y: 發射起點（通常為玩家中心）
        """
        self.rect.centerx = x
        self.rect.bottom = y  # 從玩家頂部發射
        self.active = True

    def handle_movement(self, bg_y):
        """
        處理飛彈移動與邊界檢查
        bg_y: 畫面高度，用於判斷是否飛出畫面
        """
        if self.active:
            self.rect.y += self.speed
            # 若飛彈飛出畫面上方則設為不活躍
            if self.rect.bottom < 0:
                self.active = False

    def draw(self, screen):
        """
        在畫面上繪製飛彈
        """
        if self.active:
            if self.img:
                screen.blit(self.img, self.rect)
            else:
                pygame.draw.rect(screen, (255, 0, 0), self.rect)  # 紅色方塊


###################### 敵人類別區塊 ######################
class Enemy:
    def __init__(self, x, y, width, height, speed, img=None):
        """
        初始化敵人
        x, y: 敵人左上角座標
        width, height: 敵人尺寸
        speed: 敵人移動速度（每幀移動的像素數）
        img: 敵人圖片 Surface，若為None則用顏色方塊
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.img = img
        self.active = True  # 敵人是否存活

    def move(self, bg_y):
        """
        控制敵人自動往下移動
        bg_y: 畫面高度，用於判斷是否超出畫面
        """
        if self.active:
            self.rect.y += self.speed
            # 若敵人超出畫面下方則設為不活躍
            if self.rect.top > bg_y:
                self.active = False

    def draw(self, screen):
        """
        在畫面上繪製敵人
        """
        if self.active:
            if self.img:
                screen.blit(self.img, self.rect)
            else:
                pygame.draw.rect(screen, (255, 128, 0), self.rect)  # 橘色方塊

    def check_collision(self, missile):
        """
        檢查與飛彈的碰撞
        missile: Missile 物件
        若碰撞則敵人消失，飛彈也消失
        """
        if self.active and missile.active and self.rect.colliderect(missile.rect):
            self.active = False
            missile.active = False
            return True
        return False


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
# 載入敵人圖片
try:
    enemy_img = pygame.image.load(os.path.join("image", "enemy.png"))
except Exception as e:
    print(f"載入敵人圖片失敗: {e}")
    enemy_img = None

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
missile = Missile(missile_w, missile_h, missile_speed, missile_img)
# 建立敵人物件
enemy_w = 64
enemy_h = 64
enemy_speed = 8  # 敵人下落速度
enemy = Enemy(
    x=(bg_x - enemy_w) // 2,  # 初始位置在畫面中央上方
    y=-enemy_h,
    width=enemy_w,
    height=enemy_h,
    speed=enemy_speed,
    img=enemy_img,
)

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
            elif event.key == K_SPACE:
                # 空白鍵發射飛彈（若目前沒有飛彈在飛行中）
                if not missile.active:
                    missile.launch(player.rect.centerx, player.rect.top)

    # 更新捲動背景的 Y 座標
    roll_y = (roll_y + 10) % bg_y  # 每次往下捲動 10 像素，超過一張圖高度就循環

    # 更新飛彈狀態
    missile.handle_movement(bg_y)
    # 敵人自動下落
    if not enemy.active:
        # 若敵人消失，重新生成一個敵人，位置隨機
        import random

        enemy.rect.x = random.randint(0, bg_x - enemy_w)
        enemy.rect.y = -enemy_h
        enemy.active = True
    enemy.move(bg_y)

    # 檢查飛彈與敵人碰撞
    enemy.check_collision(missile)

    # 畫出捲動背景
    roll_bg(screen, bg_img, roll_y)

    # 先畫飛彈，再畫敵人，再畫玩家，確保圖層順序
    missile.draw(screen)
    enemy.draw(screen)
    player.draw(screen)

    # 更新畫面顯示
    pygame.display.update()

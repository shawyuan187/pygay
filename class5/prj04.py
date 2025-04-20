######################載入套件######################
import sys
import pygame
import random

######################物件類別######################
pygame.init()


class Platform:
    def __init__(self, x, y):
        """
        初始化平台物件
        x, y: 平台的左上角座標
        """
        self.width = 60  # 平台寬度
        self.height = 10  # 平台高度
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (255, 255, 255)  # 白色平台

    def draw(self, screen):
        """繪製平台"""
        pygame.draw.rect(screen, self.color, self.rect)


class Player:
    def __init__(self, x, y):
        """
        初始化主角物件
        x, y: 主角方塊的左上角座標
        """
        self.width = 30  # 主角寬度
        self.height = 30  # 主角高度
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (0, 255, 0)  # 綠色
        self.speed_x = 5  # 水平移動速度
        self.speed_y = 0  # 垂直移動速度
        self.gravity = 0.5  # 重力加速度
        self.jump_speed = -10  # 跳躍初始速度
        self.is_jumping = False  # 是否正在跳躍

    def move(self, direction, bg_x):
        """
        移動主角並實現穿牆效果
        direction: -1為左移，1為右移
        bg_x: 遊戲視窗寬度
        """
        # 更新水平位置
        self.rect.x += direction * self.speed_x

        # 實現穿牆效果
        if self.rect.right < 0:  # 從左邊穿牆
            self.rect.left = bg_x
        elif self.rect.left > bg_x:  # 從右邊穿牆
            self.rect.right = 0

    def update(self):
        """
        更新主角狀態（重力效果）
        """
        # 更新垂直速度（加入重力效果）
        self.speed_y += self.gravity
        # 更新垂直位置
        self.rect.y += self.speed_y

    def check_platform_collisions(self, platforms):
        """
        檢查是否與平台發生碰撞
        platforms: 平台物件列表
        """
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # 確保只在從上方碰撞時才處理
                if self.rect.bottom >= platform.rect.top and self.speed_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.speed_y = self.jump_speed  # 碰到平台後自動跳躍
                    self.is_jumping = True
                    return True
        return False

    def draw(self, screen):
        """繪製主角"""
        pygame.draw.rect(screen, self.color, self.rect)


######################視窗設定######################
bg_x = 400  # 視窗寬度
bg_y = 600  # 視窗高度
bg_size = (bg_x, bg_y)
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
FPS = pygame.time.Clock()

######################遊戲物件設定######################
# 建立主角
player = Player(x=(bg_x - 30) // 2, y=bg_y - 100)

# 建立平台列表
platforms = []

# 建立玩家腳下的起始平台（確保玩家一開始就有站立點）
start_platform = Platform(
    x=(bg_x - 60) // 2,  # 平台置中（視窗寬度減去平台寬度的一半）
    y=bg_y - 60,  # 位置在玩家腳下
)
platforms.append(start_platform)

# 建立其他靜態平台
for i in range(8):  # 建立8個平台
    platform = Platform(
        x=random.randint(0, bg_x - 60),  # 隨機x座標
        y=bg_y - 160 - i * 60,  # 從起始平台上方開始放置，每個平台間隔60像素
    )
    platforms.append(platform)

######################主程式######################
while True:
    FPS.tick(60)  # 限制遊戲更新率為每秒60次
    screen.fill((0, 0, 0))  # 黑色背景

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    # 鍵盤控制
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  # 按下左方向鍵
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:  # 按下右方向鍵
        player.move(1, bg_x)

    # 更新主角狀態
    player.update()

    # 處理平台碰撞
    player.check_platform_collisions(platforms)

    # 檢查是否掉出畫面
    if player.rect.top > bg_y:
        # 重置主角位置
        player.rect.y = bg_y - 100
        player.speed_y = 0

    # 繪製所有平台
    for platform in platforms:
        platform.draw(screen)

    # 繪製主角
    player.draw(screen)

    pygame.display.update()

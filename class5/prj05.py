######################載入套件######################
import sys
import pygame
import random

######################物件類別######################
pygame.init()


class Platform:
    def __init__(self, x, y):
        """初始化平台"""
        self.width = 60  # 平台寬度
        self.height = 10  # 平台高度
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (255, 255, 255)  # 白色平台
        self.active = True  # 平台是否活躍

    def is_visible(self, view_y):
        """檢查平台是否在視野內"""
        return self.rect.y >= view_y - 50 and self.rect.y <= view_y + 650


class PlatformManager:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.platforms = []
        self.min_gap = 50
        self.max_gap = 90

    def generate_initial_platform(self, player_y):
        """生成初始平台在玩家腳下"""
        start_platform = Platform(
            x=(self.screen_width - 60) // 2, y=player_y + 80  # 平台置中  # 玩家腳下
        )
        self.platforms.append(start_platform)

    def generate_platforms(self, start_y):
        """生成新的一組平台"""
        y = start_y - 60  # 從起始平台上方開始生成
        while y > -200:
            x = random.randint(10, self.screen_width - 70)
            gap = random.randint(self.min_gap, self.max_gap)
            platform = Platform(x, y)
            self.platforms.append(platform)
            y -= gap

    def remove_inactive_platforms(self, bottom_y):
        """移除離開視野的平台"""
        self.platforms = [p for p in self.platforms if p.rect.y < bottom_y]


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
        """改進的碰撞檢測"""
        # 移除上升時不檢測的限制，讓玩家可以一直跳
        for platform in platforms:
            if platform.active and self.rect.colliderect(platform.rect):
                # 只要從上方碰到平台就彈跳
                if self.rect.bottom >= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.speed_y = self.jump_speed  # 設定跳躍速度
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
# 建立遊戲物件
player = Player(x=(bg_x - 30) // 2, y=bg_y - 100)
platform_manager = PlatformManager(bg_x)
platform_manager.generate_initial_platform(player.rect.y)  # 先生成初始平台
platform_manager.generate_platforms(player.rect.y)  # 再生成其他平台

######################主程式######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))

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

    # 檢查碰撞
    player.check_platform_collisions(platform_manager.platforms)

    # 檢查是否需要重新生成平台
    if len(platform_manager.platforms) < 8:
        platform_manager.generate_platforms(bg_y - 200)

    # 移除太低的平台
    platform_manager.remove_inactive_platforms(bg_y + 50)

    # 繪製所有平台
    for platform in platform_manager.platforms:
        if platform.active:  # 只繪製活躍的平台
            pygame.draw.rect(screen, platform.color, platform.rect)

    # 繪製主角
    player.draw(screen)

    pygame.display.update()

######################載入套件######################
import sys
import pygame

######################物件類別######################
pygame.init()


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
        self.speed_y = 0  # 垂直移動速度（為後續跳躍做準備）

    def move(self, direction, bg_x):
        """
        移動主角並實現穿牆效果
        direction: -1為左移，1為右移
        bg_x: 遊戲視窗寬度
        """
        # 更新水平位置
        self.rect.x += direction * self.speed_x

        # 實現穿牆效果（像Doodle Jump一樣）
        if self.rect.right < 0:  # 從左邊穿牆
            self.rect.left = bg_x
        elif self.rect.left > bg_x:  # 從右邊穿牆
            self.rect.right = 0

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

######################角色設定######################
# 將主角放在視窗底部中間
player = Player(
    x=(bg_x - 30) // 2,  # 視窗寬度減去主角寬度的一半
    y=bg_y - 100,  # 離底部有一定距離，為後續跳躍做準備
)

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

    # 鍵盤控制（使用持續按鍵檢測實現更流暢的移動）
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  # 按下左方向鍵
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:  # 按下右方向鍵
        player.move(1, bg_x)

    # 繪製主角
    player.draw(screen)

    # 更新畫面
    pygame.display.update()

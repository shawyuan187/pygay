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

    def draw(self, screen):
        """
        繪製主角
        screen: 要繪製的畫面
        """
        pygame.draw.rect(screen, self.color, self.rect)


######################視窗設定######################
bg_x = 400  # 視窗寬度
bg_y = 600  # 視窗高度
bg_size = (bg_x, bg_y)
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)
FPS = pygame.time.Clock()  # 設定FPS時鐘

######################角色設定######################
# 將主角放在視窗底部中間
player = Player(
    x=(bg_x - 30) // 2,  # 視窗寬度減去主角寬度的一半
    y=bg_y - 60,  # 視窗底部上方一點的位置
)

######################主程式######################
while True:
    FPS.tick(60)  # 限制遊戲更新率為每秒60次

    # 清空畫面
    screen.fill((0, 0, 0))  # 黑色背景

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 關閉視窗事件
            sys.exit()
        elif event.type == pygame.KEYDOWN:  # 按鍵事件
            if event.key == pygame.K_ESCAPE:  # ESC鍵退出遊戲
                sys.exit()

    # 繪製主角
    player.draw(screen)

    # 更新畫面
    pygame.display.update()

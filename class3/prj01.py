######################載入套件######################
import sys
import pygame
import random

######################物件類別######################
pygame.init()


class Brick:
    def __init__(self, x, y, width, height, color):
        """
        初始化磚塊物件\n
        x, y: 磚塊的左上角座標\n
        width, height: 磚塊的寬度和高度\n
        color: 磚塊的顏色\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False  # 是否被擊中

    def draw(self, display_area):
        """
        繪製磚塊\n
        screen: 要繪製的畫面\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)


class Ball:
    def __init__(self, x, y, radius, color):
        """
        初始化球物件\n
        x, y: 球的中心座標\n
        radius: 球的半徑\n
        color: 球的顏色\n
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5  # 球的x速度
        self.speed_y = -5  # 球的y速度
        self.is_moving = False  # 球是否在移動

    def draw(self, display_area):
        """
        繪製球\n
        screen: 要繪製的畫面\n
        """
        pygame.draw.circle(display_area, self.color, (self.x, self.y), self.radius)

    def move(self):
        """
        移動球\n
        """
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y
            # 碰到邊界反彈

    def check_collision(self, bg_x, bg_y, pad, bricks):
        """
        檢查碰撞並反彈
        """
        # 檢查與牆壁碰撞
        if self.x - self.radius < 0 or self.x + self.radius > bg_x:
            self.speed_x = -self.speed_x
        if self.y - self.radius < 0:
            self.speed_y = -self.speed_y
        if self.y + self.radius > bg_y:
            self.is_moving = False

        # 檢查與底板碰撞
        if (
            self.y + self.radius > pad.rect.y
            and self.y + self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        # 檢查與磚塊碰撞
        for brick in bricks:
            if not brick.hit:
                # 這裡需要加入與磚塊的碰撞檢測
                if (
                    self.y - self.radius < brick.rect.y + brick.rect.height
                    and self.y + self.radius > brick.rect.y
                    and self.x + self.radius > brick.rect.x
                    and self.x - self.radius < brick.rect.x + brick.rect.width
                ):
                    brick.hit = True
                    self.speed_y = -self.speed_y


######################定義函式區######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("hit box gay")
screen = pygame.display.set_mode(bg_size)
######################初始化設定######################
FPS = pygame.time.Clock()  # 設定FPS
######################載入圖片######################

######################遊戲視窗設定######################

######################磚塊######################
brick_row = 9
brick_col = 11
brick_w = 58
brick_h = 16
brick_gap = 2
bricks = []
for row in range(brick_row):
    y = row * (brick_h + brick_gap) + 60
    for col in range(brick_col):
        x = col * (brick_w + brick_gap) + 70
        color = (
            random.randint(20, 255),
            random.randint(20, 255),
            random.randint(20, 255),
        )
        brick = Brick(x, y, brick_w, brick_h, color)
        bricks.append(brick)
for col in range(brick_col):
    x = col * (brick_w + brick_gap) + 70
    y = 60
    color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
    brick = Brick(x, y, brick_w, brick_h, color)
    bricks.append(brick)
######################顯示文字設定######################

######################底板設定######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定######################
ball_radius = 10  # 球的半徑
ball_color = (255, 0, 0)  # 球的顏色(紅色)
ball = Ball(
    pad.rect.x + pad.rect.width // 2,
    pad.rect.y - ball_radius,
    ball_radius,
    ball_color,
)  # 建立球物件
######################遊戲結束設定######################

######################主程式######################
while True:
    FPS.tick(50)
    screen.fill((0, 0, 0))  # 清空畫面
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠座標
    pad.rect.x = mos_x - pad.rect.width // 2  # 更新底板位置
    if pad.rect.x < 0:
        pad.rect.x = 0
    if pad.rect.x > bg_x - pad.rect.width:
        pad.rect.x = bg_x - pad.rect.width
    if not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2  # 球的x座標
        ball.y = pad.rect.y - ball.radius  # 球的y座標
    else:
        ball.move()
        ball.check_collision(bg_x, bg_y, pad, bricks)  # 檢查碰撞
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not ball.is_moving:
                ball.is_moving = True  # 開始移動球
    for brick in bricks:
        brick.draw(screen)
    pad.draw(screen)  # 繪製底板
    ball.draw(screen)  # 繪製球
    pygame.display.update()  # 更新畫面

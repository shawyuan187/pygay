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


######################定義函式區######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("hit box gay")
screen = pygame.display.set_mode(bg_size)
######################初始化設定######################

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

######################球設定######################

######################遊戲結束設定######################

######################主程式######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式\
    for brick in bricks:
        brick.draw(screen)
    pygame.display.update()  # 更新畫面

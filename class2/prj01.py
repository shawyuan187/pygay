######################載入套件######################
import sys
import pygame

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
Bricka = Brick(0, 0, 50, 20, (255, 0, 0))  # 磚塊物件
Brickb = Brick(200, 100, 50, 20, (0, 255, 0))  # 磚塊物件
######################顯示文字設定######################

######################底板設定######################

######################球設定######################

######################遊戲結束設定######################

######################主程式######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式
    # Bricka.rect.x =100
    # Bricka.rect.y =100
    # Bricka.rect.width =100
    Bricka.draw(screen)  # 繪製磚塊
    Brickb.draw(screen)  # 繪製磚塊
    pygame.display.update()  # 更新畫面

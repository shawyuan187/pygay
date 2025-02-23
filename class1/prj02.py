######################匯入模組######################
import pygame
import sys

######################初始化######################
pygame.init()
Width = 640
height = 320
######################建立視窗及物件######################
screen = pygame.display.set_mode((Width, height))
pygame.display.set_caption("Pygame")
bg = pygame.Surface((Width, height))
bg.fill((255, 255, 255))  # 填滿白色

######################循環偵測######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("click!")
            print(pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式

    screen.blit(bg, (0, 0))  # 將背景畫到視窗上
    pygame.display.update()  # 更新畫面
    ######################繪製圖形######################
    # circle
    pygame.draw.circle(screen, (0, 0, 255), (320, 160), 50, 0)
    # rect
    pygame.draw.rect(screen, (255, 0, 0), (320, 160, 100, 100), 0)
    # polygon
    pygame.draw.polygon(screen, (0, 255, 0), [(320, 160), (220, 260), (420, 260)], 0)
    # ellipse
    pygame.draw.ellipse(screen, (255, 255, 0), (220, 160, 200, 100), 0)
    # arc
    pygame.draw.arc(screen, (255, 0, 255), (220, 160, 200, 100), 0, 180, 1)
    # line
    pygame.draw.line(screen, (0, 0, 0), (220, 160), (420, 260), 2)

    pygame.display.update()  # 更新畫面

######################匯入模組######################
import pygame
import sys

######################初始化######################
pygame.init()
Width = 640
height = 320
######################建立視窗及物件######################
screen = pygame.display.set_mode((Width, height))  # important
pygame.display.set_caption("Pygame")
bg = pygame.Surface((Width, height))
bg.fill((255, 255, 255))  # 填滿白色

######################循環偵測######################
paint = False
color = (0, 255, 255)
while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("click!")
            print(pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式
            # 主要城市
    if paint:
        pygame.draw.circle(bg, color, (x, y), 10, 0)
    screen.blit(bg, (0, 0))  # 將背景畫到視窗上
    pygame.display.update()  # 更新畫面

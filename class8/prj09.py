######################載入套件######################
import pygame  # 載入 pygame 套件，用於遊戲開發
import sys  # 載入 sys 套件，用於系統相關操作
import random  # 載入 random 套件，用於隨機生成平台


######################全域變數######################
# 遊戲分數系統相關變數
score = 0  # 紀錄當前分數，玩家往上跳躍時會增加
highest_score = 0  # 記錄遊戲中達到的最高分數，用於顯示最佳成績
game_over = False  # 控制遊戲狀態的布林值，True表示遊戲結束
initial_player_y = 0  # 記錄玩家的初始垂直位置，用於計算上升高度和分數


######################物件類別######################
class Player:
    """
    玩家角色類別
    負責處理玩家的移動、跳躍、碰撞等所有相關行為
    包含以下主要功能：
    - 繪製玩家角色
    - 處理水平移動
    - 處理重力效果
    - 處理與平台的碰撞
    """

    def __init__(self, x, y, width, height, color):
        """
        初始化主角\n
        參數說明：
        x, y: 主角的左上角座標，決定初始生成位置\n
        width, height: 主角的寬度和高度，決定碰撞箱大小\n
        color: 主角的顏色，使用RGB格式 (r,g,b)\n

        重要屬性說明：
        - rect: 用於碰撞檢測和繪製的矩形區域
        - speed: 水平移動速度，影響左右移動的快慢
        - velocity_y: 垂直速度，受重力影響會持續改變
        - jump_power: 跳躍力道，決定跳躍高度
        - gravity: 重力加速度，影響下落速度
        - on_platform: 是否站在平台上的狀態檢查
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立主角的矩形區域
        self.color = color
        self.speed = 5  # 設定主角的水平移動速度
        self.velocity_y = 0  # 垂直速度
        self.jump_power = -12  # 跳躍初始力量（負值表示向上）
        self.gravity = 0.5  # 重力加速度
        self.on_platform = False  # 是否站在平台上

    def draw(self, display_area):
        """
        繪製主角\n
        參數說明：
        display_area: pygame的繪圖表面，用於繪製主角\n
        功能：
        - 根據當前rect的位置繪製主角
        - 使用設定的顏色填充主角區域
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        移動主角並處理穿牆效果\n
        direction: 移動方向 (1為右移, -1為左移)\n
        bg_x: 遊戲視窗寬度，用於計算穿牆位置\n
        """
        # 根據方向和速度移動主角
        self.rect.x += direction * self.speed
        # 穿牆功能處理
        if self.rect.right < 0:  # 當主角完全移出左邊界時
            self.rect.left = bg_x  # 從右側重新出現
        elif self.rect.left > bg_x:  # 當主角完全移出右邊界時
            self.rect.right = 0  # 從左側重新出現

    def apply_gravity(self):
        """
        應用重力效果\n
        更新垂直速度和位置\n
        """
        self.velocity_y += self.gravity  # 加入重力加速度
        self.rect.y += self.velocity_y  # 更新垂直位置

    def check_platform_collision(self, platforms):
        """
        檢查與所有平台的碰撞\n
        platforms: 要檢查碰撞的平台物件列表\n
        """
        if self.velocity_y > 0:
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points

            for platform in platforms:
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y

                    # 檢查是否與平台發生碰撞
                    if (
                        test_rect.bottom >= platform.rect.top
                        and test_rect.bottom <= platform.rect.bottom
                        and test_rect.right >= platform.rect.left
                        and test_rect.left <= platform.rect.right
                    ):

                        self.rect.bottom = platform.rect.top

                        # 判斷是否碰到彈簧
                        if platform.has_spring:
                            # 彈簧效果：給予2.5倍的跳躍力量
                            self.velocity_y = self.jump_power * 500
                        else:
                            # 一般平台：標準跳躍力量
                            self.velocity_y = self.jump_power

                        self.on_platform = True
                        return True
        return False


class Platform:
    def __init__(self, x, y, width, height, color):
        """
        初始化平台\n
        x, y: 平台的左上角座標\n
        width, height: 平台的寬度和高度\n
        color: 平台的顏色 (RGB格式)\n
        has_spring: 布林值，表示平台是否有彈簧\n
        spring_height: 彈簧的高度\n
        spring_width: 彈簧的寬度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        # 隨機決定是否生成彈簧（20%機率）
        self.has_spring = random.random() < 0.2
        self.spring_height = 10  # 彈簧高度
        self.spring_width = 20  # 彈簧寬度

    def draw(self, display_area):
        """
        繪製平台\n
        display_area: 繪製平台的目標視窗\n
        如果平台有彈簧，會在平台上方繪製一個黃色的小彈簧\n
        """
        # 繪製平台
        pygame.draw.rect(display_area, self.color, self.rect)

        # 如果有彈簧，繪製黃色彈簧
        if self.has_spring:
            spring_rect = pygame.Rect(
                self.rect.centerx - self.spring_width // 2,  # 讓彈簧在平台中心
                self.rect.top - self.spring_height,  # 彈簧位於平台上方
                self.spring_width,
                self.spring_height,
            )
            pygame.draw.rect(display_area, (255, 255, 0), spring_rect)  # 黃色彈簧


######################初始化設定######################
pygame.init()  # 初始化 pygame
FPS = pygame.time.Clock()  # 創建時鐘物件，用於控制遊戲更新速率

######################遊戲視窗設定######################
bg_x = 400  # 設定視窗寬度
bg_y = 600  # 設定視窗高度
bg_size = (bg_x, bg_y)  # 視窗尺寸元組
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 創建遊戲視窗

######################主角設定######################
player_w = 30  # 主角寬度
player_h = 30  # 主角高度
player_x = (bg_x - player_w) // 2  # 計算主角的初始X座標（置中）
player_y = bg_y - player_h - 50  # 計算主角的初始Y座標（底部上方50像素）
# 創建主角物件，設定為綠色
player = Player(player_x, player_y, player_w, player_h, (0, 255, 0))

######################平台設定######################
platform_w = 60  # 平台寬度
platform_h = 10  # 平台高度
platforms = []  # 建立平台列表
# 創建底部平台，確保玩家不會掉出畫面
platform_x = (bg_x - platform_w) // 2  # 平台X座標（置中）
platform_y = bg_y - platform_h - 10  # 平台Y座標（底部上方10像素）
# 創建平台物件，設定為白色
platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))
platforms.append(platform)

# 隨機生成其他平台
platform_count = random.randint(8, 10) + 10000  # 隨機決定平台數量
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)  # 隨機生成平台的X座標
    y = (bg_y - 100) - (i * 60)  # 確保平台間距60像素
    platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
    platforms.append(platform)


######################字型設定######################
font = pygame.font.Font(
    "C:/Windows/Fonts/msjh.ttc", 24
)  # 設定字型和大小為微軟正黑體24點


######################主程式######################
# 更新相機位置的函式
def update_camera():
    """
    更新相機位置和平台\n
    - 當玩家上升到螢幕的一半高度以上時，固定玩家在螢幕中間\n
    - 將所有平台往下移動，製造出玩家繼續往上的錯覺\n
    - 移除超出畫面底部的平台\n
    - 在上方生成新的平台\n
    """
    global score, initial_player_y  # 使用全域變數
    screen_middle = bg_y // 2  # 螢幕中間的Y座標
    # 如果玩家位置高於螢幕中間，更新相機位置
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        # 計算分數：每上升10像素加1分
        score += int(camera_move / 10)

        # 更新所有平台的位置
        for platform in platforms:
            platform.rect.y += camera_move

        # 移除超出畫面底部的平台
        y_min = bg_y
        for platform in platforms:
            if platform.rect.top > bg_y:
                platforms.remove(platform)
            if platform.rect.top < y_min:
                y_min = platform.rect.top

        # 在上方生成新的平台
        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60  # 確保新平台在最上方
            platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
            platforms.append(platform)


def reset_game():
    """
    重置遊戲狀態\n
    - 重設玩家位置\n
    - 清空並重新生成平台\n
    - 重設分數和遊戲狀態\n
    """
    global score, game_over, platforms, initial_player_y, highest_score

    # 重設玩家位置
    player.rect.x = (bg_x - player_w) // 2
    player.rect.y = bg_y - player_h - 50
    player.velocity_y = 0

    # 清空平台列表
    platforms.clear()

    # 重新生成底部平台
    platform_x = (bg_x - platform_w) // 2
    platform_y = bg_y - platform_h - 10
    platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))
    platforms.append(platform)

    # 重新生成其他平台
    for i in range(platform_count - 1):
        x = random.randint(0, bg_x - platform_w)
        y = (bg_y - 100) - (i * 60)
        platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
        platforms.append(platform)

    # 重設遊戲相關變數
    score = 0
    game_over = False
    initial_player_y = player.rect.y


while True:
    FPS.tick(120)  # 限制遊戲更新率為每秒60幀
    screen.fill((0, 0, 0))  # 用黑色填充畫面背景

    if not game_over:  # 遊戲進行中
        update_camera()  # 更新相機位置和平台

        # 獲取當前按下的按鍵狀態
        keys = pygame.key.get_pressed()

        # 處理左右移動控制
        if keys[pygame.K_LEFT]:  # 當按下左方向鍵
            player.move(-1, bg_x)  # 向左移動
        if keys[pygame.K_RIGHT]:  # 當按下右方向鍵
            player.move(1, bg_x)  # 向右移動

        # 應用重力效果和處理碰撞
        player.apply_gravity()
        player.check_platform_collision(platforms)

        # 檢查遊戲結束條件（玩家掉出畫面）
        if player.rect.top > bg_y:
            game_over = True
            # 更新最高分數
            if score > highest_score:
                highest_score = score

    # 事件處理迴圈
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 當使用者點擊關閉視窗
            sys.exit()  # 結束程式
        elif event.type == pygame.KEYDOWN and game_over:  # 遊戲結束時按任意鍵重新開始
            reset_game()

    # 繪製所有平台
    for platform in platforms:
        platform.draw(screen)

    player.draw(screen)  # 繪製主角

    # 顯示分數
    score_text = font.render(f"分數: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # 如果遊戲結束，顯示遊戲結束訊息和最高分
    if game_over:
        game_over_text = font.render(
            "遊戲結束！按任意鍵重新開始", True, (255, 255, 255)
        )
        highest_score_text = font.render(
            f"最高分數: {highest_score}", True, (255, 255, 255)
        )
        text_rect = game_over_text.get_rect(center=(bg_x / 2, bg_y / 2))
        score_rect = highest_score_text.get_rect(center=(bg_x / 2, bg_y / 2 + 40))
        screen.blit(game_over_text, text_rect)
        screen.blit(highest_score_text, score_rect)

    pygame.display.update()  # 更新畫面顯示

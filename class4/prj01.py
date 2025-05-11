/######################載入套件######################
import sys
import pygame
import random
import math

######################物件類別######################
pygame.init()


class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        self.color = (255, random.randint(100, 255), 0)
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(2, 8)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.lifetime = random.randint(10, 30)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class HorizontalParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.color = (0, 191, 255)  # 淺藍色
        self.dy = random.uniform(-3, 3)
        self.dx = random.uniform(-2, 2)
        self.lifetime = random.randint(15, 25)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class HealParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(3, 5)
        self.color = (100, 255, 100)  # 亮綠色
        angle = random.uniform(0, 2 * math.pi)
        self.dy = -random.uniform(2, 4)  # 往上飄
        self.dx = math.sin(angle) * 2  # 左右搖擺
        self.lifetime = random.randint(20, 35)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy *= 0.95  # 漸漸減速
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class Brick:
    def __init__(self, x, y, width, height, color, is_player_pad=False):
        """
        初始化磚塊物件\n
        x, y: 磚塊的左上角座標\n
        width, height: 磚塊的寬度和高度\n
        color: 磚塊的顏色\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False  # 是否被擊中

        # 如果是玩家板子，則不允許成為特殊方塊
        if is_player_pad:
            self.explosive = False
            self.double_score = False
            self.heal = False
            self.horizontal = False
        else:
            self.explosive = random.random() < 0.1  # 10% 機率為爆炸磚塊
            self.horizontal = random.random() < 0.08  # 8% 機率為橫向消除方塊
            self.double_score = (
                random.random() < 0.05 and not self.horizontal
            )  # 5% 機率為分數加倍方塊
            self.heal = (
                random.random() < 0.03 and not self.horizontal
            )  # 3% 機率為回復生命方塊

        if self.explosive:
            self.color = (255, 165, 0)  # 爆炸磚塊顯示為橘色
        elif self.horizontal:
            self.color = (0, 191, 255)  # 橫向方塊顯示為淺藍色
        elif self.double_score:
            self.color = (0, 255, 255)  # 分數加倍方塊顯示為青色
        elif self.heal:
            self.color = (200, 255, 200)  # 回復生命方塊顯示為淺綠色
        self.particles = []

    def trigger_effects(self):
        """觸發磚塊特效"""
        global lives, double_score_timer
        if self.heal and lives < 5:
            lives += 1
            # 產生治癒粒子效果
            for _ in range(15):
                self.particles.append(
                    HealParticle(self.rect.centerx, self.rect.centery)
                )
        if self.double_score:
            double_score_timer = 300

    def explode(self, bricks, screen_shake):
        """觸發爆炸效果"""
        if not self.explosive:
            return

        explosion_range = 100  # 爆炸範圍
        # 產生爆炸粒子
        for _ in range(20):
            self.particles.append(
                ExplosionParticle(self.rect.centerx, self.rect.centery)
            )
        # 設定震動強度和時間
        screen_shake["duration"] = 20
        screen_shake["intensity"] = 10

        for brick in bricks:
            if brick != self and not brick.hit:
                # 計算與其他磚塊的距離
                dx = brick.rect.centerx - self.rect.centerx
                dy = brick.rect.centery - self.rect.centery
                distance = (dx**2 + dy**2) ** 0.5

                # 在爆炸範圍內的磚塊都會被摧毀
                if distance < explosion_range:
                    brick.trigger_effects()  # 先觸發特效
                    brick.hit = True
                    global score
                    score += 1  # 被炸掉的方塊也要加分

    def trigger_horizontal_clear(self, bricks, screen_shake):
        """觸發橫向清除效果"""
        if not self.horizontal:
            return

        # 設定震動效果
        screen_shake["duration"] = 15
        screen_shake["intensity"] = 5

        # 清除同一行的方塊
        target_y = self.rect.y
        for brick in bricks:
            if not brick.hit and brick.rect.y == target_y:
                # 為每個被消除的方塊產生粒子效果
                for _ in range(10):
                    brick.particles.append(
                        HorizontalParticle(brick.rect.centerx, brick.rect.centery)
                    )
                brick.trigger_effects()
                brick.hit = True
                global score
                score += 1

    def draw(self, display_area):
        """
        繪製磚塊\n
        screen: 要繪製的畫面\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            if self.explosive:
                # 為爆炸磚塊加上標記
                pygame.draw.circle(
                    display_area, (255, 0, 0), (self.rect.centerx, self.rect.centery), 3
                )
            elif self.horizontal:
                # 為橫向方塊加上藍色箭頭標記
                arrow_width = 6
                pygame.draw.polygon(
                    display_area,
                    (0, 0, 255),
                    [
                        (self.rect.centerx - arrow_width, self.rect.centery),
                        (
                            self.rect.centerx + arrow_width,
                            self.rect.centery - arrow_width / 2,
                        ),
                        (
                            self.rect.centerx + arrow_width,
                            self.rect.centery + arrow_width / 2,
                        ),
                    ],
                )
            elif self.heal:
                # 為回復生命方塊加上綠點標記
                pygame.draw.circle(
                    display_area, (0, 255, 0), (self.rect.centerx, self.rect.centery), 3
                )
        # 繪製爆炸粒子
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(display_area)


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

    def check_collision(self, bg_x, bg_y, pad, bricks, screen_shake):
        """
        檢查碰撞並反彈
        """
        global score, lives, double_score_timer, game_over
        # 檢查與牆壁碰撞
        if self.x - self.radius < 0 or self.x + self.radius > bg_x:
            self.speed_x = -self.speed_x
        if self.y - self.radius < 0:
            self.speed_y = -self.speed_y
        if self.y + self.radius > bg_y:
            self.is_moving = False
            lives -= 1  # 扣除生命值
            if lives <= 0:
                game_over = True
            return

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
                    # 根據分數加倍狀態計算分數
                    points = 2 if double_score_timer > 0 else 1
                    score += points

                    brick.trigger_effects()  # 使用新的特效觸發函數
                    if brick.horizontal:
                        brick.trigger_horizontal_clear(bricks, screen_shake)
                    if brick.explosive:
                        brick.explode(bricks, screen_shake)
                    self.speed_y = -self.speed_y


######################定義函式區##########################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("hit box gay")
screen = pygame.display.set_mode(bg_size)

######################初始化設定######################
# 加入全域變數
max_explosive = 5  # 最大爆炸磚塊數量
FPS = pygame.time.Clock()
score = 0
font = pygame.font.Font(None, 36)
lives = 5
double_score_timer = 0
game_over = False
game_won = False


def reset_game():
    """重置遊戲狀態"""
    global score, lives, game_over, game_won, double_score_timer, bricks
    score = 0
    lives = 5
    game_over = False
    game_won = False
    double_score_timer = 0

    # 重置磚塊
    bricks.clear()
    explosive_count = 0
    # 重建磚塊
    for row in range(brick_row):
        y = row * (brick_h + brick_gap) + 60
        for col in range(brick_col):
            x = col * (brick_w + brick_gap) + 70
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255),
            )
            brick = Brick(x, y, brick_w, brick_h, color)
            bricks.append(brick)

    # 重置球的位置和狀態
    ball.is_moving = False
    ball.x = pad.rect.x + pad.rect.width // 2
    ball.y = pad.rect.y - ball.radius


def check_win_condition(bricks):
    """檢查是否所有方塊都被消除"""
    for brick in bricks:
        if not brick.hit:
            return False
    return True


######################載入圖片######################

######################遊戲視窗設定######################

######################磚塊######################
brick_row = 9
brick_col = 11
brick_w = 58
brick_h = 16
brick_gap = 2
bricks = []

# 先建立所有一般磚塊
for row in range(brick_row):
    y = row * (brick_h + brick_gap) + 60
    for col in range(brick_col):
        x = col * (brick_w + brick_gap) + 70
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )
        brick = Brick(x, y, brick_w, brick_h, color)
        brick.explosive = False  # 先設定為非爆炸磚塊
        bricks.append(brick)

# 最上面一排的磚塊
for col in range(brick_col):
    x = col * (brick_w + brick_gap) + 70
    y = 60
    color = (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255),
    )
    brick = Brick(x, y, brick_w, brick_h, color)
    brick.explosive = False
    bricks.append(brick)

# 隨機選擇5個磚塊成為爆炸磚塊
explosive_bricks = random.sample(bricks, 5)
for brick in explosive_bricks:
    brick.explosive = True
    brick.color = (255, 165, 0)  # 爆炸磚塊顯示為橘色

######################顯示文字設定######################

######################底板設定######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255), is_player_pad=True)
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
# 加入震動效果參數
screen_shake = {"duration": 0, "intensity": 0}

while True:
    if game_over or game_won:
        # 遊戲結束畫面
        temp_surface = screen.copy()
        temp_surface.fill((0, 0, 0))

        if game_won:
            end_text = font.render("Congratulations!", True, (0, 255, 0))
        else:
            end_text = font.render("Game Over!", True, (255, 0, 0))

        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = font.render("Press SPACE to Restart", True, (255, 255, 255))
        quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))

        temp_surface.blit(end_text, (bg_x // 2 - 100, bg_y // 2 - 60))
        temp_surface.blit(final_score_text, (bg_x // 2 - 100, bg_y // 2))
        temp_surface.blit(restart_text, (bg_x // 2 - 150, bg_y // 2 + 40))
        temp_surface.blit(quit_text, (bg_x // 2 - 100, bg_y // 2 + 80))

        screen.blit(temp_surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 重置遊戲
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
        continue

    FPS.tick(80)

    # 計算震動偏移
    shake_offset = (0, 0)
    if screen_shake["duration"] > 0:
        shake_offset = (
            random.randint(-screen_shake["intensity"], screen_shake["intensity"]),
            random.randint(-screen_shake["intensity"], screen_shake["intensity"]),
        )
        screen_shake["duration"] -= 1

    # 建立暫時的繪圖表面
    temp_surface = screen.copy()
    temp_surface.fill((0, 0, 0))

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
        ball.check_collision(bg_x, bg_y, pad, bricks, screen_shake)  # 檢查碰撞

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # 關閉程式
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not ball.is_moving:
                ball.is_moving = True  # 開始移動球

    # 在臨時表面上繪製所有物件
    for brick in bricks:
        brick.draw(temp_surface)
    pad.draw(temp_surface)
    ball.draw(temp_surface)

    # 檢查是否獲勝
    if check_win_condition(bricks):
        game_won = True

    # 更新分數加倍計時器
    if double_score_timer > 0:
        double_score_timer -= 1

    # 顯示生命值和分數
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    double_text = (
        font.render("2X!", True, (0, 255, 255)) if double_score_timer > 0 else None
    )
    temp_surface.blit(lives_text, (10, 10))
    temp_surface.blit(score_text, (10, 40))
    if double_text:
        temp_surface.blit(double_text, (10, 70))

    # 將臨時表面與震動效果一起繪製到主畫面
    screen.blit(temp_surface, shake_offset)

    pygame.display.update()  # 更新畫面

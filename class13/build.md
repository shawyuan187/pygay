# Galaxy Lancer 遊戲說明

## 0. 遊戲引擎需求

- 使用 Pygame 進行遊戲開發

## 遊戲開發步驟

### 步驟 1: 基本遊戲模板與捲動背景

- 建立基本遊戲程式架構，程式碼組織分為七大區塊：
  - 載入套件區塊：引入必要的pygame、sys和os套件，以及pygame.locals中的常數
  - 定義函式區塊：宣告遊戲中使用的自訂函式，包括 `roll_bg()` 函式實現背景捲動效果
  - 初始化設定區塊：
    - 使用`os.chdir(sys.path[0])`切換至程式所在目錄
    - 使用`pygame.init()`初始化pygame
    - 建立時鐘物件控制遊戲速度
  - 載入圖片區塊：載入太空背景圖片 (image/space.png)
  - 遊戲視窗設定區塊：
    - 設定視窗標題為"Galaxy Lancer"
    - 取得背景圖片尺寸作為遊戲視窗大小
    - 初始化捲動背景所需變數 `roll_y = 0`
  - 玩家設定區塊：設定玩家初始狀態和相關變數
  - 主程式區塊：包含遊戲主迴圈
- 實現捲動背景功能：
  - 捲動邏輯：
    - 持續更新 `roll_y` 變數 (每次增加 10 像素)
    - 使用模運算確保無縫循環 `roll_y = (roll_y + 10) % bg_y`
    - 在上下兩部分繪製背景圖片實現連續捲動
- 提供基本遊戲迴圈功能：
  - 使用`clock.tick(60)`設定時鐘頻率為每秒30幀
  - 實現退出遊戲功能 (按X關閉視窗)
  - 提供按鍵事件處理：
    - F1鍵切換至全螢幕模式
    - ESC鍵返回視窗模式
  - 使用`pygame.display.update()`更新畫面

### 步驟 2: 加入玩家物件及太空船

- 創建 `Player` 類別管理玩家太空船：
  - 初始化函式 `__init__` 設定：
    - 位置與尺寸 (x, y, width, height)，預設尺寸為 80x80
    - 顏色 (用於測試或無圖片時)
    - 速度 (預設水平移動速度)
    - 太空船圖片 (sprites字典)
  - 設計 `draw` 方法在螢幕上繪製太空船
  - 設計 `handle_input` 方法封裝所有移動相關邏輯：
    - 接收按鍵狀態作為參數
    - 內部處理移動方向計算
    - 自動處理邊界檢測
    - 更新太空船位置
- 載入太空船圖片 (image/fighter_M.png)其他方向的圖片先不載入
- 實現四方向移動控制：
  - 使用上下左右方向鍵控制太空船移動
  - 每次按鍵移動設定的速度值，每次移動 10 像素
- 添加邊界檢測：
  - 在類別內部處理所有邊界檢測邏輯
  - 根據太空船尺寸進行邊界計算
- 太空船初始位置設為畫面中央，尺寸為 80x80
- 簡化主程式結構：
  - 只需獲取按鍵狀態
  - 將按鍵狀態傳給太空船物件處理
  - 保持主迴圈邏輯清晰簡潔

### 步驟 3: 實現轉向效果

- 載入太空船左右轉向圖片 (image/fighter_L.png, image/fighter_R.png)
- 將太空船圖片組織為字典，包含三種狀態：
  - 中間直飛 (image/fighter_M.png)
  - 左轉 (image/fighter_L.png)
  - 右轉 (image/fighter_R.png)
- 增強 `Player` 類別：
  - 添加 `facing_direction` 屬性記錄當前方向狀態
  - 在 `handle_input` 方法中根據移動方向自動更新方向狀態
  - 在 `draw` 方法中根據方向狀態選擇適當的太空船圖片
  - 當按左鍵時顯示左轉圖片
  - 當按右鍵時顯示右轉圖片
  - 其他情況顯示直飛圖片
- 動態計算太空船圖片的尺寸，以適應不同狀態的圖片大小
### 步驟 4: 添加火焰推進效果

- 載入太空船火焰圖片 (image/starship_burner.png)
- 擴展 `Player` 類別：
  - 新增初始化參數 `burner_img`，讓使用者可自訂傳入火焰圖片
  - 在 `__init__` 方法中將 `burner_img` 設為火焰動畫用圖片
  - 添加火焰動畫相關屬性及方法
  - 設定變數 `burn_shift` 控制火焰上下晃動
  - 每幀更新位移值：`burn_shift = (burn_shift + 2) % 12`  # 循環0~11
  - 火焰寬度動態設為太空船寬度的1/4，高度等比例縮放
  - 火焰固定在太空船底部，但有微小的位移變化
- 修改 `Player` 類的 `draw` 方法：
  - 先繪製火焰，再繪製太空船，確保正確的圖層順序
  - 計算火焰與太空船的相對位置關係，並根據太空船寬度動態調整火焰寬度
- 獲取火焰圖片的尺寸以便精確定位

### 步驟 5: 建立飛彈類別

- 創建 `Missile` 類別來管理飛彈：
  - 初始化函式 `__init__` 設定：
    - 位置與尺寸 (x, y, width, height)
    - 速度 (移動速度)
    - 圖片 (飛彈精靈圖片)
    - 狀態 (活躍狀態)
  - 設計 `draw` 方法在螢幕上繪製飛彈
  - 設計 `handle_movement` 方法封裝所有移動相關邏輯：
    - 自動更新位置
    - 處理邊界檢測
    - 控制活躍狀態
  - 設計 `launch` 方法封裝發射邏輯：
    - 設定初始位置（根據玩家「中心點」發射，x=player.rect.centerx, y=player.rect.centery）
    - 設定活躍狀態
    - 重設移動相關參數
- 載入飛彈圖片 (image/bullet.png)
- 簡化主程式發射邏輯：
  - 檢測空白鍵按下
  - 呼叫飛彈的 launch 方法
  - 飛彈物件自行處理後續移動和狀態更新
- 主程式繪圖順序：
  - 先繪製飛彈，再繪製玩家太空船，這樣飛彈會被太空船蓋住底部，看起來像是從太空船身體中間發射出去
### 步驟 6: 實現飛彈連發功能

- 設計飛彈連發機制：
  - 設定飛彈最大同時存在數量常數 `MISSILE_MAX`（如 10），建立一個飛彈物件列表，每個物件皆為 `Missile` 實例。
  - 每次發射時，從飛彈列表中尋找第一個未啟動（`active=False`）的飛彈物件，呼叫其 `launch()` 方法發射，並啟動冷卻計時。
  - 設計飛彈冷卻時間變數 `msl_cooldown`，每次發射後設為最大值 `msl_cooldown_max`，每幀自動遞減，冷卻歸零才能再次發射。
  - 這樣可防止玩家無限連發，並確保同時在畫面上的飛彈數量不超過上限。
- 主程式邏輯：
  - 每幀自動遞減 `msl_cooldown`，確保冷卻機制生效。
  - 處理按鍵事件時，若按下空白鍵且冷卻為零，則遍歷飛彈清單，找到未啟動的飛彈物件進行發射，並重設冷卻。
  - 每幀遍歷飛彈清單，呼叫每個飛彈的 `move()` 方法進行移動，並呼叫 `draw()` 方法繪製所有活躍中的飛彈。
- 這種設計可大幅提升效能，避免頻繁建立/銷毀物件，並讓飛彈發射更流暢自然。
### 步驟 7: 添加敵機類別

- 創建 `Enemy` 類別管理敵機：
  - `__init__` 初始化函式：
    - 位置與尺寸 (x, y, width, height)
    - 速度 (敵機移動速度)
    - 圖片 (img)
    - 以 `pygame.Rect` 建立敵機的矩形區域，方便碰撞與移動管理
  - `move` 方法：
    - 控制敵機垂直向下移動（`self.rect.y += self.speed`）
    - 若敵機超出畫面底部（`self.rect.top > bg_y`），則自動呼叫 `reset()`，將敵機重置到畫面上方隨機位置
  - `reset` 方法：
    - 隨機產生敵機的 X 座標（`random.randint(0, bg_x - self.rect.width)`），Y 座標設為畫面上方外（`-self.rect.height`）
  - `draw` 方法：
    - 若有圖片則繪製圖片，否則以紅色矩形顯示
    - 圖片會根據敵機尺寸自動縮放
- 載入敵機圖片 (image/enemy1.png)
  - 於圖片載入區塊加入：

    ```python
    img_enemy1 = pygame.image.load("image/enemy1.png")
    ```

- 在主程式區塊建立一個敵機物件，初始位置隨機，速度固定，並讓其自動移動與重生：
  - 設定敵機寬高、速度
  - 隨機 X 座標，Y 座標設為畫面上方外
  - 建立敵機物件：

    ```python
    enemy = Enemy(enemy_x, enemy_y, enemy_w, enemy_h, enemy_speed, img_enemy1)
    ```

- 在主程式中呼叫 `enemy.move()` 與 `enemy.draw(screen)` 來更新與繪製敵機
  - 每幀先移動敵機，再繪製敵機
  - 敵機會自動在畫面底部重生，形成無限下落的效果
- 這樣設計可讓敵機持續出現在畫面上，為後續碰撞與分數系統做準備
### 步驟 8: 增加多種敵機類型

- 載入多種敵機圖片：
  - 在圖片載入區塊，載入多張敵機圖片，例如：

    ```python
    img_enemy1 = pygame.image.load("image/enemy1.png")  # 載入敵機圖片1
    img_enemy2 = pygame.image.load("image/enemy2.png")  # 載入敵機圖片2
    ```

  - 建立敵機圖片列表，方便之後隨機選擇：

    ```python
    enemy_images = [img_enemy1, img_enemy2]
    ```

- 修改 `Enemy` 類別，讓每台敵機都能隨機選擇不同圖片：
  - 在 `__init__` 初始化時，將圖片參數改為隨機從 `enemy_images` 選取：

    ```python
    self.img = random.choice(enemy_images)
    ```

  - 在 `reset` 方法中，敵機重生時也隨機選擇一張圖片：

    ```python
    self.img = random.choice(enemy_images)
    ```

- 建立敵機物件時，省略圖片參數，讓 `Enemy` 類別自動隨機選擇圖片：
  - 例如：

    ```python
    enemy = Enemy(enemy_x, enemy_y, enemy_w, enemy_h, enemy_speed)
    ```

- 主程式中，敵機的移動與繪製方式不變：
  - 每幀呼叫 `enemy.move()` 與 `enemy.draw(screen)`，敵機會自動在畫面底部重生並隨機換一種外觀。
- 這樣設計可讓敵機每次出現時都可能是不同造型，讓遊戲畫面更豐富多變。
### 步驟 9: 實現敵機群系統

- 設定敵機數量與屬性：
  - 設定敵機數量常數 `emy_num = 5`，可依需求調整。
  - 設定敵機寬度 `enemy_w = 60`、高度 `enemy_h = 60`、下落速度 `enemy_speed = 5`。
- 建立敵機物件列表：
  - 建立空列表 `emy_list = []` 用於儲存所有敵機物件。
  - 使用 for 迴圈依序建立多個敵機物件：
    - 每個敵機的 x 座標隨機（`random.randint(0, bg_x - enemy_w)`），確保不會超出視窗。
    - y 座標設為 `-enemy_h - random.randint(0, bg_y)`，讓敵機分布於畫面上方外的不同位置，避免同時出現一整排。

- 主程式中敵機群的更新與繪製：
  - 每幀遍歷 `emy_list`，分別呼叫每台敵機的 `move()` 與 `draw(screen)` 方法。
  - 敵機會自動在畫面底部重生，形成無限下落的效果。
- 這樣設計可讓敵機持續出現在畫面上，並且分布隨機，為後續碰撞與分數系統做準備。

### 步驟 10: 添加分數和音效系統

-   設計 `ScoreManager` 類別管理分數系統：

    -   初始化函式設定：
        -   分數變數 `self.score`
        -   顯示字體 `self.font`
        -   顯示位置 `self.pos` 與顏色 `self.color`
    -   方法：
        -   `add_score(value)`: 增加分數
        -   `deduct_score(value)`: 減少分數（不低於 0）
        -   `draw(screen)`: 顯示分數於畫面指定位置
        -   `reset()`: 重設分數
    -   於主程式初始化：
        ```python
        font = pygame.font.Font("C:/Windows/Fonts/msjh.ttc", 32)
        ```
    -   在主程式繪圖階段呼叫 `score_manager.draw(screen)` 顯示分數。

-   設計 `AudioManager` 類別管理音效系統：

    -   初始化函式接收音效物件（如 `hit_sound`）
    -   方法：
        -   `play_hit()`: 播放擊中敵機音效
    -   於主程式初始化：
        ```python
            hit_sound = pygame.mixer.Sound("image/hit.mp3")
        ```

-   整合分數與音效於碰撞管理器：

    -   `CollisionManager` 類別初始化時傳入 `score_manager` 與 `audio_manager`
    -   當子彈擊中敵機時：
        -   呼叫 `score_manager.add_score(10)` 增加分數
        -   呼叫 `audio_manager.play_hit()` 播放音效

-   主程式結構簡化：
    -   分數與音效管理集中於 manager 類別
    -   每幀呼叫 `score_manager.draw(screen)` 顯示分數
    -   撞擊時自動加分與播放音效，主程式邏輯更清晰

#GRAVITY SWITCH - A gravity-flipping platformer with 5 levels

#For sound:
add_library('minim')
minim_player = None
sounds = {}

#CONSTANTS
WIDTH, HEIGHT, TILE = 800, 600, 40
GRAVITY, FLIP_VELOCITY, FALL_ACCEL = 1.8, 12.0, 2.5
MAX_VY, RUN_SPEED, EPS, FPS_TARGET = 18, 4, 2.0, 60
SPEED_BOOST = 7

#Level heights
FLOOR_Y = HEIGHT - TILE * 2
CEILING_Y = TILE * 2
MID_Y = HEIGHT / 2

#Import level data from level_data.py file
from level_data import get_level, get_level_count, ALL_LEVELS

def init_audio():
    global minim_player, sounds
    minim_player = Minim(this)
    #All sounds are from pixabay.com
    sounds['flip'] = minim_player.loadFile("sounds/flip.mp3")
    sounds['fail'] = minim_player.loadFile("sounds/fail.mp3")
    sounds['win'] = minim_player.loadFile("sounds/win.mp3")
    sounds['bgm'] = minim_player.loadFile("sounds/bgm.mp3")
    sounds['menu'] = minim_player.loadFile("sounds/menu.mp3")
    sounds['start'] = minim_player.loadFile("sounds/start.mp3")
    if sounds['bgm']: sounds['bgm'].setGain(-16) #Lower bgm volume

#Handling when each sound should be played:
def stop_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].pause()
        sounds[name].rewind()

def play_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].rewind()
        sounds[name].play()

def loop_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].loop()

def pause_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].pause()

def resume_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].play()

#Scores (per level) - Scores are stored in texts file.
def get_scores_file(level_num):
    return "scores_level" + str(level_num) + ".txt"

def read_highscore(level_num):
    try:
        with open(get_scores_file(level_num), 'r') as f:
            content = f.read().strip()
            if content:
                scores = [int(line) for line in content.split('\n') if line.strip()]
                return max(scores) if scores else 0
    except:
        pass
    return 0

def add_score(level_num, score):
    try:
        with open(get_scores_file(level_num), 'a') as f:
            f.write(str(int(score)) + '\n')
    except:
        pass

game_instance = None

#SPEEDPAD CLASS - Speeds up player character while they are on.
class SpeedPad:
    def __init__(self, px, py, pw):
        self.px, self.py, self.pw = px, py, pw
        self.ph = 8
    
    def check_collision(self, player):
        player_bottom = player.py + player.ph
        player_top = player.py
        if player.px + player.pw > self.px and player.px < self.px + self.pw:
            if player.gravity_dir == 1:
                if abs(player_bottom - self.py) < 5 and player.on_platform:
                    return True
            else:
                if abs(player_top - (self.py + TILE)) < 5 and player.on_platform:
                    return True
        return False
    
    def render_speedpad(self, cam_x):
        screen_x = self.px - cam_x
        if screen_x + self.pw < -50 or screen_x > WIDTH + 50:
            return
        noStroke()
        glow = (sin(frameCount * 0.15) + 1) * 0.3 + 0.4 #using sine since it makes the glow oscillate
        fill(255, 80, 40, 150 * glow)
        rect(screen_x - 2, self.py - 2, self.pw + 4, self.ph + 4)
        fill(255, 120, 60)
        rect(screen_x, self.py, self.pw, self.ph)
        fill(255, 200, 100)
        for i in range(int(self.pw / 20)):
            arrow_x = screen_x + 5 + i * 20
            triangle(arrow_x, self.py + self.ph - 2, arrow_x + 6, self.py + 2, arrow_x + 12, self.py + self.ph - 2)

#GRAVITY ORB CLASS - Collectible that adds +2 flips
class GravityOrb:
    def __init__(self, px, py):
        self.px, self.py = px, py
        self.radius = 18
        self.collected = False
        self.pulse_offset = random(TWO_PI) #random start for glow animation. using two pi since its a full sine oscillation cycle.
    
    def check_collision(self, player):
        if self.collected:
            return False
        cx, cy = self.px, self.py
        player_cx = player.px + player.pw / 2
        player_cy = player.py + player.ph / 2
        dist = sqrt((player_cx - cx) ** 2 + (player_cy - cy) ** 2)
        return dist < self.radius + 15
    
    def render_orb(self, cam_x):
        if self.collected:
            return
        screen_x = self.px - cam_x
        if screen_x < -50 or screen_x > WIDTH + 50:
            return
        
        pulse = (sin(frameCount * 0.1 + self.pulse_offset) + 1) * 0.5
        
        noStroke()
        for i in range(3, 0, -1):
            glow_size = self.radius + i * 8 + pulse * 6
            fill(100, 200, 255, 30 - i * 8)
            ellipse(screen_x, self.py, glow_size * 2, glow_size * 2)
        
        #Core orb
        fill(150, 220, 255, 220)
        ellipse(screen_x, self.py, self.radius * 2, self.radius * 2)
        
        #Inner highlight
        fill(200, 240, 255, 250)
        ellipse(screen_x - 4, self.py - 4, self.radius * 0.8, self.radius * 0.8)
        
        #+2 indicator
        fill(255); textSize(12); textAlign(CENTER, CENTER)
        text("+2", screen_x, self.py + self.radius + 12)

#PLATFORM CLASS
class Platform:
    def __init__(self, px, py, pw, ph, move_axis=None, move_range=0, speed=0):
        self.px, self.py, self.pw, self.ph = px, py, pw, ph
        self.is_small_pad = pw <= TILE * 2
        self.move_axis, self.move_range, self.speed = move_axis, move_range, speed
        self.start_x, self.start_y = px, py
        self.move_offset, self.move_dir = 0, 1
    
    def update_platform(self):
        if not self.move_axis:
            return
        self.move_offset += self.speed * self.move_dir
        if abs(self.move_offset) >= self.move_range:
            self.move_dir *= -1
        if self.move_axis == 'x':
            self.px = self.start_x + self.move_offset
        else:
            self.py = self.start_y + self.move_offset
    
    def render_platform(self, cam_x):
        screen_x = self.px - cam_x
        if screen_x + self.pw < -50 or screen_x > WIDTH + 50:
            return #doesn't draw platform if its off-screen, optimization.
        noStroke()
        if self.move_axis: #for the moving platforms
            fill(40, 35, 25, 80); rect(screen_x + 4, self.py + 4, self.pw, self.ph)
            fill(180, 150, 80); rect(screen_x, self.py, self.pw, self.ph)
            fill(220, 190, 100); rect(screen_x, self.py, self.pw, 4)
            fill(140, 110, 60); rect(screen_x, self.py + self.ph - 3, self.pw, 3)
        else: #for the static platforms
            fill(30, 30, 50, 80); rect(screen_x + 4, self.py + 4, self.pw, self.ph)
            fill(60, 70, 90); rect(screen_x, self.py, self.pw, self.ph)
            fill(100, 120, 150); rect(screen_x, self.py, self.pw, 4)
            fill(40, 50, 70); rect(screen_x, self.py + self.ph - 3, self.pw, 3)
    
    def get_rect(self):
        return (self.px, self.py, self.pw, self.ph)

#PLAYER CLASS
class Player:
    def __init__(self, start_x, start_y, max_flips):
        self.px, self.py = float(start_x), float(start_y)
        self.pw, self.ph = 24, 32
        self.vx, self.vy = RUN_SPEED, 0.0
        self.gravity_dir = 1
        self.on_platform = False
        self.flip_count = 0
        self.flips_remaining = max_flips
        self.max_flips = max_flips
        self.squash, self.rotation_anim = 1.0, 0.0 #visual effects for flipping
        self.distance_traveled = 0.0
        self.alive = True
        self.on_speed_pad = False
    
    def request_flip(self):
        #flip only works when grounded.
        if self.on_platform and self.alive and self.flips_remaining > 0:
            self.gravity_dir *= -1
            self.vy = FLIP_VELOCITY * self.gravity_dir #extra launch velocity
            self.flip_count += 1
            self.flips_remaining -= 1
            self.squash = 0.6 #squash effect when flipping
            self.rotation_anim = PI * 0.5 * (-self.gravity_dir)
            return True
        return False
    
    def update_player(self, platforms, speed_pads):
        if not self.alive:
            return #physics update each frame
        
        self.on_speed_pad = False
        for pad in speed_pads:
            if pad.check_collision(self):
                self.on_speed_pad = True
                break
        
        current_speed = SPEED_BOOST if self.on_speed_pad else RUN_SPEED
        
        #Faster acceleration for gravity
        is_falling = (self.vy * self.gravity_dir) > 0
        accel = (GRAVITY + FALL_ACCEL) if is_falling else GRAVITY
        self.vy += accel * self.gravity_dir
        self.vy = constrain(self.vy, -MAX_VY, MAX_VY)
        
        self.px += current_speed #auto-run horizontally
        self.distance_traveled = self.px
        
        was_on_platform = self.on_platform
        self.on_platform = False
        next_y = self.py + self.vy
        
        for plat in platforms:
            prect = plat.get_rect()
            #check horizontal overlap
            if self.px + self.pw > prect[0] and self.px < prect[0] + prect[2]:
                if self.gravity_dir == 1:
                    player_bottom, plat_top = next_y + self.ph, prect[1]
                    if self.vy >= 0 and self.py + self.ph <= plat_top + EPS:
                        if player_bottom >= plat_top - EPS and player_bottom <= plat_top + prect[3]:
                            next_y, self.vy, self.on_platform = plat_top - self.ph, 0, True
                elif self.gravity_dir == -1:
                    player_top, plat_bottom = next_y, prect[1] + prect[3]
                    if self.vy <= 0 and self.py >= plat_bottom - EPS:
                        if player_top <= plat_bottom + EPS and player_top >= prect[1]:
                            next_y, self.vy, self.on_platform = plat_bottom, 0, True
        
        self.py = next_y
        self.squash = lerp(self.squash, 1.0, 0.15) #lerp is used for calculating values at a certain percentage between two given values
        self.rotation_anim = lerp(self.rotation_anim, 0.0, 0.1)
        
        if self.py > HEIGHT + 200 or self.py < -200:
            self.alive = False #Death check
        
        return not was_on_platform and self.on_platform
    
    def render_player(self, cam_x):
        screen_x = self.px - cam_x
        pushMatrix()
        translate(screen_x + self.pw / 2, self.py + self.ph / 2)
        rotate(self.rotation_anim)
        scale(1.0 / self.squash, self.squash)
        noStroke()
        
        #Glow effect when on speed pad
        if self.on_speed_pad:
            fill(255, 120, 60, 100)
        else:
            fill(180, 120, 200, 60)
        rectMode(CENTER); rect(0, 0, self.pw + 8, self.ph + 8, 6)
        fill(220, 180, 230); rect(0, 0, self.pw, self.ph, 4)
        fill(255, 240, 255); rect(0, -self.ph * 0.15 * self.gravity_dir, self.pw * 0.6, self.ph * 0.3, 2)
        fill(80, 60, 100)
        eye_y = -4 * self.gravity_dir
        ellipse(-4, eye_y, 5, 5); ellipse(4, eye_y, 5, 5)
        rectMode(CORNER)
        popMatrix()
        
        fill(100, 255, 100, 150) if self.on_platform else fill(255, 100, 100, 150)
        ellipse(screen_x + self.pw / 2, self.py - 10 * self.gravity_dir, 8, 8)

#UI CLASS
class UI:
    def __init__(self):
        self.messages = []
    
    def add_message(self, msg, duration=120):
        self.messages.append({'msg': msg, 'life': duration})
    
    def update_ui(self):
        #Remove expired messages
        self.messages = [m for m in self.messages if m['life'] > 0]
        for m in self.messages:
            m['life'] -= 1
    
    def render_hud(self, player, paused, level_num, level_name, highscore=0):
        noStroke(); fill(20, 20, 40, 180); rect(10, 10, 220, 95, 8)
        fill(255); textSize(14); textAlign(LEFT, TOP)
        text("Level " + str(level_num) + ": " + level_name, 20, 20)
        text("Distance: " + str(int(player.distance_traveled)), 20, 40)
        fill(255, 220, 100); text("Best: " + str(highscore), 20, 60)
        fill(255); text("Gravity: " + ("DOWN" if player.gravity_dir == 1 else "UP"), 20, 80)
        
        #Centered flips display
        textAlign(CENTER, TOP)
        flips = player.flips_remaining
        if flips <= 3: flip_col = color(255, 80, 80)
        elif flips <= 6: flip_col = color(255, 180, 80)
        else: flip_col = color(120, 255, 160)
        
        #Shadow/glow effect
        fill(0, 0, 0, 100); textSize(28)
        text(str(flips) + " FLIPS LEFT", WIDTH / 2 + 2, 22)
        fill(flip_col); text(str(flips) + " FLIPS LEFT", WIDTH / 2, 20)
        
        if paused:
            fill(255, 200, 100); textSize(32); textAlign(CENTER, CENTER)
            text("PAUSED", WIDTH / 2, HEIGHT / 2)
            textSize(16); text("Press P to resume", WIDTH / 2, HEIGHT / 2 + 30)
        
        textSize(16); textAlign(CENTER, TOP)
        for i, m in enumerate(self.messages):
            fill(255, 255, 200, min(255, m['life'] * 4))
            text(m['msg'], WIDTH / 2, 140 + i * 24)
    
    
    def render_game_over(self, flips_remaining=1):
        fill(0, 0, 0, 180); rect(0, 0, WIDTH, HEIGHT)
        fill(255, 100, 100); textSize(48); textAlign(CENTER, CENTER)
        text("GAME OVER", WIDTH / 2, HEIGHT / 2 - 40)
        if flips_remaining <= 0:
            fill(150, 220, 255); textSize(18)
            text("Try collecting the gravity orbs!", WIDTH / 2, HEIGHT / 2 + 10)
        fill(255); textSize(20); text("Press R to restart | 0 for menu", WIDTH / 2, HEIGHT / 2 + 50)
    
    def render_victory(self):
        fill(0, 0, 0, 150); rect(0, 0, WIDTH, HEIGHT)
        fill(100, 255, 150); textSize(48); textAlign(CENTER, CENTER)
        text("LEVEL COMPLETE!", WIDTH / 2, HEIGHT / 2 - 30)
        fill(255); textSize(20); text("Press R to replay | 0 for menu", WIDTH / 2, HEIGHT / 2 + 30)

#GAME CLASS
class Game:
    def __init__(self):
        self.platforms, self.speed_pads, self.orbs = [], [], []
        self.player = None
        self.ui = UI()
        self.cam_x = 0.0 #camera position for scrolling
        self.paused = False
        self.level_complete = False
        self.state = "intro"
        self.intro_anim_timer = 0
        self.loading_timer = 0
        self.loading_duration = 60  #1 second at 60fps
        self.selected_level = 1
        self.current_level = 1
        self.level_data = None
        self.highscore = 0
        self._score_saved = False
        self.load_level(1)
    
    def load_level(self, level_num):
        self.current_level = level_num
        self.level_data = get_level(level_num)
        self.highscore = read_highscore(level_num)
        
        level_plats = self.level_data['platforms']
        moving_plats = self.level_data['moving']
        speed_pad_data = self.level_data['speed_pads']
        orb_data = self.level_data.get('orbs', [])
        max_flips = self.level_data['max_flips']
        
        #Static platforms:
        self.platforms = []
        for pdata in level_plats:
            px, py, pw = pdata[0], pdata[1], pdata[2]
            ph = pdata[3] if len(pdata) > 3 else TILE
            self.platforms.append(Platform(px, py, pw, ph))
        for pdata in moving_plats:
            px, py, pw, ph = pdata[0], pdata[1], pdata[2], pdata[3]
            move_axis, move_range, speed = pdata[4], pdata[5], pdata[6]
            self.platforms.append(Platform(px, py, pw, ph, move_axis, move_range, speed))
        
        self.speed_pads = [SpeedPad(p[0], p[1], p[2]) for p in speed_pad_data]
        self.orbs = [GravityOrb(o[0], o[1]) for o in orb_data]
        self.level_plats = level_plats
        
        #spawn player on first plat
        first_plat = level_plats[0]
        self.player = Player(first_plat[0] + 20, first_plat[1] - 34, max_flips)
        self.player.on_platform = True
        self.cam_x, self.level_complete = 0.0, False
    
    def restart_game(self):
        self.highscore = read_highscore(self.current_level)
        self._score_saved = False
        self.load_level(self.current_level)
        self.paused, self.level_complete, self.state = False, False, "playing"
        loop_sound('bgm')
        self.ui.add_message("Game Restarted!")
    
    def start_game(self):
        #Transition to loading state with fade
        self.state = "loading"
        self.loading_timer = 0
        self._score_saved = False
        stop_sound('menu')
        play_sound('start')
        self.load_level(self.selected_level)
    
    def finish_loading(self):
        #Called after loading animation completes
        self.state = "playing"
        loop_sound('bgm')
    
    def save_current_score(self, is_win=False):
        if self._score_saved:
            return
        self._score_saved = True
        current_score = int(self.player.distance_traveled)
        add_score(self.current_level, current_score)
        old_highscore = self.highscore
        self.highscore = read_highscore(self.current_level)
        stop_sound('bgm')
        play_sound('win' if is_win else 'fail')
        if current_score > old_highscore and current_score == self.highscore:
            self.ui.add_message("NEW BEST: " + str(self.highscore) + "!", 180)
    
    def render_intro(self):
        t = self.intro_anim_timer * 0.02
        for i in range(HEIGHT):
            inter = map(i, 0, HEIGHT, 0, 1)
            #Animated gradient - top color shifts with sine waves, blends to dark purple at bottom:
            c = lerpColor(color(70 + sin(t) * 20, 50 + sin(t + 1) * 15, 90 + sin(t + 2) * 20), color(25, 20, 45), inter)
            stroke(c); line(0, i, WIDTH, i)
        self.intro_anim_timer += 1
        
        noStroke(); fill(60, 50, 80, 80); rect(0, HEIGHT - 80, WIDTH, 80)
        textAlign(CENTER, CENTER)
        
        #Title
        for i in range(3, 0, -1):
            fill(180, 120, 220, 30); textSize(56 + i * 3); text("GRAVITY SWITCH", WIDTH / 2, 60)
        fill(255, 240, 255); textSize(56); text("GRAVITY SWITCH", WIDTH / 2, 60)
        fill(180, 160, 200); textSize(16); text("A gravity-flipping platformer", WIDTH / 2, 100)
        
        #Level select box
        noStroke(); fill(40, 30, 60, 220); rect(WIDTH / 2 - 350, 130, 700, 340, 12)
        fill(220, 180, 255); textSize(24); text("SELECT LEVEL", WIDTH / 2, 160)
        
        #Level buttons
        num_levels = get_level_count()
        button_w, button_h = 120, 160
        start_x = WIDTH / 2 - (num_levels * button_w + (num_levels - 1) * 15) / 2
        
        for i in range(num_levels):
            level_num = i + 1
            lvl = ALL_LEVELS[i]
            bx = start_x + i * (button_w + 15)
            by = 200
            
            is_selected = (level_num == self.selected_level)
            is_hovered = (mouseX >= bx and mouseX <= bx + button_w and mouseY >= by and mouseY <= by + button_h)
            
            if is_selected:
                fill(100, 80, 150)
                rect(bx - 4, by - 4, button_w + 8, button_h + 8, 10)
            if is_hovered:
                fill(80, 60, 120)
            else:
                fill(50, 40, 80)
            rect(bx, by, button_w, button_h, 8)
            
            fill(255, 220, 255); textSize(36); textAlign(CENTER, CENTER)
            text(str(level_num), bx + button_w / 2, by + 35)
            
            fill(200, 180, 220); textSize(14)
            text(lvl['name'], bx + button_w / 2, by + 70)
            
            diff = lvl['difficulty']
            if diff == 'Easy': fill(100, 255, 100)
            elif diff == 'Medium': fill(255, 200, 100)
            elif diff == 'Hard': fill(255, 100, 100)
            else: fill(255, 50, 50)
            textSize(12); text(diff, bx + button_w / 2, by + 90)
            
            hs = read_highscore(level_num)
            fill(255, 220, 100); textSize(11)
            text("Best: " + str(hs), bx + button_w / 2, by + 115)
            
            fill(150, 150, 200); textSize(10)
            text("Flips: " + str(lvl['max_flips']), bx + button_w / 2, by + 135)
        
        fill(200, 190, 220); textSize(14); textAlign(CENTER, TOP)
        text("Click a level or press 1-5 to select, then SPACE to start", WIDTH / 2, 380)
        
        fill(40, 30, 60, 200); rect(WIDTH / 2 - 300, 410, 600, 50, 8)
        fill(180, 160, 200); textSize(12); textAlign(CENTER, CENTER)
        text("SPACE/CLICK - Flip  |  R - Restart  |  P - Pause  |  0 - Menu", WIDTH / 2, 425)
        text("Arrow keys or 1-5 to select level", WIDTH / 2, 445)
        
        pulse = (sin(self.intro_anim_timer * 0.08) + 1) * 0.5 #oscillating pulse value
        fill(255, 220, 255, 150 + pulse * 105); textSize(20 + pulse * 3); textAlign(CENTER, CENTER)
        text("Press SPACE to start Level " + str(self.selected_level), WIDTH / 2, HEIGHT - 45)
    
    def render_loading(self):
        #Calculate fade progress (0 to 1)
        progress = self.loading_timer / float(self.loading_duration)
        
        #Background fade to black then reveal
        if progress < 0.5:
            #Fade out - show intro fading to black
            fade_alpha = int(progress * 2 * 255)
            self.render_intro()
            fill(0, 0, 0, fade_alpha)
            rect(0, 0, WIDTH, HEIGHT)
        else:
            #Fade in - show game fading from black
            fade_alpha = int((1 - (progress - 0.5) * 2) * 255)
            self.render_background()
            for plat in self.platforms: plat.render_platform(self.cam_x)
            for pad in self.speed_pads: pad.render_speedpad(self.cam_x)
            for orb in self.orbs: orb.render_orb(self.cam_x)
            if self.player: self.player.render_player(self.cam_x)
            fill(0, 0, 0, fade_alpha)
            rect(0, 0, WIDTH, HEIGHT)
        
        #Loading text with pulse effect
        pulse = (sin(self.loading_timer * 0.2) + 1) * 0.5
        textAlign(CENTER, CENTER)
        fill(255, 255, 255, 200 + pulse * 55); textSize(28 + pulse * 4)
        text("LOADING...", WIDTH / 2, HEIGHT / 2)
        
        #Level name
        fill(180, 160, 220, 180); textSize(18)
        text("Level " + str(self.selected_level) + ": " + self.level_data['name'], WIDTH / 2, HEIGHT / 2 + 40)
        
        #Progress bar
        bar_width = 200
        bar_height = 6
        bar_x = WIDTH / 2 - bar_width / 2
        bar_y = HEIGHT / 2 + 70
        fill(60, 50, 80); rect(bar_x, bar_y, bar_width, bar_height, 3)
        fill(150, 120, 220); rect(bar_x, bar_y, bar_width * progress, bar_height, 3)
    
    def handle_level_select_click(self, mx, my):
        num_levels = get_level_count()
        button_w, button_h = 120, 160
        start_x = WIDTH / 2 - (num_levels * button_w + (num_levels - 1) * 15) / 2
        
        for i in range(num_levels):
            bx = start_x + i * (button_w + 15)
            by = 200
            if mx >= bx and mx <= bx + button_w and my >= by and my <= by + button_h:
                self.selected_level = i + 1
                return True
        return False
    
    
    def handle_input_flip(self):
        if self.paused or not self.player.alive or self.level_complete:
            return
        if self.player.request_flip():
            play_sound('flip'); self.ui.add_message("Flip!", 30)
        else:
            self.ui.add_message("Can't flip mid-air!", 40)
    
    def update_game(self):
        if self.state == "loading":
            self.loading_timer += 1
            if self.loading_timer >= self.loading_duration:
                self.finish_loading()
            return
        if self.state == "intro" or self.paused:
            return
        if not self.player.alive:
            self.save_current_score(is_win=False); return
        if self.level_complete:
            return
        
        for plat in self.platforms:
            plat.update_platform()
        self.player.update_player(self.platforms, self.speed_pads)
        
        #Check orb collisions
        for orb in self.orbs:
            if orb.check_collision(self.player):
                orb.collected = True
                self.player.flips_remaining += 2
                self.ui.add_message("+2 Flips!", 60)
        
        self.cam_x = lerp(self.cam_x, max(0, self.player.px - WIDTH * 0.3), 0.08)
        self.ui.update_ui()
        
        if self.player.px > self.level_plats[-1][0] + self.level_plats[-1][2] * 0.5:
            self.level_complete = True
            self.save_current_score(is_win=True); self.ui.add_message("Level Complete!", 300)
    
    def render_background(self):
        global bg_img, bg_cropped
        if bg_img:
            #Crop to right 2/3 of image (from 1/3 x to end) - do once
            if bg_cropped is None:
                crop_x = bg_img.width / 3
                bg_cropped = bg_img.get(int(crop_x), 0, int(bg_img.width - crop_x), bg_img.height)
            
            #Parallax scrolling - background moves slower than camera
            parallax_speed = 0.3
            img_w = bg_cropped.width
            img_h = bg_cropped.height
            
            #Scale image with zoom
            zoom = 1.8
            scale_factor = (float(HEIGHT) / img_h) * zoom
            scaled_w = int(img_w * scale_factor)
            scaled_h = int(img_h * scale_factor)
            
            #Center vertically when zoomed
            y_offset = (HEIGHT - scaled_h) / 2
            
            #Calculate parallax offset (loops the image)
            offset = (self.cam_x * parallax_speed) % scaled_w
            
            #Darkening the image, original was too bright
            tint(150)
            
            #Draw two copies for seamless looping
            image(bg_cropped, -offset, y_offset, scaled_w, scaled_h)
            image(bg_cropped, -offset + scaled_w, y_offset, scaled_w, scaled_h)
            
            #Reset tint for other elements
            noTint()
        else:
            #Fallback gradient if image fails to load
            for i in range(HEIGHT):
                stroke(lerpColor(color(70, 50, 90), color(30, 25, 50), map(i, 0, HEIGHT, 0, 1)))
                line(0, i, WIDTH, i)
            noStroke()
    
    def render_game(self):
        if self.state == "intro":
            self.render_intro(); return
        if self.state == "loading":
            self.render_loading(); return
        self.render_background()
        for plat in self.platforms: plat.render_platform(self.cam_x)
        for pad in self.speed_pads: pad.render_speedpad(self.cam_x)
        for orb in self.orbs: orb.render_orb(self.cam_x)
        if self.player.alive: self.player.render_player(self.cam_x)
        self.ui.render_hud(self.player, self.paused, self.current_level, self.level_data['name'], self.highscore)
        if not self.player.alive: self.ui.render_game_over(self.player.flips_remaining)
        elif self.level_complete: self.ui.render_victory()

#MAIN FUNCTIONS
bg_img = None
bg_cropped = None

def setup():
    global game_instance, bg_img, bg_cropped
    size(WIDTH, HEIGHT); frameRate(FPS_TARGET)
    bg_img = loadImage("bg.png") #bg based on the game Celeste, found on reddit by user thenhedies
    bg_cropped = None
    init_audio(); game_instance = Game(); loop_sound('menu')

def draw():
    global game_instance
    if game_instance:
        game_instance.update_game(); game_instance.render_game()

def keyPressed():
    global game_instance
    if not game_instance: return
    
    if game_instance.state == "intro":
        if key == ' ' or key == ENTER:
            game_instance.start_game()
        elif key == '1': game_instance.selected_level = 1
        elif key == '2': game_instance.selected_level = 2
        elif key == '3': game_instance.selected_level = 3
        elif key == '4': game_instance.selected_level = 4
        elif key == '5': game_instance.selected_level = 5
        elif keyCode == LEFT and game_instance.selected_level > 1:
            game_instance.selected_level -= 1
        elif keyCode == RIGHT and game_instance.selected_level < get_level_count():
            game_instance.selected_level += 1
        return
    
    if key == ' ': game_instance.handle_input_flip()
    elif key == 'r' or key == 'R': game_instance.restart_game()
    elif key == 'p' or key == 'P':
        game_instance.paused = not game_instance.paused
        pause_sound('bgm') if game_instance.paused else resume_sound('bgm')
    elif key == '0':
        game_instance.state, game_instance.intro_anim_timer = "intro", 0
        stop_sound('bgm'); loop_sound('menu')

def mousePressed():
    global game_instance
    if not game_instance: return
    
    if game_instance.state == "intro":
        if not game_instance.handle_level_select_click(mouseX, mouseY):
            game_instance.start_game()
        return
    
    game_instance.handle_input_flip()

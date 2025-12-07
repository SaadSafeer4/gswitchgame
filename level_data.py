#Level Data for Gravity Switch - 5 levels from easiest to hardest

#Constants (same as main game)
TILE = 40
HEIGHT = 600
FLOOR_Y = HEIGHT - TILE * 2
CEILING_Y = TILE * 2
MID_Y = HEIGHT / 2

LEVEL_1 = {
    'name': 'Tutorial',
    'difficulty': 'Easy',
    'max_flips': 8,
    'platforms': [
        (0, FLOOR_Y, TILE * 10, TILE),
        (TILE * 8, MID_Y, TILE * 6, TILE),
        (TILE * 12, CEILING_Y, TILE * 8, TILE),
        (TILE * 18, MID_Y, TILE * 6, TILE),
        (TILE * 22, FLOOR_Y, TILE * 10, TILE),
        (TILE * 30, MID_Y, TILE * 5, TILE),
        (TILE * 33, CEILING_Y, TILE * 8, TILE),
        (TILE * 39, MID_Y, TILE * 5, TILE),
        (TILE * 42, FLOOR_Y, TILE * 10, TILE),
        #Victory
        (TILE * 51, FLOOR_Y - TILE, TILE * 4, TILE * 2),
    ],
    'moving': [],
    'speed_pads': [],
    'orbs': [],
}

LEVEL_2 = {
    'name': 'First Steps',
    'difficulty': 'Easy',
    'max_flips': 7,
    'platforms': [
        (0, FLOOR_Y, TILE * 8, TILE),
        (TILE * 6, MID_Y, TILE * 5, TILE),
        (TILE * 10, CEILING_Y, TILE * 6, TILE),
        (TILE * 14, MID_Y, TILE * 4, TILE),
        (TILE * 17, FLOOR_Y, TILE * 6, TILE),
        (TILE * 21, MID_Y + TILE, TILE * 3, TILE),
        (TILE * 23, CEILING_Y, TILE * 6, TILE),
        (TILE * 27, MID_Y, TILE * 4, TILE),
        (TILE * 30, FLOOR_Y, TILE * 6, TILE),
        (TILE * 34, MID_Y - TILE, TILE * 3, TILE),
        (TILE * 36, CEILING_Y, TILE * 5, TILE),
        (TILE * 40, MID_Y, TILE * 4, TILE),
        (TILE * 43, FLOOR_Y, TILE * 8, TILE),
        #Victory
        (TILE * 50, FLOOR_Y - TILE, TILE * 4, TILE * 2),
    ],
    'moving': [],
    'speed_pads': [
        (TILE * 31, FLOOR_Y, TILE * 3),
    ],
    'orbs': [],
}

LEVEL_3 = {
    'name': 'Momentum',
    'difficulty': 'Medium',
    'max_flips': 5,
    'platforms': [
        (0, FLOOR_Y, TILE * 6, TILE),
        (TILE * 5, MID_Y, TILE * 4, TILE),
        (TILE * 8, CEILING_Y, TILE * 5, TILE),
        #Gap for moving platform at TILE * 14-17
        (TILE * 18, FLOOR_Y, TILE * 5, TILE),
        (TILE * 22, MID_Y + TILE, TILE * 3, TILE),
        (TILE * 24, CEILING_Y, TILE * 5, TILE),
        (TILE * 28, MID_Y, TILE * 4, TILE),
        (TILE * 31, FLOOR_Y, TILE * 5, TILE),
        #Gap for moving platform at TILE * 37-40
        (TILE * 41, CEILING_Y, TILE * 5, TILE),
        (TILE * 45, MID_Y, TILE * 4, TILE),
        (TILE * 48, FLOOR_Y, TILE * 6, TILE),
        #Victory
        (TILE * 53, FLOOR_Y - TILE, TILE * 4, TILE * 2),
    ],
    'moving': [
        #Moving platform in gap between TILE*13 and TILE*18
        (TILE * 14, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 0.6),
        #Moving platform in gap between TILE*36 and TILE*41
        (TILE * 37, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 0.7),
    ],
    'speed_pads': [
        (TILE * 32, FLOOR_Y, TILE * 3),
    ],
    'orbs': [
        #Orbs placed on platforms - gain +2 flips each
        (TILE * 10 + 95, CEILING_Y + TILE*2 + 50),
        (TILE * 28 , MID_Y + - 25),
    ],
}

LEVEL_4 = {
    'name': 'Velocity',
    'difficulty': 'Hard',
    'max_flips': 6,
    'platforms': [
        (0, FLOOR_Y, TILE * 5, TILE),
        (TILE * 4, MID_Y, TILE * 4, TILE),
        (TILE * 7, CEILING_Y, TILE * 4, TILE),
        #Gap for moving platform at TILE * 12-15
        (TILE * 16, FLOOR_Y, TILE * 4, TILE),
        (TILE * 19, MID_Y - TILE, TILE * 3, TILE),
        (TILE * 21, CEILING_Y, TILE * 4, TILE),
        (TILE * 24, MID_Y, TILE * 3, TILE),
        (TILE * 26, FLOOR_Y, TILE * 4, TILE),
        #Gap for moving platform at TILE * 31-34
        (TILE * 35, CEILING_Y, TILE * 4, TILE),
        (TILE * 38, MID_Y, TILE * 3, TILE),
        (TILE * 40, FLOOR_Y, TILE * 4, TILE),
        (TILE * 43, CEILING_Y, TILE * 4, TILE),  #Ceiling to flip from before gap
        #Gap for moving platform at TILE * 48-51
        (TILE * 52, CEILING_Y, TILE * 3, TILE),
        (TILE * 54, FLOOR_Y, TILE * 5, TILE),
        #Victory
        (TILE * 58, FLOOR_Y - TILE, TILE * 4, TILE * 2),
    ],
    'moving': [
        (TILE * 12, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 0.8),
        (TILE * 31, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 0.9),
        (TILE * 48, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 0.8),  #Vertical movement, reachable from ceiling
    ],
    'speed_pads': [
        (TILE * 17, FLOOR_Y, TILE * 3),
        (TILE * 22, CEILING_Y, TILE * 3),
        (TILE * 27, FLOOR_Y, TILE * 3),
        (TILE * 36, CEILING_Y, TILE * 3),
        (TILE * 41, FLOOR_Y, TILE * 3),
    ],
    'orbs': [
        #Orbs
        (TILE * 23 + 40, CEILING_Y + TILE*4 + 25),
        (TILE * 36 + 60, CEILING_Y + TILE*4 + 25),
    ],
}

LEVEL_5 = {
    'name': 'Expert',
    'difficulty': 'Expert',
    'max_flips': 5,
    'platforms': [
        (0, FLOOR_Y, TILE * 4, TILE),
        (TILE * 3, MID_Y, TILE * 3, TILE),
        (TILE * 5, CEILING_Y, TILE * 4, TILE),
        #Gap for moving platform at TILE * 10-13
        (TILE * 14, FLOOR_Y, TILE * 3, TILE),
        (TILE * 15, MID_Y - TILE, TILE * 2, TILE),
        (TILE * 17, CEILING_Y, TILE * 4, TILE),
        (TILE * 20, MID_Y, TILE * 3, TILE),
        (TILE * 22, FLOOR_Y, TILE * 3, TILE),
        #Gap for moving platform at TILE * 26-29
        (TILE * 30, CEILING_Y, TILE * 4, TILE),
        (TILE * 32, MID_Y, TILE * 2, TILE),
        (TILE * 33, FLOOR_Y, TILE * 3, TILE),
        (TILE * 37, CEILING_Y, TILE * 3, TILE),  #Ceiling before gap
        #Gap for moving platform at TILE * 41-44
        (TILE * 45, FLOOR_Y, TILE * 3, TILE),
        (TILE * 47, CEILING_Y, TILE * 4, TILE),  #Ceiling before last gap
        #Gap for moving platform at TILE * 52-55
        (TILE * 56, FLOOR_Y, TILE * 4, TILE),
        #Victory
        (TILE * 59, FLOOR_Y - TILE, TILE * 4, TILE * 2),
    ],
    'moving': [
        (TILE * 10, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 1.0),
        (TILE * 26, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 1.0),
        (TILE * 40.5, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 1.0),  
        (TILE * 52, MID_Y, TILE * 3, TILE, 'y', TILE * 2, 1.0),
    ],
    'speed_pads': [
        (TILE * 15, FLOOR_Y, TILE * 2),
        (TILE * 18, CEILING_Y, TILE * 2),
        (TILE * 23, FLOOR_Y, TILE * 2),
        (TILE * 31, CEILING_Y, TILE * 2),
        (TILE * 33, FLOOR_Y, TILE * 2),
        (TILE * 46, MID_Y, TILE * 2),
        (TILE * 48, CEILING_Y, TILE * 2),
        (TILE * 57, FLOOR_Y, TILE * 2),
    ],
    'orbs': [
        #Orbs
        (TILE * 16 + 100, MID_Y + TILE + 25),
        (TILE * 33 + 30, FLOOR_Y - 25),
        (TILE * 45 + 60, CEILING_Y + TILE + 25),
    ],
}

ALL_LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5]

def get_level(level_num):
    #Get level data by number (1-5). Returns dict with all level info.
    if level_num < 1 or level_num > len(ALL_LEVELS):
        return ALL_LEVELS[0]
    return ALL_LEVELS[level_num - 1]

def get_level_count():
    return len(ALL_LEVELS) #dynamic function in case we decide to add more levels

import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except:
    print("Warning: Sound system not available")
    sound_enabled = False

# Constants
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 30
FPS = 60
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Game variables
score = 0
high_score = 0
font = pygame.font.SysFont('Arial', 24)
game_over = False
restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

# High score file
high_score_file = "highscore.txt"

# Load high score if file exists
def load_high_score():
    if os.path.exists(high_score_file):
        try:
            with open(high_score_file, "r") as file:
                return int(file.read().strip())
        except:
            return 0
    return 0

# Save high score
def save_high_score(score):
    with open(high_score_file, "w") as file:
        file.write(str(score))

# Load high score at startup
high_score = load_high_score()

# Create simple sounds if sound is enabled
if sound_enabled:
    try:
        # Create a simple chomp sound
        chomp_sound = pygame.mixer.Sound(buffer=bytes([128] * 4000 + [180, 80] * 500))
        chomp_sound.set_volume(0.5)
        
        # Create a simple death sound
        death_sound = pygame.mixer.Sound(buffer=bytes([128] * 1000 + [200, 50] * 1000 + [220, 40] * 1000))
        death_sound.set_volume(0.7)
    except:
        print("Warning: Could not create sound effects")
        sound_enabled = False

# Define the maze layout
# 0 = empty path, 1 = wall, 2 = dot
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 1, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1],
    [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Pacman class with smooth movement
class Pacman:
    def __init__(self):
        # Start at the center of the maze (row 10, col 10)
        self.grid_pos = [10, 10]  # Grid position (row, col)
        self.pixel_pos = [self.grid_pos[1] * GRID_SIZE + GRID_SIZE // 2, 
                         self.grid_pos[0] * GRID_SIZE + GRID_SIZE // 2]  # Pixel position (x, y)
        self.direction = STOP
        self.stored_direction = STOP
        self.able_to_move = True
        self.speed = 2  # Pixels per frame
        self.animation_count = 0
        self.mouth_open = True
        self.target_pixel_pos = self.pixel_pos.copy()
    
    def update(self):
        # Check if we're at a grid position (center of a cell)
        at_grid_pos = (self.pixel_pos[0] % GRID_SIZE == GRID_SIZE // 2 and 
                       self.pixel_pos[1] % GRID_SIZE == GRID_SIZE // 2)
        
        if at_grid_pos:
            # Update grid position
            self.grid_pos[0] = self.pixel_pos[1] // GRID_SIZE
            self.grid_pos[1] = self.pixel_pos[0] // GRID_SIZE
            
            # Collect dot if present
            self.collect_dot()
            
            # Check if we can change direction
            if self.stored_direction != STOP:
                can_move = self.can_move(self.stored_direction)
                if can_move:
                    self.direction = self.stored_direction
                    self.stored_direction = STOP
            
            # Check if we can continue in current direction
            if self.direction != STOP:
                can_move = self.can_move(self.direction)
                if not can_move:
                    self.direction = STOP
        
        # Move in the current direction
        if self.direction != STOP:
            self.pixel_pos[0] += self.direction[0] * self.speed
            self.pixel_pos[1] += self.direction[1] * self.speed
        
        # Animation
        self.animation_count += 1
        if self.animation_count >= 5:
            self.mouth_open = not self.mouth_open
            self.animation_count = 0
    
    def can_move(self, direction):
        # Calculate the next grid position
        next_row = self.grid_pos[0] + direction[1]
        next_col = self.grid_pos[1] + direction[0]
        
        # Check if the next position is within bounds
        if next_row < 0 or next_row >= len(maze) or next_col < 0 or next_col >= len(maze[0]):
            return False
        
        # Check if the next position is a wall
        return maze[next_row][next_col] != 1
    
    def draw(self):
        x, y = self.pixel_pos
        
        if self.mouth_open:
            # Draw Pac-Man with open mouth
            if self.direction == RIGHT or (self.direction == STOP and self.stored_direction == STOP):
                pygame.draw.circle(screen, YELLOW, (x, y), GRID_SIZE // 2)
                pygame.draw.polygon(screen, BLACK, [(x, y), 
                                                   (x + GRID_SIZE // 2, y - GRID_SIZE // 4),
                                                   (x + GRID_SIZE // 2, y + GRID_SIZE // 4)])
            elif self.direction == LEFT:
                pygame.draw.circle(screen, YELLOW, (x, y), GRID_SIZE // 2)
                pygame.draw.polygon(screen, BLACK, [(x, y), 
                                                   (x - GRID_SIZE // 2, y - GRID_SIZE // 4),
                                                   (x - GRID_SIZE // 2, y + GRID_SIZE // 4)])
            elif self.direction == UP:
                pygame.draw.circle(screen, YELLOW, (x, y), GRID_SIZE // 2)
                pygame.draw.polygon(screen, BLACK, [(x, y), 
                                                   (x - GRID_SIZE // 4, y - GRID_SIZE // 2),
                                                   (x + GRID_SIZE // 4, y - GRID_SIZE // 2)])
            elif self.direction == DOWN:
                pygame.draw.circle(screen, YELLOW, (x, y), GRID_SIZE // 2)
                pygame.draw.polygon(screen, BLACK, [(x, y), 
                                                   (x - GRID_SIZE // 4, y + GRID_SIZE // 2),
                                                   (x + GRID_SIZE // 4, y + GRID_SIZE // 2)])
        else:
            # Draw Pac-Man with closed mouth
            pygame.draw.circle(screen, YELLOW, (x, y), GRID_SIZE // 2)

    def collect_dot(self):
        global score, high_score
        if maze[self.grid_pos[0]][self.grid_pos[1]] == 2:
            maze[self.grid_pos[0]][self.grid_pos[1]] = 0
            score += 10
            
            # Update high score if needed
            if score > high_score:
                high_score = score
                save_high_score(high_score)
                
            # Play chomp sound when eating a dot
            if sound_enabled:
                chomp_sound.play()

# Ghost class
class Ghost:
    def __init__(self, row, col, color):
        self.grid_pos = [row, col]
        self.pixel_pos = [col * GRID_SIZE + GRID_SIZE // 2, 
                         row * GRID_SIZE + GRID_SIZE // 2]
        self.color = color
        self.direction = STOP
        self.speed = 1  # Slower than Pacman
        self.possible_directions = [UP, DOWN, LEFT, RIGHT]
        
    def update(self):
        # Check if we're at a grid position (center of a cell)
        at_grid_pos = (self.pixel_pos[0] % GRID_SIZE == GRID_SIZE // 2 and 
                       self.pixel_pos[1] % GRID_SIZE == GRID_SIZE // 2)
        
        if at_grid_pos:
            # Update grid position
            self.grid_pos[0] = self.pixel_pos[1] // GRID_SIZE
            self.grid_pos[1] = self.pixel_pos[0] // GRID_SIZE
            
            # Choose a new random direction at intersections
            valid_directions = []
            for direction in self.possible_directions:
                if self.can_move(direction) and direction != (-self.direction[0], -self.direction[1]):
                    valid_directions.append(direction)
            
            if valid_directions:
                if self.direction in valid_directions and random.random() > 0.3:
                    # 70% chance to continue in the same direction if possible
                    pass
                else:
                    self.direction = random.choice(valid_directions)
            else:
                # If no valid directions, reverse
                self.direction = (-self.direction[0], -self.direction[1])
                if not self.can_move(self.direction):
                    self.direction = STOP
        
        # Move in the current direction
        self.pixel_pos[0] += self.direction[0] * self.speed
        self.pixel_pos[1] += self.direction[1] * self.speed
    
    def can_move(self, direction):
        # Calculate the next grid position
        next_row = self.grid_pos[0] + direction[1]
        next_col = self.grid_pos[1] + direction[0]
        
        # Check if the next position is within bounds
        if next_row < 0 or next_row >= len(maze) or next_col < 0 or next_col >= len(maze[0]):
            return False
        
        # Check if the next position is a wall
        return maze[next_row][next_col] != 1
    
    def draw(self):
        x, y = self.pixel_pos
        
        # Draw ghost body
        pygame.draw.circle(screen, self.color, (x, y), GRID_SIZE // 2)
        
        # Draw the bottom part of the ghost
        rect = pygame.Rect(x - GRID_SIZE // 2, y, GRID_SIZE, GRID_SIZE // 2)
        pygame.draw.rect(screen, self.color, rect)
        
        # Draw eyes
        eye_radius = GRID_SIZE // 8
        pygame.draw.circle(screen, WHITE, (x - GRID_SIZE // 6, y - GRID_SIZE // 6), eye_radius)
        pygame.draw.circle(screen, WHITE, (x + GRID_SIZE // 6, y - GRID_SIZE // 6), eye_radius)
        
        # Draw pupils
        pupil_radius = eye_radius // 2
        pygame.draw.circle(screen, BLACK, (x - GRID_SIZE // 6 + self.direction[0] * 2, 
                                          y - GRID_SIZE // 6 + self.direction[1] * 2), pupil_radius)
        pygame.draw.circle(screen, BLACK, (x + GRID_SIZE // 6 + self.direction[0] * 2, 
                                          y - GRID_SIZE // 6 + self.direction[1] * 2), pupil_radius)
    
    def check_collision(self, pacman):
        # Calculate distance between ghost and pacman
        distance = ((self.pixel_pos[0] - pacman.pixel_pos[0]) ** 2 + 
                   (self.pixel_pos[1] - pacman.pixel_pos[1]) ** 2) ** 0.5
        return distance < GRID_SIZE - 5  # Slightly smaller than grid size for better collision

# Reset the game
def reset_game():
    global score, game_over, pacman, ghosts, maze
    
    # Reset score
    score = 0
    game_over = False
    
    # Reset maze (restore dots)
    maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
        [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
        [1, 2, 2, 1, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    # Reset Pacman
    pacman = Pacman()
    
    # Reset ghosts
    ghosts = [
        Ghost(3, 3, RED),
        Ghost(3, 16, PINK),
        Ghost(16, 3, CYAN),
        Ghost(16, 16, ORANGE)
    ]

# Create game objects
pacman = Pacman()
ghosts = [
    Ghost(3, 3, RED),
    Ghost(3, 16, PINK),
    Ghost(16, 3, CYAN),
    Ghost(16, 16, ORANGE)
]

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pacman.stored_direction = UP
            elif event.key == pygame.K_DOWN:
                pacman.stored_direction = DOWN
            elif event.key == pygame.K_LEFT:
                pacman.stored_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                pacman.stored_direction = RIGHT
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if restart button is clicked when game is over
            if game_over and restart_button_rect.collidepoint(event.pos):
                reset_game()
    
    if not game_over:
        # Update game state
        pacman.update()
        
        # Update ghosts and check for collisions
        for ghost in ghosts:
            ghost.update()
            if ghost.check_collision(pacman):
                game_over = True
                # Play death sound when game over
                if sound_enabled:
                    death_sound.play()
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw maze
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            x = col * GRID_SIZE
            y = row * GRID_SIZE
            
            if maze[row][col] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif maze[row][col] == 2:  # Dot
                pygame.draw.circle(screen, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), GRID_SIZE // 8)
    
    # Draw Pacman
    pacman.draw()
    
    # Draw ghosts
    for ghost in ghosts:
        ghost.draw()
    
    # Draw score and high score
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (10, HEIGHT - 40))
    screen.blit(high_score_text, (WIDTH - 200, HEIGHT - 40))
    
    # Draw game over message and restart button
    if game_over:
        game_over_font = pygame.font.SysFont('Arial', 48)
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)
        
        # Draw restart button
        pygame.draw.rect(screen, GREEN, restart_button_rect)
        restart_text = font.render("Play Again", True, BLACK)
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, restart_text_rect)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit the game
pygame.quit()
sys.exit()

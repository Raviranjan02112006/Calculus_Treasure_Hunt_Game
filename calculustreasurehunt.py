import pygame
import sympy as sp
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_PINK = (255, 182, 193)
FONT = pygame.font.SysFont('Arial', 25)
LARGE_FONT = pygame.font.SysFont('Arial', 35)

TILE_SIZE = 50

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Calculus Treasure Hunt")

# Game Variables
score = 0
health = 3  # Number of lives
current_question = ""
current_answer = ""
answer_options = []
quiz_type = ""
difficulty = ""
timer = 0
selected_option = -1
correct_answers = 0
incorrect_answers = 0
skipped_questions = 0
question_count = 0
MAX_QUESTIONS = 10
submitted = False

player_pos = [3, 3]  # Starting position
map_width, map_height = 12, 12

# Load custom images (replace with your own images)
player_image = pygame.image.load('6785156.jpg')  # Your player's image file
player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))  # Scale to fit the tile size
ground_image = pygame.image.load('tile.jpg')  # Ground tile image
ground_image = pygame.transform.scale(ground_image, (TILE_SIZE, TILE_SIZE))
chest_image = pygame.image.load('treasure_hunt.png')  # Treasure chest image
chest_image = pygame.transform.scale(chest_image, (TILE_SIZE, TILE_SIZE))

# Map Layout (0 = ground, 1 = treasure chest)
game_map = [
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
]

# Add difficulty-specific timers
DIFFICULTY_TIMERS = {"Easy": 45, "Medium": 60, "Hard": 75}

# Function to generate calculus questions
def generate_question(quiz_type, level):
    x = sp.symbols('x')
    if level == "Easy":
        func = sum(random.randint(-5, 5) * x**i for i in range(1, random.randint(2, 3)))
    elif level == "Medium":
        func = sum(random.randint(-5, 5) * x**i for i in range(1, random.randint(2, 4))) + random.choice([sp.sin(x), sp.cos(x), sp.log(x + 1), sp.exp(x)])
    else:  # Hard level
        func = sum(random.randint(-5, 5) * x**i for i in range(1, random.randint(3, 5))) + random.choice([sp.sin(x), sp.cos(x), sp.tan(x), sp.csc(x), sp.sec(x), sp.cot(x), sp.log(x + 1), sp.exp(x)])

    if quiz_type == "Differentiation":
        question = f"Find the derivative: {func}"
        answer = sp.simplify(sp.diff(func, x))
    else:  # Indefinite Integration
        question = f"Find the integral: {func}"
        answer = sp.simplify(sp.integrate(func, x))

    answer_options = [answer]
    while len(answer_options) < 4:
        fake_answer = sp.simplify(sp.diff(func, x) if quiz_type == "Differentiation" else sp.integrate(func, x)) * random.randint(-2, 2)
        if fake_answer not in answer_options:
            answer_options.append(fake_answer)

    random.shuffle(answer_options)
    return question, str(answer), [str(opt) for opt in answer_options]

# Display text function
def display_text(text, x, y, color=BLACK, font=FONT):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

# Draw player and treasure chests on map
def draw_map():
    screen.fill(WHITE)
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            screen.blit(ground_image, (x * TILE_SIZE, y * TILE_SIZE))  # Draw ground
            if tile == 1:
                screen.blit(chest_image, (x * TILE_SIZE, y * TILE_SIZE))  # Draw treasure chests
    screen.blit(player_image, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE))
    # Display score and health in RED color
    display_text(f"Lives: {health}", 10, 10, RED, FONT)
    display_text(f"Score: {score}", 10, 50, RED, FONT)

# Handle player movement and boundaries
def move_player(dx, dy):
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    if 0 <= new_x < map_width and 0 <= new_y < map_height:  # Check boundaries
        player_pos[0] = new_x
        player_pos[1] = new_y

# Function to display question and options with a timer
def display_question_with_timer(question, options, time_left):
    screen.fill(WHITE)  # Clear screen to display question
    display_text(question, 50, 100, BLACK, FONT)  # Show the question
    y_offset = 200  # Starting point for the options
    for idx, option in enumerate(options):
        display_text(f"{idx+1}. {option}", 50, y_offset, BLACK, FONT)
        y_offset += 50  # Move down for the next option
    display_text(f"Time Left: {time_left}s", 50, 400, RED, FONT)  # Display timer
    pygame.display.flip()  # Update the screen to show changes

# Function to handle player's answer with timing
def handle_player_answer_with_timing():
    global score, health, correct_answers, incorrect_answers
    start_time = time.time()
    while time.time() - start_time < timer:  # Use the timer based on difficulty
        remaining_time = timer - int(time.time() - start_time)
        display_question_with_timer(current_question, answer_options, remaining_time)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    selected_option = int(event.key) - pygame.K_1  # Convert key to index
                    if answer_options[selected_option] == current_answer:
                        score += 10  # Increment score for a correct answer
                        correct_answers += 1
                    else:
                        health -= 1  # Deduct health for incorrect answer
                        incorrect_answers += 1
                    return  # Exit function after answer
    # If time runs out:
    health -= 1  # Deduct health for timeout
    incorrect_answers += 1

# Main game loop
def main():
    global health, score, current_question, current_answer, answer_options, quiz_type, difficulty, timer

    # Select study or play option
    study_or_play_page()

    # Select quiz type and difficulty
    start_page()
    difficulty_page()

    # Initialize clock to control frame rate
    clock = pygame.time.Clock()

    # Main game loop
    running = True
    while running:
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_player(-1, 0)
        elif keys[pygame.K_RIGHT]:
            move_player(1, 0)
        elif keys[pygame.K_UP]:
            move_player(0, -1)
        elif keys[pygame.K_DOWN]:
            move_player(0, 1)

        # Check if player is on a treasure chest
        if game_map[player_pos[1]][player_pos[0]] == 1:
            game_map[player_pos[1]][player_pos[0]] = 0  # Remove chest after opening
            current_question, current_answer, answer_options = generate_question(quiz_type, difficulty)
            handle_player_answer_with_timing()  # Display question and handle answer with timing

        # Check if health is 0
        if health <= 0:
            game_over()

        # Display score, health, and other stats on the map
        display_text(f"Score: {score}", 10, 10)
        display_text(f"Lives: {health}", 10, 50)

        # Draw the map and player
        draw_map()

        # Update screen
        pygame.display.flip()

        # Limit the frame rate to 30 FPS for smoother gameplay
        clock.tick(30)

# Game over screen
def game_over():
    screen.fill(WHITE)
    display_text(f"Game Over! Final Score: {score}", 50, 150, RED, LARGE_FONT)
    display_text(f"Correct Answers: {correct_answers}", 50, 250, GREEN, FONT)
    display_text(f"Incorrect Answers: {incorrect_answers}", 50, 300, RED, FONT)
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()
    exit()

# Function to select quiz type
def start_page():
    global quiz_type
    running = True
    while running:
        screen.fill(WHITE)
        display_text("Calculus Treasure Hunt", 150, 100, BLUE, LARGE_FONT)
        display_text("Select Quiz Type:", 50, 200, BLACK)

        diff_button = pygame.Rect(100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, diff_button)
        display_text("Differentiation", 110, 260)

        int_button = pygame.Rect(100, 350, 200, 50)
        pygame.draw.rect(screen, BLUE, int_button)
        display_text("Integration", 110, 360)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if diff_button.collidepoint(x, y):
                    quiz_type = "Differentiation"
                    running = False
                elif int_button.collidepoint(x, y):
                    quiz_type = "Integration"
                    running = False

        pygame.display.flip()

# Function to select difficulty level
def difficulty_page():
    global difficulty, timer
    running = True
    while running:
        screen.fill(WHITE)
        display_text("Select Difficulty:", 150, 150, BLACK, LARGE_FONT)

        easy_button = pygame.Rect(100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, easy_button)
        display_text("Easy (45 sec)", 110, 260)

        medium_button = pygame.Rect(100, 350, 200, 50)
        pygame.draw.rect(screen, BLUE, medium_button)
        display_text("Medium (60 sec)", 110, 360)

        hard_button = pygame.Rect(100, 450, 200, 50)
        pygame.draw.rect(screen, RED, hard_button)
        display_text("Hard (75 sec)", 110, 460)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if easy_button.collidepoint(x, y):
                    difficulty = "Easy"
                    timer = DIFFICULTY_TIMERS[difficulty]
                    running = False
                elif medium_button.collidepoint(x, y):
                    difficulty = "Medium"
                    timer = DIFFICULTY_TIMERS[difficulty]
                    running = False
                elif hard_button.collidepoint(x, y):
                    difficulty = "Hard"
                    timer = DIFFICULTY_TIMERS[difficulty]
                    running = False

        pygame.display.flip()

# Function for study or play option
def study_or_play_page():
    running = True
    while running:
        screen.fill(WHITE)
        display_text("Welcome to Calculus Treasure Hunt", 100, 100, BLUE, LARGE_FONT)
        display_text("Select an option:", 50, 200, BLACK)

        play_button = pygame.Rect(100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, play_button)
        display_text("Play Game", 110, 260)

        study_button = pygame.Rect(100, 350, 200, 50)
        pygame.draw.rect(screen, BLUE, study_button)
        display_text("Study Calculus", 110, 360)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if play_button.collidepoint(x, y):
                    running = False
                elif study_button.collidepoint(x, y):
                    study_calculus_page()
                    running = False

        pygame.display.flip()

# Study page to show formulas
def study_calculus_page():
    running = True
    while running:
        screen.fill(WHITE)
        display_text("Comparative Study: Differential & Integral Calculus", 50, 50, BLACK, LARGE_FONT)
        display_text("Differentiation Formulas:", 50, 150, BLACK, FONT)
        display_text("d/dx (x^n) = n*x^(n-1)", 50, 200, BLACK, FONT)
        display_text("d/dx (sin x) = cos x", 50, 250, BLACK, FONT)
        display_text("d/dx (cos x) = -sin x", 50, 300, BLACK, FONT)
        display_text("d/dx (tan x) = sec^2 x", 50, 350, BLACK, FONT)
        display_text("d/dx (cot x) = -cosec^2 x",50, 400,BLACK,FONT) 
        display_text("d/dx (sec x) = sec x*tan x",50, 450,BLACK,FONT) 
        display_text("d/dx (cosec x) = -cosec x*cot x",50, 500,BLACK,FONT)
        display_text("d/dx (exp x) = exp x",50, 550,BLACK,FONT) 

        display_text("Integral Formulas:", 500, 150, BLACK, FONT)
        display_text("∫ x^n dx = (x^(n+1))/(n+1)", 500, 200, BLACK, FONT)
        display_text("∫ sin x dx = -cos x", 500, 250, BLACK, FONT)
        display_text("∫ cos x dx = sin x", 500, 300, BLACK, FONT)
        display_text("∫ sec^2 x dx = tan x", 500, 350, BLACK, FONT)
        display_text("∫ cosec^2 x dx = -cot x", 500, 400, BLACK, FONT)
        display_text("∫ sec x*tan x dx = sec x", 500, 450, BLACK, FONT)
        display_text("∫ cosec x*cot x dx = -cosec x", 500, 500, BLACK, FONT)
        display_text("∫ exp dx = exp x", 500, 550, BLACK, FONT)

        back_button = pygame.Rect(300, 450, 200, 50)
        pygame.draw.rect(screen, RED, back_button)
        display_text("Back to Menu", 310, 460)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if back_button.collidepoint(x, y):
                    return  # Go back to the main menu

        pygame.display.flip()

# Run the game
if __name__ == "__main__":
    main()

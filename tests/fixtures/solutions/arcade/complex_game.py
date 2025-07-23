import arcade
import random
from typing import List


class Ball:
    def __init__(self, x: float, y: float, radius: float = 10):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-3, 3)
        self.color = arcade.color.WHITE
    
    def update(self, width: int, height: int):
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        if self.x - self.radius <= 0 or self.x + self.radius >= width:
            self.velocity_x *= -1
        
        if self.y - self.radius <= 0 or self.y + self.radius >= height:
            self.velocity_y *= -1
    
    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)


class Paddle:
    def __init__(self, x: float, y: float, width: float = 100, height: float = 20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 5
        self.color = arcade.color.BLUE
    
    def move_left(self, screen_width: int):
        self.x = max(self.width // 2, self.x - self.speed)
    
    def move_right(self, screen_width: int):
        self.x = min(screen_width - self.width // 2, self.x + self.speed)
    
    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.color)


class SimpleGame(arcade.Window):
    def __init__(self, width: int = 800, height: int = 600, title: str = "Simple Game"):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        
        self.balls: List[Ball] = []
        self.paddle: Paddle = None
        self.score = 0
        self.game_over = False
    
    def setup(self):
        self.balls = [
            Ball(400, 300),
            Ball(200, 400),
            Ball(600, 200)
        ]
        self.paddle = Paddle(400, 50)
        self.score = 0
        self.game_over = False
    
    def on_draw(self):
        self.clear()
        
        for ball in self.balls:
            ball.draw()
        
        if self.paddle:
            self.paddle.draw()
        
        arcade.draw_text(f"Score: {self.score}", 10, self.height - 30, 
                        arcade.color.WHITE, 20)
        
        if self.game_over:
            arcade.draw_text("GAME OVER", self.width // 2 - 100, self.height // 2,
                           arcade.color.RED, 36)
    
    def on_update(self, delta_time: float):
        if self.game_over:
            return
        
        for ball in self.balls:
            ball.update(self.width, self.height)
            
            if (ball.y - ball.radius <= self.paddle.y + self.paddle.height // 2 and
                ball.x >= self.paddle.x - self.paddle.width // 2 and
                ball.x <= self.paddle.x + self.paddle.width // 2):
                ball.velocity_y = abs(ball.velocity_y)
                self.score += 10
            
            if ball.y < 0:
                self.game_over = True
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.paddle.move_left(self.width)
        elif key == arcade.key.RIGHT:
            self.paddle.move_right(self.width)
        elif key == arcade.key.SPACE and self.game_over:
            self.setup()
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.balls.append(Ball(x, y))


def main():
    game = SimpleGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
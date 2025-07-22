import arcade


class MyFirstArcadeGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.background_color = arcade.color.TEA_GREEN

    def setup(self):
        pass

    def on_draw(self):
        self.clear()


def main():
    game = MyFirstArcadeGame(800, 600, "Arcade Первый Контакт")
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
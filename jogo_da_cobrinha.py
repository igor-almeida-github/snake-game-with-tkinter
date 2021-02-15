import sys
from os import path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from collections import deque
from random import randint

# pyinstaller cobrinha.py --onefile --add-data "assets;assets"     -> Um único arquivo
# pyinstaller cobrinha.py --add-data "assets;assets"               -> Pasta

MOVE_INCREMENT = 20
MOVES_PER_SECOND = 9
GAME_SPEED = 1000 // MOVES_PER_SECOND

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except (ModuleNotFoundError, ImportError):
    pass


class Snake(tk.Canvas):
    def __init__(self):
        super().__init__(width=600, height=620, background="black", highlightthickness=0)
        self.__snake_positions = deque([(100, 100), (80, 100), (60, 100)])
        self.__food_position = (200, 100)
        self.__direction = "start"
        self.bind_all("<Key>", self.__on_key_press)
        self.__score = 0
        self.__key_block = False
        self.__load_assets()
        self.__create_objects()

    def __load_assets(self):
        try:
            bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
            path_to_snake = path.join(bundle_dir, "assets", "snake.png")

            self.__snake_body_image = Image.open(path_to_snake)
            self.__snake_body = ImageTk.PhotoImage(self.__snake_body_image)

            path_to_food = path.join(bundle_dir, "assets", "food.png")
            self.__food_image = Image.open(path_to_food)
            self.__food = ImageTk.PhotoImage(self.__food_image)
        except IOError as error:
            print(error)
            root.destroy()

    def __create_objects(self):
        self.create_text(
            500, 12, text=f"Pontos: {self.__score}", tag="score", fill="#ffff00", font=("TkDefaultFont", 14)
        )
        for x, y in self.__snake_positions:
            self.create_image(x, y, image=self.__snake_body, tag="snake")
        self.create_image(*self.__food_position, image=self.__food, tag="food")
        self.create_rectangle(7, 27, 593, 613, outline="#525d69")

    def __move_snake(self):
        head_x_position, head_y_position = self.__snake_positions[0]
        new_head_position = ()
        self.__key_block = False
        if self.__direction == "Right":
            new_head_position = (head_x_position + MOVE_INCREMENT, head_y_position)
        elif self.__direction == "Left":
            new_head_position = (head_x_position - MOVE_INCREMENT, head_y_position)
        elif self.__direction == "Down":
            new_head_position = (head_x_position, head_y_position + MOVE_INCREMENT)
        elif self.__direction == "Up":
            new_head_position = (head_x_position, head_y_position - MOVE_INCREMENT)

        self.__snake_positions.pop()
        self.__snake_positions.appendleft(new_head_position)
        for segment, position in zip(self.find_withtag("snake"), self.__snake_positions):
            self.coords(segment, position)

    def __perform_actions(self):
        if self.__check_collisions():
            self.__end_game()
            return
        self.__check_food_collision()
        self.__move_snake()
        self.after(GAME_SPEED, self.__perform_actions)

    def __check_collisions(self):
        head_x_position, head_y_position = self.__snake_positions[0]
        return (
            head_x_position in (0, 600) or
            head_y_position in (20, 620) or
            (head_x_position, head_y_position) in list(self.__snake_positions)[1:]
        )

    def __on_key_press(self, e):
        if not self.__key_block:
            new_direction = e.keysym
            if {self.__direction, new_direction} in ({"Left", "Right"}, {"Up", "Down"}):
                return
            elif self.__direction == "start":
                if new_direction in ("Right", "Up", "Down"):
                    self.__direction = new_direction
                    self.__perform_actions()
            elif new_direction in ("Left", "Right", "Up", "Down"):
                self.__key_block = True
                self.__direction = new_direction

    def __check_food_collision(self):
        if self.__snake_positions[0] == self.__food_position:
            self.__snake_positions.appendleft(self.__snake_positions[0])
            self.create_image(*self.__snake_positions[0], image=self.__snake_body, tag="snake")
            self.__score += 1
            score = self.find_withtag("score")
            self.itemconfigure(score, text=f"Pontos: {self.__score}", tag="score")
            self.__set_new_food_position()

    def __set_new_food_position(self):
        while True:
            x_position = randint(1, 29) * MOVE_INCREMENT
            y_position = randint(3, 30) * MOVE_INCREMENT
            food_position = x_position, y_position
            if food_position not in self.__snake_positions:
                self.coords(self.find_withtag("food"), food_position)
                self.__food_position = food_position
                return

    def __end_game(self):
        self.delete(tk.ALL)
        self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            text=f" A felicidade é a pretensão ilusória\n"
                 f"   de converter um instante de\n     alegria em eternidade.\n"
                 f"\n\n                               Game over",
            fill="#ffffff",
            font=("TkDefaultFont", 24)
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background="black")
    root.title("JOGO DA COBRINHA")
    root.minsize(650, 650)
    board = Snake()
    board.pack(fill="none", expand=True)
    root.update()
    root.mainloop()

import tkinter as tk
from PIL import Image,ImageTk
from typing import List

from state import State

class GUI:
    _state: State
    _window: tk.Tk
    _canvas: tk.Canvas
    _tile_size: int
    _board_width: int
    _board_height: int
    _message: tk.Label
    _plus: tk.Button
    _minus: tk.Button
    _board_tiles: List[ImageTk.PhotoImage]

    def __init__(self):
        self._state = State()

        self._window = tk.Tk()
        self._window.title("Carcassonne")
        self._window.geometry()

        self._canvas_width = self._canvas_height = 800
        self._tile_size = 100
        self._canvas_tiles = []
        self._canvas = tk.Canvas(self._window, bd=0, bg="grey", width=self._canvas_width, height=self._canvas_height, relief="raised")
        self._canvas.bind("<Button-1>", self.board_clicked)
        self._canvas.grid(row=0, column=0, columnspan=2)

        self._message = tk.Label(self._window, text=self.message())
        self._message.grid(row=1, column=0, columnspan=2)

        self._plus = tk.Button(self._window, text="+", fg="purple", width=10, command=self.plus_clicked)
        self._plus.grid(row=2, column=0)

        self._minus = tk.Button(self._window, text="-", fg="purple", width=10, command=self.minus_clicked)
        self._minus.grid(row=2, column=1)

        self._img = ImageTk.PhotoImage(Image.open(f"assets/{self._state.next_tile().image_name()}"))
        self._temp = tk.Label(self._window, image=self._img, bg="grey")
        self._temp.grid(row=3, column=0, columnspan=2)
        self._temp.bind("<Button-1>", self.board_clicked)

        for tile in self._state.board():
            self.place_tile(tile._image_name, tile._i, tile._j, tile._rotation)

    def place_tile(self, image_name, i, j, rot):
        img = Image.open(f"assets/{image_name}").resize((self._tile_size, self._tile_size)).rotate(rot)
        x = int(self._canvas_width / 2 + self._tile_size * (i - 0.5))
        y = int(self._canvas_height / 2 + self._tile_size * (-j - 0.5))
        tk_img = ImageTk.PhotoImage(img)
        self._canvas.create_image(x,y,anchor="nw",image=tk_img)
        self._canvas_tiles.append(tk_img)

    def message(self):
        return str(self._state)

    def plus_clicked(self):
        self._canvas_width, self._canvas_height = round(self._canvas_width * 1.1), round(self._canvas_height * 1.1)
        self._canvas.configure(width=self._canvas_width, height=self._canvas_height)

    def minus_clicked(self):
        self._canvas_width, self._canvas_height = round(self._canvas_width / 1.1), round(self._canvas_height / 1.1)
        self._canvas.configure(width=self._canvas_width, height=self._canvas_height)
    
    def board_clicked(self, event: tk.Event):
        print ("clicked at", event.x, event.y)

    def show(self):
        self._window.mainloop()

if __name__ == "__main__":
    GUI().show()
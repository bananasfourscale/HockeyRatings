import tkinter as tk
from tkinter.ttk import *

main_window = tk.Tk()

def get_main_window() -> tk.Tk:
    return main_window

def construct_main_menu(window : tk.Tk=None, ) -> Frame:
    

    return main_menu_frame


if __name__ == "__main__":

    main_window = tk.Tk()
    height=main_window.winfo_screenheight()/2
    width=main_window.winfo_screenwidth()/2
    main_window.geometry('{}x{}'.format(int(width), int(height)))
    construct_main_menu(main_window)
    print(main_window.winfo_children())
    tk.mainloop()
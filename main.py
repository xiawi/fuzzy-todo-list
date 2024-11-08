import tkinter as tk
from tasklist import TaskList
from gui import Gui

def main():
  root = tk.Tk()
  task_list = TaskList()
  app = Gui(root, task_list)
  root.mainloop()

if __name__ == "__main__":
  main()
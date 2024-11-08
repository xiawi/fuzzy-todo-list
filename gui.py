import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import datetime
from task import Task
from priority_scorer import FuzzyPriorityScorer
from tasklist import TaskList

class Gui:
  def __init__(self, root, task_list: TaskList):
    self.task_list = task_list  # Use your existing TaskList class
    self.file_path = None
    self.is_unsaved = False

    self.root = root
    self.root.title("Fuzzy To-do List")
    self.root.grid_rowconfigure(0, weight=1, minsize=100)  # Add this for row resizing
    self.root.grid_columnconfigure(0, weight=1, minsize=200)  # Add this for column resizing

    # Set up frames
    self.frame_top = tk.Frame(self.root)
    self.frame_top.pack(pady=10)
    self.frame_top.grid_rowconfigure(0, weight=1)
    self.frame_top.grid_rowconfigure(1, weight=1)
    self.frame_top.grid_columnconfigure(1, weight=1)
    
    # Task entry form
    tk.Label(self.frame_top, text="Task Name:").grid(row=0, column=0, padx=5)
    self.task_name_entry = tk.Entry(self.frame_top)
    self.task_name_entry.grid(row=0, column=1, padx=5, sticky="ew")
    
    # Importance slider (1 to 10)
    tk.Label(self.frame_top, text="Importance (1-10):").grid(row=1, column=0, padx=5, sticky="w")
    self.importance_slider = tk.Scale(self.frame_top, from_=0, to=10, orient=tk.HORIZONTAL)
    self.importance_slider.set(5)  # Set the default value to 5
    self.importance_slider.grid(row=1, column=1, padx=5, sticky="ew")
    
    # Checkbox for deadline existence
    self.deadline_exists = tk.BooleanVar(value=False)  # Default to No deadline

    self.deadline_checkbox = tk.Checkbutton(self.frame_top, text="Has Deadline", variable=self.deadline_exists, command=self.toggleDeadline)
    self.deadline_checkbox.grid(row=0, column=4, padx=5)

    # Deadline date picker (only visible if the deadline exists)
    self.deadline_picker_label = tk.Label(self.frame_top, text="Select Deadline:")
    self.deadline_picker_label.grid(row=1, column=4, padx=5)

    self.deadline_picker = DateEntry(self.frame_top, date_pattern="yyyy-mm-dd")
    self.deadline_picker.config(mindate=datetime.date.today() + datetime.timedelta(days=1))
    self.deadline_picker.set_date(datetime.date.today() + datetime.timedelta(days=1))
    self.deadline_picker.grid(row=1, column=5, padx=5)
    self.deadline_picker.config(state="disabled")  # Initially disable the date picker

    # Buttons
    self.addTask_button = tk.Button(self.frame_top, text="Add Task", command=self.addTask)
    self.addTask_button.grid(row=0, column=6, padx=5)

    self.save_button = tk.Button(self.frame_top, text="Save", command=self.saveTasks)
    self.save_button.grid(row=0, column=7, padx=5)

    self.load_button = tk.Button(self.frame_top, text="Load", command=self.loadTasks)
    self.load_button.grid(row=1, column=7, padx=5)

    # Task list display
    self.tree = ttk.Treeview(self.root, columns=("Name", "Complete", "Deadline"), show="headings")
    self.tree.heading("Name", text="Task Name")
    self.tree.heading("Complete", text="Status")
    self.tree.heading("Deadline", text="Deadline")

    self.tree.pack(pady=10)
    self.tree.bind("<Double-1>", self.editTask)
    self.tree.pack(fill=tk.BOTH, expand=True)
    self.refreshTaskList()

    # Mark as complete and delete buttons in a horizontal frame
    self.button_frame = tk.Frame(self.root)
    self.button_frame.pack(pady=5)

    self.complete_task_button = tk.Button(self.button_frame, text="Mark as Complete/Incomplete", command=self.toggleComplete)
    self.delete_task_button = tk.Button(self.button_frame, text="Delete Task", command=self.deleteTask)
    self.complete_task_button.pack(side=tk.LEFT, padx=5, fill=tk.X)
    self.delete_task_button.pack(side=tk.LEFT, padx=5, fill=tk.X)


    self.root.protocol("WM_DELETE_WINDOW", self.onClose)

  def addTask(self):
    task_name = self.task_name_entry.get()
    importance = self.importance_slider.get()
    deadline_text = self.deadline_picker.get() if self.deadline_exists.get() else None

    # Validate and add task
    try:
      if not task_name:
        raise ValueError("Task name cannot be empty")
      deadline = datetime.datetime.strptime(deadline_text, "%Y-%m-%d") if deadline_text else None
      task = Task(task_name, importance, deadline)
      self.task_list.addTask(task)
      self.refreshTaskList()
      self.resetEntries()
      self.is_unsaved = True
    except ValueError as e:
      messagebox.showerror("Invalid input", e)

  def resetEntries(self):
    self.task_name_entry.delete(0, tk.END)  # Clear task name entry
    self.importance_slider.set(5)  # Reset importance slider to default value (e.g., 5)
    
    self.deadline_exists.set(False)  # Reset the deadline checkbox to unchecked

    # Reset the deadline picker to today's date if it's enabled
    self.deadline_picker.set_date(datetime.datetime.today() + datetime.timedelta(days=1)) 

    self.toggleDeadline()  # Update the state of the deadline picker (disable it)


  def refreshTaskList(self):
    # Clear the current display
    for row in self.tree.get_children():
        self.tree.delete(row)

    self.task_list.refreshList()

    # Re-populate the tree with sorted tasks
    for i, task in enumerate(self.task_list.tasks):
        status = "Complete" if task.is_complete else "Incomplete"
        deadline = task.deadline.date() if task.deadline else ""
        self.tree.insert("", "end", iid=i, values=(task.task_name, status, deadline))

  def toggleComplete(self):
    selected_item = self.tree.focus()
    if selected_item:
        index = int(selected_item)
        self.task_list.triggerCompletion(index)
        self.refreshTaskList()
        self.is_unsaved = True

  def deleteTask(self):
    selected_item = self.tree.focus()
    if selected_item:
      index = int(selected_item)
      self.task_list.deleteTask(index)
      self.refreshTaskList()
      self.is_unsaved = True

  def saveTasks(self):
    if not self.file_path:
      # Open file dialog if no file path is set
      self.file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
      if not self.file_path:
        return
    try:
      self.task_list.saveToJson(self.file_path)
      self.is_unsaved = False
    except Exception as e:
      messagebox.showerror("Error", f"Failed to save tasks: {e}")


  def loadTasks(self):

    if self.is_unsaved:
      answer = messagebox.askyesnocancel("Quit", "Do you want to save your tasks before exiting?")
      if answer is None:
        return  # User clicked cancel, do nothing
      elif answer:
        self.saveTasks()  # Save tasks if the user clicked 'Yes'

    # Open file dialog to select a JSON file
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])

    if not file_path:
      return
    else:
      self.file_path = file_path
    
    if self.file_path:
      try:
        self.task_list.tasks.clear()
        self.task_list.loadFromJson(self.file_path)  # Load tasks from the selected file
        self.refreshTaskList()
        self.is_unsaved = False
      except Exception as e:
        messagebox.showerror("Error", f"Failed to load tasks: {e}")

  def toggleDeadline(self, *args):
    if self.deadline_exists.get() == 1:  # If deadline exists
      self.deadline_picker.config(state="normal")  # Enable calendar
      self.deadline_picker_label.grid(row=1, column=4, padx=5)
      self.deadline_picker.grid(row=1, column=5, padx=5)
    else:
      self.deadline_picker.config(state="disabled")  # Disable calendar
      self.deadline_picker_label.grid(row=1, column=4, padx=5)  # Keep label visible
      self.deadline_picker.grid(row=1, column=5, padx=5)  # Keep date picker visible

  def onClose(self):
    # Only ask to save if there have been modifications to the task list
    if self.is_unsaved:
      answer = messagebox.askyesnocancel("Quit", "Do you want to save your tasks before exiting?")
      if answer is None:
        return  # User clicked cancel, do nothing
      elif answer:
        self.saveTasks()  # Save tasks if the user clicked 'Yes'
    self.root.quit()  # Close the application

  def editTask(self, event):
    # Get the selected item
    selected_item = self.tree.focus()
    if not selected_item:
        return

    index = int(selected_item)
    task = self.task_list.tasks[index]
    initial_status = task.is_complete

    # Create the pop-up window
    edit_window = tk.Toplevel(self.root)
    edit_window.title("Edit Task")

    # Grab focus for the edit window, deactivating the main window
    edit_window.grab_set()

    # Task Name Entry
    tk.Label(edit_window, text="Task Name:").grid(row=0, column=0, padx=5, pady=5)
    task_name_entry = tk.Entry(edit_window)
    task_name_entry.insert(0, task.task_name)
    task_name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Importance Slider
    tk.Label(edit_window, text="Importance (1-10):").grid(row=1, column=0, padx=5, pady=5)
    importance_slider = tk.Scale(edit_window, from_=1, to=10, orient=tk.HORIZONTAL)
    importance_slider.set(task.importance)
    importance_slider.grid(row=1, column=1, padx=5, pady=5)

    # Deadline Date Picker
    deadline_exists = tk.BooleanVar(value=task.deadline is not None)
    deadline_checkbox = tk.Checkbutton(edit_window, text="Has Deadline", variable=deadline_exists)
    deadline_checkbox.grid(row=2, column=0, padx=5, pady=5)

    deadline_picker_label = tk.Label(edit_window, text="Select Deadline:")
    deadline_picker_label.grid(row=3, column=0, padx=5, pady=5)
    deadline_picker = DateEntry(edit_window, date_pattern="yyyy-mm-dd")
    deadline_picker.config(mindate=datetime.date.today() + datetime.timedelta(days=1))
    deadline_picker.set_date(datetime.date.today() + datetime.timedelta(days=1))

    # Completeness checkbox
    completeness_var = tk.BooleanVar(value=task.is_complete)
    completeness_checkbox = tk.Checkbutton(edit_window, text="Complete", variable=completeness_var)
    completeness_checkbox.grid(row=2, column=1, padx=5, pady=5)

    if task.deadline:
        deadline_picker.set_date(task.deadline.strftime("%Y-%m-%d"))
    deadline_picker.grid(row=3, column=1, padx=5, pady=5)
    deadline_picker.config(state="normal" if deadline_exists.get() else "disabled")

    # Toggle deadline picker visibility based on checkbox
    def toggleDeadline():
      if deadline_exists.get():
        deadline_picker.config(state="normal")
      else:
        deadline_picker.config(state="disabled")
    deadline_checkbox.config(command=toggleDeadline)

    # Save button to update the task
    def saveChanges():
      new_task_name = task_name_entry.get()
      new_importance = importance_slider.get()
      new_deadline = datetime.datetime.strptime(deadline_picker.get(), "%Y-%m-%d") if deadline_exists.get() else None

      if completeness_var.get() != initial_status:
        self.task_list.triggerCompletion(index)

      # Validate input
      if not new_task_name:
        messagebox.showerror("Invalid input", "Task name cannot be empty")
        return

      # Update the task and refresh the list
      task.task_name = new_task_name
      task.importance = new_importance
      task.deadline = new_deadline
      self.refreshTaskList()

      self.is_unsaved = True

      edit_window.destroy()  # Close the pop-up window

    # Cancel button to discard changes
    def cancelChanges():
      edit_window.destroy()

    save_button = tk.Button(edit_window, text="Save", command=saveChanges)
    save_button.grid(row=4, column=0, padx=5, pady=5)

    cancel_button = tk.Button(edit_window, text="Cancel", command=cancelChanges)
    cancel_button.grid(row=4, column=1, padx=5, pady=5)

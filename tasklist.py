from priority_scorer import FuzzyPriorityScorer
from task import Task
import datetime
import json
import math

class TaskList:
    def __init__(self):
        self.priority_scorer = FuzzyPriorityScorer()
        self.tasks = []
        
    def addTask(self, task:Task):
        self.tasks.append(task)
        self.calculateUrgency()
        self.calculatePriority() 
        self.sortTasks()
        
    def deleteTask(self, index):
        self.tasks.pop(index)
        
    def calculateUrgency(self):
        deadlined_tasks = [t for t in self.tasks if t.deadline and not t.is_complete]
        
        if not deadlined_tasks: # return from function if there are no tasks with deadlines (no urgency)
            return
    
        # find task with the closest deadline
        closest_deadline = min(deadlined_tasks, key=lambda t: t.deadline)
        closest_time_diff = (closest_deadline.deadline - datetime.datetime.now()).total_seconds()
        
        for task in self.tasks:
            if task in deadlined_tasks:
                time_diff = (task.deadline - datetime.datetime.now()).total_seconds()
                time_diff = min(time_diff, closest_time_diff * 2)   # to adjust in case time_diff is too large
                task.urgency = round((closest_time_diff / time_diff) * 10, 1)
                
    def triggerCompletion(self, index):
        self.tasks[index].triggerCompletion()
        self.calculatePriority()
        self.sortTasks()
                
    def calculatePriority(self):
        for task in self.tasks:
            if task.is_complete == False:
                task.priority_score = self.priority_scorer.getPriorityScore(task.importance, task.urgency)
                print(task.task_name, task.urgency, task.priority_score)
            else:
                task.priority_score = 0
            
    def sortTasks(self):
        self.tasks = sorted(self.tasks, key=lambda task: task.priority_score, reverse=True)
            
    def saveToJson(self, filename='tasks.json'):
        with open(filename, 'w') as file:
            json.dump([task.toDict() for task in self.tasks], file, indent=4)
            
    def loadFromJson(self, filename='tasks.json'):
        try:
            with open(filename, 'r') as file:
                tasks_data = json.load(file)
                for task_data in tasks_data:
                    deadline = datetime.datetime.fromisoformat(task_data['deadline']) if task_data['deadline'] else None
                    task = Task(
                        task_name=task_data['task_name'],
                        importance=task_data['importance'],
                        deadline=deadline
                    )
                    task.urgency = task_data['urgency']
                    task.priority_score = task_data['priority_score']
                    task.is_complete = task_data['is_complete']
                    self.addTask(task)
        except FileNotFoundError:
            pass

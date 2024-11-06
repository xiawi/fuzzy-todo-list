import datetime

class Task:
    def __init__(self, task_name:str, importance:int, deadline:datetime.datetime=None):
        self.task_name = task_name
        self.importance = importance
        self.deadline = deadline
        self.urgency = 0 if self.deadline == None else None # if there is no deadline, urgency score is automatically set to 0
        self.priority_score = None
        self.isComplete = False
        
    def triggerCompletion(self):
        self.isComplete = True if self.isComplete == False else False
        
    def toDict(self):
        task_dict = self.__dict__.copy()
        if self.deadline:
            task_dict['deadline'] = self.deadline.isoformat()  # Convert datetime to string
        return task_dict
        
# for testing        

# if __name__ == "__main__":
#     t = Task("test", 10, datetime.datetime(2024,12,12))
#     print(t.__dict__)
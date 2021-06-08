class WhenAllTask:
    def __init__(self, id, tasks):
        self.pending_tasks = set()
        self.completed_tasks = []
     
    def signal_completion(self, child):
        try:
            self.pending_tasks.remove(child)
        except KeyError:
            raise Exception("TBD")
        
        self.completed_tasks.append(child)
    
    @property
    def is_completed(self):
        return len(self.pending_tasks) == 0
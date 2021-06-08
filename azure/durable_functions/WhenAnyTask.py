class WhenAnyTask:
    def __init__(self, id, tasks):
        self.pending_tasks = set()
        self.completed_tasks = set()
        self.is_completed = len(self.completed_tasks) >= 1
     
    def signal_completion(self, child):
        try:
            self.pending_tasks.remove(child)
        except KeyError:
            raise Exception("TBD")
        
        self.completed_tasks.add(child)
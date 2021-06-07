from azure.durable_functions.models.Task import Task

class MutableTask():
    def __init__(self, id_):
        self.id = id_
        self.has_parent = False

    def set_result(self, result):
        self.is_completed = True
        self.result = result
        if self.has_parent:
            self.parent.handle_child_completion(self)

    def set_error(self, error):
        self.is_completed = True
        self.is_faulted = True
        self.error = error

        if self.has_parent:
            self.parent.handle_child_completion(self) 
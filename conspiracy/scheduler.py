from abc import ABC, abstractmethod

class Scheduler(ABC):
    def __init__(self, frequency):
        self.frequency = frequency
        self.previous_index = 0
    
    def step(self, steps):
        if not self.frequency:
            return None
        
        update_index = steps // self.frequency
        if update_index > self.previous_index:
            result = self.update(update_index, steps)
        else:
            result = None
        
        self.previous_index = update_index
        return result
    
    @abstractmethod
    def update(self, index, steps):
        pass
    
    def state_dict(self):
        return {'previous_index' : self.previous_index}
    
    def load_state_dict(self, state_dict):
        self.previous_index = state_dict['previous_index']

class DynamicScheduler(Scheduler):
    def __init__(self, frequency, dynamic_update):
        super().__init__(frequency)
        self.dynamic_update = dynamic_update
    
    def update(self, index, steps):
        return self.dynamic_update(index, steps)

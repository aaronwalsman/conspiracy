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
            # it's important to set previous_index before self.update
            # so that get_state will be valid inside the update method
            # which is relevant for the checkpointer
            self.previous_index = update_index
            result = self.update(update_index, steps)
        else:
            result = None
        
        #self.previous_index = update_index
        return result
    
    @abstractmethod
    def update(self, index, steps):
        pass
    
    def get_state(self):
        return {'previous_index' : self.previous_index}
    
    def set_state(self, state_dict):
        self.previous_index = state_dict['previous_index']

class DynamicScheduler(Scheduler):
    def __init__(self, frequency, dynamic_update):
        super().__init__(frequency)
        self.dynamic_update = dynamic_update
    
    def update(self, index, steps):
        return self.dynamic_update(index, steps)

class LinearSchedule:
    def __init__(self, start_v, end_v, start_t, end_t):
        self.start_v = start_v
        self.end_v = end_v
        self.start_t = start_t
        self.end_t = end_t
    
    def value(self, t):
        if t < self.start_t:
            return self.start_v
        elif t > self.end_t:
            return self.end_v
        else:
            tt = (t-self.start_t)/(self.end_t-self.start_t)
            return self.start_v + (self.end_v-self.start_v)*tt

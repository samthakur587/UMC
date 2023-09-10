class SortedObject:
    def __init__(self, id, value):
        self.id = id
        self.value = value
        
    def __lt__(self, other):
        return self.value < other.value
    
    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

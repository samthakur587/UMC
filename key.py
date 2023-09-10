class Key:
    def __init__(self, val):
        self.val = val
        
    def __eq__(self, other):
        if not isinstance(other, Key):
            return False
        if len(self.val) != len(other.val):
            return False
        for i in range(len(self.val)):
            if self.val[i] != other.val[i]:
                return False
        return True
    
    def __hash__(self):
        result = 17  # any prime number
        for v in self.val:
            result = 31 * result + hash(v)
        return result

from dataclasses import dataclass

def jsondata(cls):
    cls = dataclass(cls)
    class Wrapper:
        def __init__(self, *args, **kwargs):
            self.wrap = cls(*args, **kwargs)

        def __setitem__(self, key, value):
            setattr(self.wrap, key, value)

        def __getitem__(self, key):
            return getattr(self.wrap, key)
        
        def __eq__(self, other):
            return self.json() == other.json()
        
        def __str__(self):
            return str(self.wrap.json())
        
        def __repr__(self):
            return str(self.wrap.json())
              
        def json(self):
            return vars(self.wrap)
        
        @staticmethod
        def from_json(data: dict):
            fields = list(cls.__annotations__.keys())
            args = [
                data[key]
                for key in fields
            ]
            return Wrapper(*args)
          
    return Wrapper

import abc

class Tombola(abc.ABC):
    @abc.abstractmethod
    def load(self, iterable):
        pass

    @abc.abstractmethod
    def pick(self):
        """随机删除元素，然后将其返回"""

    def loaded(self):
        """
        如果至少有一个元素，返回`True`，否则返回`False`
        """
        return bool(self.inspect())
    
    def inspect(self):
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(sorted(items))  
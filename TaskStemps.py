# TaskStemps.py

class TaskStemps:
    def __init__(self, initial_value: int = 0):
        if not isinstance(initial_value, int) or initial_value < 0:
            raise ValueError("Initial value must be a non-negative integer.")
        self._value = initial_value

    def set_task(self, index: int, solved: bool):

        index -= 1
        if index < 0:
            raise IndexError("Index must be non-negative.")
        if solved:
            self._value |= (1 << index)
        else:
            self._value &= ~(1 << index)


    def get_task(self, index: int) -> bool:
        index -= 1
        if index < 0:
            raise IndexError("Index must be non-negative.")
        return bool(self._value & (1 << index))

    def to_list(self, length: int = None) -> list[bool]:
        if length is None:
            if self._value == 0:
                return []
            length = self._value.bit_length()
        return [self.get_task(i) for i in range(length)]

    @property
    def value(self) -> int:
        return self._value

    def __repr__(self):
        return f"TaskStemps({self._value})"

    def __str__(self):
        return f"TaskStemps with bits: {bin(self._value)}"
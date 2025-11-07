import re

class FilterTypes:
    EQUALS = 0
    NOT_EQUALS = 1
    CONTAINS = 2
    NOT_CONTAINS = 3
    BEGINS_WITH = 4
    ENDS_WITH = 5
    @staticmethod
    def StringToType(op: str):
        match op:
            case "=":
                return FilterTypes.EQUALS
            case "!=":
                return FilterTypes.NOT_EQUALS
            case "*=":
                return FilterTypes.CONTAINS
            case "!*=":
                return FilterTypes.NOT_CONTAINS
            case "^=":
                return FilterTypes.BEGINS_WITH
            case "$=":
                return FilterTypes.ENDS_WITH
        
class Filter:
    @staticmethod
    def CreateFromString(string: str):
        values = re.split(r"(\W*=)", string)
        if len(values) != 3:
            raise ValueError(f"Invalid filter string: {string}")
        field = values[0]
        op = values[1]
        value = values[2]
        return Filter(field, FilterTypes.StringToType(op), value)
    def __init__(self, field: str, op, value: str):
        self.field = field
        self.op = op
        self.value = value.lower()
    def Match(self, value):
        value = str(value).lower()
        match self.op:
            case FilterTypes.EQUALS:
                return value == self.value
            case FilterTypes.NOT_EQUALS:
                return value != self.value
            case FilterTypes.CONTAINS:
                return self.value in value
            case FilterTypes.NOT_CONTAINS:
                return self.value not in value
            case FilterTypes.BEGINS_WITH:
                return value.startswith(self.value)
            case FilterTypes.ENDS_WITH:
                return value.endswith(self.value)
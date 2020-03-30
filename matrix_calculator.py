import operator as op
from typing import List, Optional, Union, Any
import time


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return return_value

    return wrapper


class NaturalNumber:
    def __get__(self, instance: Any, owner: Any) -> int:
        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: int) -> None:
        if value <= 0:
            raise ValueError('Cannot be negative or 0')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name


MatrixType = Optional[List[List[float]]]


class Matrix(list):
    horizontal: int = NaturalNumber()
    vertical: int = NaturalNumber()

    def __init__(self, vertical: int, horizontal: int, math_object: MatrixType = None) -> None:
        self.horizontal = horizontal
        self.vertical = vertical
        if math_object:
            super().__init__(math_object)
        else:
            super().__init__([])
            print(f'Fill in the lines ({self.vertical}✕{self.horizontal})')
            for _ in range(self.vertical):
                data = input().split()
                if len(row := list(map(lambda el: float(el), data))) != self.horizontal:
                    raise ValueError('Incorrect data input')
                self.append(row)

    def transpose(self) -> 'Matrix':
        vertical = self.horizontal
        horizontal = self.vertical
        matrix = [[self[column][row] for column in range(horizontal)] for row in range(vertical)]
        return Matrix(vertical, horizontal, matrix)

    def __repr__(self) -> str:
        string = ''
        for row in range(self.vertical):
            for column in range(self.horizontal):
                string += f'{self[row][column]} '
            string += '\n'
        return string


MathType = Union[Matrix, float, int]


class MathHandler:

    @staticmethod
    def _initialize_empty_matrix(vertical: int):
        return [[] for _ in range(vertical)]

    @staticmethod
    def search_max_or_min(a: Matrix, operator) -> Union[float, int]:
        if a.vertical != 1:
            raise ArithmeticError('not a vector')

        a = a[0]
        result = a[0]
        for elem in a[1:]:
            if operator(elem, result):
                result = elem
        return result

    @staticmethod
    def scalar_product(a: Matrix, b: Matrix) -> Union[float, int]:
        if a.vertical != 1:
            raise ArithmeticError('not a vector')

        a, b = a[0], b[0]
        result = 0
        for index in range(len(a)):
            result += a[index] * b[index]

        return result

    def _constant_mul(self, constant: Union[float, int], a: Matrix) -> Matrix:
        matrix = self._initialize_empty_matrix(a.vertical)
        for row in range(a.vertical):
            for col in range(a.horizontal):
                matrix[row].append(constant * a[row][col])

        return Matrix(a.vertical, a.horizontal, matrix)

    def _matrix_mul(self, a: Matrix, b: Matrix) -> MathType:
        if a.vertical == 1 and b.vertical == 1:
            return self.scalar_product(a, b)
        elif a.horizontal != b.vertical:
            raise ArithmeticError(
                'The number of columns in the first matrix should equal the number of rows in the second')

        matrix = self._initialize_empty_matrix(a.vertical)
        for i, row in enumerate(a):
            for j, column in enumerate(b.transpose()):
                matrix[i].append(sum(r * c for r, c in zip(row, column)))

        return Matrix(a.vertical, b.horizontal, matrix)

    def _multiply(self, a: MathType, b: MathType) -> MathType:
        if type(a) in (float, int) and isinstance(b, Matrix):
            return self._constant_mul(constant=a, a=b)

        elif type(b) in (float, int) and isinstance(a, Matrix):
            return self._constant_mul(constant=b, a=a)

        elif isinstance(a, Matrix) and isinstance(b, Matrix):
            return self._matrix_mul(a, b)

        else:
            return a * b

    def _divide(self, a: MathType, b: MathType) -> MathType:
        if type(b) in (float, int) and isinstance(a, Matrix):
            return self._constant_mul(constant=1 / b, a=a)

        elif type(a) in (float, int) and type(b) in (float, int):
            return a / b

        else:
            raise ArithmeticError('Matrices cannot be divided')

    def _matrix_add_or_sub(self, a: Matrix, operator, b: Matrix) -> Matrix:
        if a.vertical != b.vertical or a.horizontal != b.horizontal:
            raise ArithmeticError('The number of rows and columns must be the same')

        matrix = self._initialize_empty_matrix(a.vertical)
        for row in range(a.vertical):
            for col in range(a.horizontal):
                matrix[row].append(operator(a[row][col], b[row][col]))

        return Matrix(a.vertical, a.horizontal, matrix)

    def _add_or_sub(self, a: MathType, operator, b: MathType) -> MathType:
        if isinstance(a, Matrix) and isinstance(b, Matrix):
            return self._matrix_add_or_sub(a, operator, b)

        elif type(a) in (float, int) and type(b) in (float, int):
            return operator(a, b)

        else:
            raise ArithmeticError('The type of operands must be the same')

    def controller(self, a: MathType, operation: str, b: Optional[MathType] = None) -> MathType:
        operators = {
            '+': lambda: self._add_or_sub(a, op.add, b),
            '-': lambda: self._add_or_sub(a, op.sub, b),
            '*': lambda: self._multiply(a, b),
            '/': lambda: self._divide(a, b)
        }

        operations = {
            'max': lambda: self.search_max_or_min(a, op.gt),
            'min': lambda: self.search_max_or_min(a, op.lt)
        }

        if req_func := operators.get(operation):
            return req_func()
        elif (req_func := operations.get(operation)) and b is None:
            return req_func()
        else:
            raise ArithmeticError('Unknown operation received')
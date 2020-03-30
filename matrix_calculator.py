import time
from operator import add, sub, gt, lt
from typing import List, Optional, Union, Any


def logged(time_format='%b %d %Y - %H:%M:%S'):
    def decorator(func):
        def decorated_func(*args, **kwargs):
            print(f'- Running <{func.__name__}> on {time.strftime(time_format)} ')
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f'- Finished <{func.__name__}>, execution time = {end_time - start_time}s ')
            return result

        decorated_func.__name__ = func.__name__
        return decorated_func

    return decorator


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
    horizontal = NaturalNumber()
    vertical = NaturalNumber()

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

    @staticmethod
    def is_vector(matrix):
        return True if matrix.vertical == 1 else False

    def transpose(self) -> 'Matrix':
        vertical = self.horizontal
        horizontal = self.vertical
        matrix = [[self[column][row] for column in range(horizontal)] for row in range(vertical)]
        return Matrix(vertical, horizontal, matrix)

    def __repr__(self) -> str:
        string = '\n'
        for row in range(self.vertical):
            for column in range(self.horizontal):
                string += f'{self[row][column]} '
            string += '\n'
        return string


NumericType = Union[float, int]
MathType = Union[Matrix, float, int]


class MatrixCalculator:

    @staticmethod
    def _initialize_empty_matrix(vertical: int):
        return [[] for _ in range(vertical)]

    @staticmethod
    def search_max_or_min(a: Matrix, operator) -> NumericType:
        if not Matrix.is_vector(a):
            raise ArithmeticError(f'Not a vector {a=}')

        a = a[0]
        result = a[0]
        for element in a[1:]:
            if operator(element, result):
                result = element

        return result

    @staticmethod
    def _scalar_product(a: Matrix, b: Matrix) -> NumericType:
        if not Matrix.is_vector(a):
            raise ArithmeticError(f'Not a vector {a=}')

        a, b = a[0], b[0]
        result = 0
        for index in range(len(a)):
            result += a[index] * b[index]

        return result

    def _constant_mul(self, constant: NumericType, a: Matrix) -> Matrix:
        matrix = self._initialize_empty_matrix(a.vertical)
        for row in range(a.vertical):
            for column in range(a.horizontal):
                matrix[row].append(constant * a[row][column])

        return Matrix(a.vertical, a.horizontal, matrix)

    def _matrix_mul(self, a: Matrix, b: Matrix) -> MathType:
        if a.vertical == 1 and b.vertical == 1:
            return self._scalar_product(a, b)
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

    def _divide(self, a: MathType, b: NumericType) -> MathType:
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
            for column in range(a.horizontal):
                matrix[row].append(operator(a[row][column], b[row][column]))

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
            '+': lambda: self._add_or_sub(a, add, b),
            '-': lambda: self._add_or_sub(a, sub, b),
            '*': lambda: self._multiply(a, b),
            '/': lambda: self._divide(a, b)
        }

        operations = {
            'max': lambda: self.search_max_or_min(a, gt),
            'min': lambda: self.search_max_or_min(a, lt)
        }

        if req_func := operators.get(operation):
            return req_func()
        elif (req_func := operations.get(operation)) and b is None:
            return req_func()
        else:
            raise ArithmeticError('Unknown operation received')

import time
from operator import add, sub
from typing import List, Optional, Union, Any
from functools import wraps


def logged(time_format='%b %d %Y - %H:%M:%S', separator=''):
    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            print(f'{separator}- Running <{func.__qualname__}> on {time.strftime(time_format)}')
            start_time = time.time()
            result = func(*args, **kwargs)
            print(f'- Finished <{func.__qualname__}>, execution time = {time.time() - start_time}s{separator}')
            return result
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

    @logged()
    def __init__(self, vertical: int, horizontal: int, math_object: MatrixType = None, fill_auto=False) -> None:
        self.horizontal = horizontal
        self.vertical = vertical

        if math_object:
            super().__init__(math_object)
        else:
            if fill_auto:
                super().__init__([[1 for _ in range(horizontal)] for _ in range(vertical)])
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

    @logged()
    def transpose(self) -> 'Matrix':
        matrix = [[self[row][column] for row in range(self.vertical)] for column in range(self.horizontal)]
        return Matrix(self.horizontal, self.vertical, math_object=matrix)

    @logged()
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
    @logged(separator='\n')
    def search_max_or_min(a: Matrix, operation) -> NumericType:
        if not Matrix.is_vector(a):
            raise ArithmeticError(f'Not a vector {a=}')

        a = a[0]
        return max(a) if operation == 'max' else min(a)

    @staticmethod
    @logged()
    def _scalar_product(a: Matrix, b: Matrix) -> NumericType:
        return sum(map(lambda a_elem, b_elem: a_elem * b_elem, a[0], b[0]))

    @staticmethod
    @logged(separator='\n')
    def _constant_mul(constant: NumericType, a: Matrix) -> Matrix:
        matrix = [[constant * a[row][column] for column in range(a.horizontal)] for row in range(a.vertical)]
        return Matrix(a.vertical, a.horizontal, matrix)

    @logged(separator='\n')
    def _matrix_mul(self, a: Matrix, b: Matrix) -> MathType:
        if a.vertical == 1 and b.vertical == 1 and a.horizontal == b.horizontal:
            return self._scalar_product(a, b)

        elif a.horizontal != b.vertical:
            raise ArithmeticError(
                'The number of columns in the first matrix should equal the number of rows in the second')

        b = b.transpose()
        matrix = [[sum(r_a * r_b for r_a, r_b in zip(row_a, row_b)) for row_b in b] for row_a in a]
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

    @staticmethod
    @logged(separator='\n')
    def _matrix_add_or_sub(a: Matrix, operator, b: Matrix) -> Matrix:
        if a.vertical != b.vertical or a.horizontal != b.horizontal:
            raise ArithmeticError('The number of rows and columns must be the same')
        # c - column; r - row
        matrix = [[operator(a[r][c], b[r][c]) for c in range(a.horizontal)] for r in range(a.vertical)]
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
            'max': lambda: self.search_max_or_min(a, 'max'),
            'min': lambda: self.search_max_or_min(a, 'min')
        }

        if req_func := operators.get(operation):
            return req_func()
        elif (req_func := operations.get(operation)) and b is None:
            return req_func()
        else:
            raise ArithmeticError('Unknown operation received')


if __name__ == '__main__':
    calc = MatrixCalculator()

    v1 = Matrix(1, 30, fill_auto=True)
    v2 = Matrix(1, 30, fill_auto=True)
    n1 = calc.controller(v1, '*', v2)
    calc.controller(n1, '*', v1)

    m1 = Matrix(20, 20, fill_auto=True)
    m2 = Matrix(20, 20, fill_auto=True)
    m3 = calc.controller(m1, '*', m2)
    calc.controller(m3, '+', m2)

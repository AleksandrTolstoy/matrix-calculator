import unittest
from matrix_calculator import Matrix, MatrixCalculator


class TestVector(unittest.TestCase):

    calculator = MatrixCalculator()
    N = 3
    v1 = Matrix(1, N, fill_auto=True)
    v2 = Matrix(1, N, fill_auto=True)

    def test_add_and_sub(self):
        test_vector = self.calculator.controller(self.v1, '+', self.v2)
        res_vector = Matrix(1, self.N, [[2, 2, 2]])
        self.assertEqual(test_vector, res_vector)
        test_vector = self.calculator.controller(self.v1, '-', self.v1)
        res_vector = Matrix(1, self.N, [[0, 0, 0]])
        self.assertEqual(test_vector, res_vector)

    def test_mul(self):
        test_res = self.calculator.controller(self.v1, '*', self.v2)
        res = 3
        self.assertEqual(test_res, res)

    def test_div(self):
        divider = 1
        test_vector = self.calculator.controller(self.v1, '/', divider)
        res_vector = Matrix(1, self.N, [[1, 1, 1]])
        self.assertEqual(test_vector, res_vector)
        with self.assertRaises(ArithmeticError):
            self.calculator.controller(self.v1, '/', self.v2)
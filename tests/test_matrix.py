import unittest
from matrix_calculator import Matrix, MatrixCalculator


class TestMatrix(unittest.TestCase):

    calculator = MatrixCalculator()
    N = 2
    m1 = Matrix(N, N, fill_auto=True)
    m2 = Matrix(N, N, fill_auto=True)

    def test_transpose(self):
        matrix = Matrix(self.N, self.N, [[1, 2],
                                         [3, 4]])
        test_matrix = matrix.transpose()
        res_matrix = Matrix(self.N, self.N, [[1, 3],
                                             [2, 4]])
        self.assertEqual(test_matrix, res_matrix)

    def test_add_and_sub(self):
        test_matrix = self.calculator.controller(self.m1, '+', self.m2)
        res_matrix = Matrix(self.N, self.N, [[2, 2], [2, 2]])
        self.assertEqual(test_matrix, res_matrix)
        test_matrix = self.calculator.controller(self.m1, '-', self.m1)
        res_matrix = Matrix(self.N, self.N, [[0, 0], [0, 0]])
        self.assertEqual(test_matrix, res_matrix)

    def test_mul(self):
        test_matrix = self.calculator.controller(self.m1, '*', self.m2)
        res_matrix = Matrix(self.N, self.N, [[2, 2], [2, 2]])
        self.assertEqual(test_matrix, res_matrix)
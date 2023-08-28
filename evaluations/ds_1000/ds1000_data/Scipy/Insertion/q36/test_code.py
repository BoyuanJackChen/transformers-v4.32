import numpy as np
import pandas as pd
import io
from scipy import integrate
from scipy.sparse import csr_matrix
import parser


def extract_element(t):
    if type(t) != list:
        return [t]
    xs = []
    for e in t:
        xs += extract_element(e)
    return xs


def stringTest(code):
    ast = parser.st2list(parser.suite(code))
    leaves = extract_element(ast)
    return (
        "toarray" not in leaves
        and "array" not in leaves
        and "todense" not in leaves
        and "A" not in leaves
    )


def test(result, ans):
    assert np.allclose(result, ans)
    return 1

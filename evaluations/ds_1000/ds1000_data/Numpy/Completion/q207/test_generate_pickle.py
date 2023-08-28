import numpy as np
import pandas as pd
import numpy as np
import copy


def define_test_input(args):
    if args.test_case == 1:
        a = np.ones((41, 13))
        shape = (93, 13)

    return a, shape


def ans1(_a):
    arr, shape = _a
    result = np.pad(
        arr, ((0, shape[0] - arr.shape[0]), (0, shape[1] - arr.shape[1])), "constant"
    )

    return result


if __name__ == "__main__":
    import argparse
    import os
    import pickle

    parser = argparse.ArgumentParser()
    parser.add_argument("--test_case", type=int, default=1)
    args = parser.parse_args()

    a = define_test_input(args)
    ans = ans1(copy.deepcopy(a))

    if not os.path.exists("input"):
        os.mkdir("input")
    with open("input/input{}.pkl".format(args.test_case), "wb") as f:
        pickle.dump(a, f)

    if not os.path.exists("ans"):
        os.mkdir("ans")
    with open("ans/ans{}.pkl".format(args.test_case), "wb") as f:
        pickle.dump(ans, f)

import math
import numpy as np


class Volatility(object):

    @staticmethod
    def get_history_volatility(price_list):
        X = []
        for i in range(len(price_list)-2):
            X.append(math.log(price_list[i+1]/price_list[i]))
        return np.std(X)

if __name__ == "__main__":
    print Volatility.get_history_volatility([1.1, 1.2, 1.2, 1.2, 1, 0.9])
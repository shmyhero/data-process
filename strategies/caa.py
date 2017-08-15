from algorithms.cla import CLA
from research.tradesimulation import TradeAccount, TradeNode, TradeSimulation

lower_bounds = [[0.00],[0.00],[0.00],[0.00],[0.00],[0.00],[0.00],[0.00]]
upper_bounds = [[0.25],[0.25],[0.25],[0.25],[0.25],[0.25],[1.00],[1.00]]


#TODO: calculate covar& mean...
covar = None
mean = None
cla = CLA(mean, covar, lower_bounds, upper_bounds)

mu,sigma,weights=cla.efFrontier(1000)
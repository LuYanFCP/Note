import matplotlib.pyplot as plt
import numpy as np

x = np.random.uniform(-6, 6, 200)
# xmax = np.max(x)
# xmin = np.min(x);
xmax = 5
xmin = -5

delta = (xmax - xmin) / 10
xq = np.round(x / delta)
x.sort()
xq.sort()

x_ = x[:]
x_[x_ > xmax] = xmax
x_[x_ < xmin] = xmin

k = xmax - xmin

plt.plot(x, xq)
plt.plot(x, x_)
# plt.scatter(x, xq)

plt.show()
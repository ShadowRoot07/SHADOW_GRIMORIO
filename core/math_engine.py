import numpy as np\
\
def calculate_rsi(prices, period=14):\
\\t\\tdelta = np.diff(prices)\
\\t\\tup, down = delta.copy(), delta.copy()\
\\t\\tup[up < 0] = 0\
\\t\\tdown[down > 0] = 0\
\\t\\troll_up = np.cumsum(up)\
\\t\\troll_down = np.cumsum(np.abs(down))\
\\t\\trs = roll_up / roll_down\
\\t\\trsi = 100.0 - (100.0 / (1.0 + rs))\
\\t\\treturn rsi\
\
\
def calculate_moving_average(prices, period=20):\
\\t\\treturn np.convolve(prices, np.ones(period) / period, mode='valid')
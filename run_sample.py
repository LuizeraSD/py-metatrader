from datetime import datetime
from metatrader.mt4 import initizalize
from metatrader.backtest import BackTest

SYMBOL = 'EURUSD'
PERIOD = 'H1'
DEPOSIT = 1000
METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4'
EA_NAME = 'Spartan Bolt V6\\Spartan Bolt V6.ex4'
INI_DATE = datetime(2018, 1, 1)
END_DATE = datetime(2018, 2, 1)

# create ea param by dict.
param = {
         'PipStep': {'value': 20},
         'LotMultiplier': {'value': 1.8}
         }

initizalize(METATRADER_DIR)

backtest = BackTest(EA_NAME, param, SYMBOL, PERIOD, INI_DATE, END_DATE, DEPOSIT)

# run backtest
ret = backtest.run()

# you can get result from result object
# for example you can print gross profit
print ret.gross_profit
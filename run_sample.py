from datetime import datetime
from metatrader.mt4 import initizalize
from metatrader.backtest import BackTest

DEPOSIT = 542
METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4'
EA_NAME = 'Spartan Bolt V6\\Spartan Bolt V6.ex4'


from_date = datetime(2018, 1, 1)
to_date = datetime(2018, 2, 1)



# create ea param by dict.
param = {
         'PipStep': {'value': 20},
         'LotMultiplier': {'value': 1.8}
         }

initizalize(METATRADER_DIR)
# create backtest object
backtest = BackTest(EA_NAME, param, 'EURUSD', 'H1', from_date, to_date, DEPOSIT)

# run backtest
ret = backtest.run()

# you can get result from result object
# for example you can print gross profit
print ret.gross_profit
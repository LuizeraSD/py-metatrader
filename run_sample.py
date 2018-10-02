from datetime import datetime
from metatrader.mt4 import initizalize
from metatrader.backtest import BackTest
import requests

SYMBOL = 'USDJPY'
PERIOD = 'M15'
DEPOSIT = 1000
METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4'
EA_NAME = 'Spartan Bolt V6\\Spartan Bolt V6.ex4'
SET_FILE = 'C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\PPP_USDJPY5M_Desde2017_600percent.set'
YEAR = 2018
MONTH = None

initizalize(METATRADER_DIR)

if MONTH == None:
    iniMonth = 1
    maxMonth = 12
    today = datetime.today()
    if(today.year == YEAR):
        maxMonth = today.month
else:
    iniMonth = MONTH
    maxMonth = MONTH+1

#TODO: Adicionar check se ja existe um BT com esses parametros
for MONTH in range(iniMonth,maxMonth):
    backtest = BackTest(EA_NAME, SET_FILE, SYMBOL, PERIOD, datetime(YEAR, MONTH, 1), datetime(YEAR, MONTH+1, 1), DEPOSIT)
    ret = backtest.run()

    retdata = {
        "action": "register",
        "ea": backtest.ea_md5,
        "ea_name": backtest.ea_name,
        "ano": YEAR,
        "mes": MONTH,
        "symbol": SYMBOL,
        "period": PERIOD,
        "profit": ret.profit,
        "deposit": DEPOSIT,
        "modelQuality": ret.modeling_quality_percentage,
        "profitFactor": ret.profit_factor,
        "payoff": ret.expected_payoff,
        "maxDrawDown": ret.max_drawdown,
        "maxDrawDownRate": ret.max_drawdown_rate,
        "relDrawDown": ret.relative_drawdown,
        "relDrawDownRate": ret.relative_drawdown_rate,
        "absDrawDown": ret.abs_drawdown,
        "grossProfit": ret.gross_profit,
        "grossLoss": ret.gross_loss,
        "totalTrades": ret.total_trades,
        "largestProfit": ret.largest_profit_trade,
        "largestLoss": ret.largest_loss_trade,
        "avgProfitTrade": ret.average_profit_trade,
        "avgLossTrade": ret.average_loss_trade,    
        "maxConsecutiveProfitCount": ret.max_consecutive_profit_count,
        "maxConsecutiveProfit": ret.max_consecutive_profit,
        "maxConsecutiveLossCount": ret.max_consecutive_loss_count,
        "maxConsecutiveLoss": ret.max_consecutive_loss,
        "maxConsecutiveWinsCount": ret.max_consecutive_wins_count,
        "maxConsecutiveWinsProfit": ret.max_consecutive_wins_profit,
        "maxConsecutiveLossesCount": ret.max_consecutive_losses_count,
        "maxConsecutiveLosses": ret.max_consecutive_losses_loss,
        "profitTrades": ret.profit_trades,
        "profitTradesRate": ret.profit_trades_rate,
        "lossTrades": ret.loss_trades,
        "lossTradesRate": ret.loss_trades_rate,
        "avgConsecutiveWins": ret.ave_consecutive_wins,
        "avgConsecutiveLosses": ret.ave_consecutive_losses,
        "shortPositions": ret.short_positions,
        "shortPositionsRate": ret.short_positions_rate,
        "longPositions": ret.long_positions,
        "longPositionsRate": ret.long_positions_rate,
    }
    print retdata

    #r = requests.post('http://167.99.227.51/bt/register.php', data=retdata)
    #print r.status_code
    #print r.json()
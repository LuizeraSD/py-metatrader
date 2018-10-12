from metatrader.mt4 import runBackTest

import csv

#METATRADER_DIR = 'C:\\Program Files (x86)\\Tickmill MT4 Client Terminal'
METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4 - 1'

EA_NAME = 'Blessing3.ex4'

SET_FILE = [
"C:\\Users\\Luizera\\OneDrive\\BackTests\\Blessing\\default_morerisk.set",
"C:\\Users\\Luizera\\OneDrive\\BackTests\\Blessing\\noTraditional_any_ma_cci.set"
]

PERIOD = ['H1']

YEAR = [2015,2016,2017]
MONTH = None
DEPOSIT = 1000
UPLOAD_BACKTEST = True

#To make weekly backtests, active this flag:
WEEKLY = False

#Major Symbols

SYMBOLS = ["EURUSD","GBPUSD","USDJPY","USDCAD","USDCHF","AUDUSD","NZDUSD"]

#If you want more symbols, just uncomment the desired line below:
SYMBOLS.extend(["EURJPY","EURGBP","EURCHF","EURCAD","EURAUD","EURNZD"]) #EUR Crosses 
SYMBOLS.extend(["GBPAUD","GBPCAD","GBPCHF","GBPJPY","GBPNZD"]) #GBP Crosses 
SYMBOLS.extend(["AUDJPY","AUDCAD","AUDCHF","AUDNZD"]) #AUD Crosses 
SYMBOLS.extend(["NZDCAD","NZDCHF","NZDJPY"]) #NZD Crosses 
SYMBOLS.extend(["CADJPY","CADCHF"]) #CAD Crosses 
SYMBOLS.extend(["CHFJPY"]) #CHF Cross 
SYMBOLS.extend(["GOLD"]) #GOLD

runBackTest(METATRADER_DIR, EA_NAME, SET_FILE, SYMBOLS, PERIOD, YEAR, MONTH, WEEKLY, DEPOSIT, UPLOAD_BACKTEST)
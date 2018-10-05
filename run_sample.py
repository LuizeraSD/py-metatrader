#TODO: Adicionar opcao de rodar por semana
#TODO: Adicionar upload do Gif
#TODO: Adicionar opcao de Optimization mode, ele escolhe os 5 melhores e roda 1 ano (mes a mes)

from metatrader.mt4 import runBackTest
import csv

METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4'
EA_NAME = 'Spartan Bolt V6\\Spartan Bolt V6.ex4'
SET_FILE = 'C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\PPP_USDJPY5M_Desde2017_600percent.set'

PERIOD = 'M15'
YEAR = 2018
MONTH = None
DEPOSIT = 1000
UPLOAD_BACKTEST = False

#To make weekly backtests, active this flag:
WEEKLY = True

#Major Symbols
SYMBOLS = ["EURUSD"]
#SYMBOLS = ["EURUSD","GBPUSD","USDJPY","USDCAD","USDCHF","AUDUSD","NZDUSD"]

#If you want more symbols, just uncomment the desired line below:
#SYMBOLS.extend(["EURJPY","EURGBP","EURCHF","EURCAD","EURAUD","EURNZD"]) #EUR Crosses 
#SYMBOLS.extend(["GBPAUD","GBPCAD","GBPCHF","GBPJPY","GBPNZD"]) #GBP Crosses 
#SYMBOLS.extend(["AUDJPY","AUDCAD","AUDCHF","AUDNZD"]) #AUD Crosses 
#SYMBOLS.extend(["NZDCAD","NZDCHF","NZDJPY"]) #NZD Crosses 
#SYMBOLS.extend(["CADJPY","CADCHF"]) #CAD Crosses 
#SYMBOLS.extend(["CHFJPY"]) #CHF Cross 
#SYMBOLS.extend(["XAUUSD"]) #GOLD

runBackTest(METATRADER_DIR, EA_NAME, SET_FILE, SYMBOLS, PERIOD, YEAR, MONTH, WEEKLY, DEPOSIT, UPLOAD_BACKTEST)
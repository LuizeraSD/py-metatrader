#TODO: Adicionar upload do Gif
#TODO: Adicionar opcao de Optimization mode, ele escolhe os 5 melhores e roda 1 ano (mes a mes)
#TODO: Ter opcao de disparar varios terminais simultaneos

from metatrader.mt4 import runBackTest

import csv

METATRADER_DIR = 'C:\\Program Files (x86)\\Tickmill MT4 Client Terminal'
EA_NAME = 'saunapips\\SaunaPips.ex4'
SET_FILE = [
"C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\SaunaPips\\teste\\2-OnlyMonday.set"
"C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\SaunaPips\\teste\\3-OnlyTuesday.set"
"C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\SaunaPips\\teste\\4-OnlyWednesday.set",
"C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\SaunaPips\\teste\\5-OnlyThursday.set",
"C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\SaunaPips\\teste\\6-OnlyFriday.set"]
#METATRADER_DIR = 'C:\\Program Files (x86)\\XM Global MT4'
#EA_NAME = 'Spartan Bolt V6\\Spartan Bolt V6.ex4'
#SET_FILE = 'C:\\Users\\Luizera\\OneDrive\\BackTests\\_SetsStore\\Spartan\\SpartanReversaoIV.set'



PERIOD = 'M1'
YEAR = 2018
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
SYMBOLS.extend(["XAUUSD"]) #GOLD

for myset in SET_FILE:
    runBackTest(METATRADER_DIR, EA_NAME, myset, SYMBOLS, PERIOD, YEAR, MONTH, WEEKLY, DEPOSIT, UPLOAD_BACKTEST)
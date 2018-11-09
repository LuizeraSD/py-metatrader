# -*- coding: utf-8 -*-
"""
@OriginAuthor: samuraitaiga
@ModifiedBy: LuizeraSD
"""
import os
import csv
import logging
import hashlib
import requests
import datetime
import re
import time
from win32com.client import Dispatch

_mt4s = {}

DEFAULT_MT4_NAME = 'default'
# mt4 program file path is written in origin.txt 
ORIGIN_TXT = 'origin.txt'
MT4_EXE = 'terminal.exe'

class MT4(object):
    """
    Notes:
      meta trader4 class which can lunch metatrader4.
      this class will only lunch metatrader4,
      because metatrader4 can lunch either normal mode or backtest mode. 
    """
    prog_path = None
    appdata_path = None

    def __init__(self, prog_path):
        if os.path.exists(prog_path):
            self.prog_path = prog_path
            if is_uac_enabled():
                self.appdata_path = get_appdata_path(prog_path)
            else:
                self.appdata_path = prog_path

        else:
            err_msg = 'prog_path %s not exists' % prog_path
            logging.error(err_msg)
            raise IOError(err_msg)

        if not has_mt4_subdirs(self.appdata_path):
            err_msg = 'appdata path %s has not sufficient dirs' % self.appdata_path
            logging.error(err_msg)
            raise IOError(err_msg) 
        
        ver_parser = Dispatch('Scripting.FileSystemObject')
        try:
            self.version = ver_parser.GetFileVersion(os.path.join(prog_path,'terminal.exe'))
        except:    
            self.version = 0
    

        conf_dir = os.path.join(self.appdata_path, 'config')
        self.broker = "broker"
        for filename in os.listdir(conf_dir):
            matchRegex = re.match(r'^([\w ]+)\-.+\.srv', filename)
            if (matchRegex):
                self.broker = matchRegex.group(1)
                break

        if not has_tickdata_install():
            self.usedTickData = False
            self.sourceTick = self.broker
            self.tickDataParams = {}
            err_msg = 'Tick Data Not Found / Not Installed'
            logging.error(err_msg)
        else:
            self.usedTickData = True
            self.sourceTick = "Dukascopy"
            self.tickDataParams = {
                "GMTOffset":"2",
                "DST":"1",
                "UseVariableSpread":"True",
                "SlippageEnabled":"True",
                "ReproducibleSlippage":"False",
                "OptimizationSlippage":"False",
                "LimitOrderSlippage":"True",
                "StopOrderSlippage":"True",
                "SlOrderSlippage":"True",
                "TpOrderSlippage":"True",
                "DealerStyleSlippage":"True",
                "MaxFavorableSlippage":"10",
                "MaxUnfavorableSlippage":"20",
                "UseCustomSlippageChance":"True",
                "CustomSlippageChance":"60",
                "UseCustomFavorableChance":"True",
                "FavorableSlippageChance":"40",
                "LiveExecutionStoploss":"True",
                "LiveExecutionTakeprofit":"True",
                "LiveExecutionStop":"True",
                "LiveExecutionLimit":"True",
            }

    def run(self, ea_name, conf=None):
        """
        Notes:
          run terminal.exe.
        Args:
          conf(string): abs path of conf file. 
            details see mt4 help doc Client Terminal/Tools/Configuration at Startup 
        """
        import subprocess
        
        if conf:
            prog = '"%s"' % os.path.join(self.prog_path, MT4_EXE)
            conf = '"%s"' % conf
            cmd = '%s %s' % (prog, conf)
            p = subprocess.Popen(cmd)            
            p.wait()
            if p.returncode == 0:
                logging.info('cmd[%s]', cmd)
            else:
                err_msg = 'run mt4 with cmd[%s] failed!!' % cmd
                logging.error(err_msg)
                raise RuntimeError(err_msg)


def has_mt4_subdirs(appdata_path):
    """
    Note:
      check this appdata path has required mt4 sub dirs.
      currently chech backtest related dirs.
      - history
      - profiles
      - tester
      - MQL4\\Experts
      - MQL4\\Libraries
    Returns:
      True if has required mt4 sub dirs,
      False if doesn't have
    """
    sub_dirs = [os.path.join(appdata_path, 'history'),
                os.path.join(appdata_path, 'profiles'),
                os.path.join(appdata_path, 'tester'),
                os.path.join(appdata_path, 'MQL4', 'Experts'),
                os.path.join(appdata_path, 'MQL4', 'Libraries')]
    ret = True

    for sub_dir in sub_dirs:
        if not os.path.exists(sub_dir) and not os.path.isdir(sub_dir):
            ret = False

    return ret

def is_uac_enabled():
    """
    Note:
      check uac is enabled or not from reg value.
    Returns:
     True if uac is enabled, False if uac is disabled.
    """
    import _winreg    
    
    try:
        reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System', 0, _winreg.KEY_READ)
        value, regtype = _winreg.QueryValueEx(reg_key, 'EnableLUA')
    except:
        return True
    
    if value == 1:
        #reg value 1 means UAC is enabled
        return True
    else:
        return False    

def has_tickdata_install():
    """
    Note:
      check if TickData is installed
    Returns:
      True if TickData is installed
    """
    import _winreg    
    
    try:
        reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\eareview.net\\Tick Data Suite', 0, _winreg.KEY_READ)
        value, regtype = _winreg.QueryValueEx(reg_key, 'LatestVersion')
    except:
        return False

    if value:
        return True
    else:
        return False


def get_appdata_path(program_file_dir):
    """
    Returns:
      AppData path corresponding to provided program file path
      e.g.: C:\\Users\\UserName\\AppData\\Roaming\\MetaQuotes\\Terminal\\7269C010EA668AEAE793BEE37C26ED57
    """
    app_data = os.environ.get('APPDATA')
    mt4_appdata_path = os.path.join(app_data, 'MetaQuotes', 'Terminal')

    app_dir = None

    walk_depth = 1
    for root, dirs, files in os.walk(mt4_appdata_path):
        # search ORIGIN_TXT until walk_depth
        depth = root[len(mt4_appdata_path):].count(os.path.sep)

        if ORIGIN_TXT in files:
            origin_file = os.path.join(root, ORIGIN_TXT)

            import codecs
            with codecs.open(origin_file, 'r', 'utf-16') as fp:
                line = fp.read()
                if line == program_file_dir:
                    app_dir = root
                    break

        if depth >= walk_depth:
            dirs[:] = []

    if app_dir == None:
        err_msg = '%s does not have appdata dir!.' % program_file_dir
        logging.error(err_msg)
        raise IOError(err_msg)

    return app_dir

def initizalize(ntpath, alias=DEFAULT_MT4_NAME):
    """
    Notes:
      initialize mt4
    Args:
      ntpath(string): mt4 install folder path.
        e.g.: C:\\Program Files (x86)\\MetaTrader 4 - Alpari Japan 
      alias(string): mt4 object alias name. default value is DEFAULT_MT4_NAME
    """
    global _mt4s
    if alias not in _mt4s:
        #store mt4 objecct with alias name
        _mt4s[alias] = MT4(ntpath, )
    else:
        logging.info('%s is already initialized' % alias)


def get_mt4(alias=DEFAULT_MT4_NAME):
    """
    Notes:
      return mt4 object which is initialized.
    Args:
      alias(string): mt4 object alias name. default value is DEFAULT_MT4_NAME
    Returns:
      mt4 object(metatrader.backtest.MT4): instantiated mt4 object
    """
    global _mt4s

    if alias in _mt4s:
        return _mt4s[alias]
    else:
        raise RuntimeError('mt4[%s] is not initialized.' % alias)


def runBackTest(metatrade_dir, ea_name, set_file, symbols, period, year, month=None, weekly=False, deposit=1000, uploadBT=False):
    """
    Notes:
      run the backtest set
    Returns:
      boolean: result of the success of the backtest set
    """
    initizalize(metatrade_dir)
    from metatrader.backtest import BackTest
    
    if isinstance(set_file, basestring):
        set_file = [set_file]

    if isinstance(symbols, basestring):
        symbols = [symbols]
    
    if isinstance(period, basestring):
        period = [period]
    
    if isinstance(year, basestring):
        year = [year]
    
    for mySet in set_file:
        for myPeriod in period:
            for symbol in symbols:
                for myYear in year:
                    today = datetime.date.today()

                    if month == None:
                        iniMonth = 1
                        maxMonth = 13
                        if(today.year == myYear):
                            maxMonth = today.month
                    else:
                        iniMonth = month
                        maxMonth = month+1

                    iniDate = datetime.date(myYear, iniMonth,1)
                    idx = iniDate.weekday()+1
                    sunday = iniDate - datetime.timedelta(days=idx)
                    saturday = sunday + datetime.timedelta(days=6)
    
                    try:                        
                        if(weekly):
                            while sunday < datetime.date(myYear, maxMonth, 1):
                                print("Generating BackTest for %s from %s to %s..." % (symbol, sunday, saturday))
                                backtest = BackTest(ea_name, mySet, symbol, myPeriod, sunday, saturday, deposit, uploadBT)
                                ret = backtest.run()
                                if(ret):
                                    collectBackTest(backtest, ret, myYear, month, uploadBT)
                                sunday += datetime.timedelta(days=7)
                                saturday += datetime.timedelta(days=7)
                        else:
                            for myMonth in range(iniMonth,maxMonth):
                                endYear=myYear
                                endMonth=myMonth+1
                                if(myMonth==12):
                                    endYear=endYear+1
                                    endMonth=1
                                
                                print("Generating BackTest for %s-%s in %s-%s..." % (symbol, myPeriod, myYear, myMonth))
                                backtest = BackTest(ea_name, mySet, symbol, myPeriod, datetime.date(myYear, myMonth, 1), datetime.date(endYear, endMonth, 1), deposit, uploadBT)
                                ret = backtest.run()
                                if(ret):
                                    collectBackTest(backtest, ret, myYear, myMonth, uploadBT)
                    except:
                        print("ERROR on Backtest %s-%s in %s-%s" % (symbol, myPeriod, myYear, month))



def collectBackTest(backtest, ret, year, month, uploadBT):
    mt4 = get_mt4()

    if(ret.total_trades==0):
        print("Zero trades for %s-%s in %s-%s (%s), ignoring..." % (backtest.symbol,backtest.period, year, month, backtest.set_name))
        return

    retdata = {
        "action": "register",        
        "ea": backtest.ea_md5,
        "ea_name": backtest.ea_name,
        "set_name": backtest.set_name,
        "paramsConfig": backtest.paramConfig,
        "symbol": backtest.symbol,
        "period": backtest.period,
        "ano": year,
        "mes": month,
        "graphic": backtest.gifbase64,
        "usedTickData": 1 if mt4.usedTickData else 0,
        "tickDataParams": str(mt4.tickDataParamsText),
        "broker": str(mt4.broker),
        'ticks':ret.ticks,
        "modelQuality": ret.modeling_quality_percentage,
        "sourceTick": str(mt4.sourceTick),
        "mtVersion": str(mt4.version),
        "profit": ret.profit,
        "deposit": backtest.deposit,        
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
    #print retdata

    colRetdata = []
    rowRetdata = []
    for t in retdata:
        colRetdata.append(t)
        rowRetdata.append(retdata[t])

    csvfile = os.path.join(backtest.full_report_dir,"%s.csv" % backtest.ea_name)    
    with open(csvfile, "w") as output:
        writer = csv.writer(output, delimiter =';', lineterminator='\n')    
        writer.writerow(colRetdata)
        writer.writerow(rowRetdata)

    csvfile2 = os.path.join(backtest.base_dir,"%s.csv" % backtest.ea_name)
    if not os.path.exists(csvfile2):
        with open(csvfile2, "w") as output:
            writer = csv.writer(output, delimiter =';', lineterminator='\n')
            writer.writerow(colRetdata)
            writer.writerow(rowRetdata)
    else:
        with open(csvfile2, "a") as output:
            writer = csv.writer(output, delimiter =';', lineterminator='\n')
            writer.writerow(rowRetdata)

    print("Report for %s in %s-%s finished." % (backtest.symbol, year, month))

    if(uploadBT):
        #print retdata        
        try:
            print("Uploading backtest to Server...")
            uploadBackTest(retdata)
        except:
            try:
                print("Failed, retry again in 5 seconds...")
                time.sleep(5)
                uploadBackTest(retdata)
            except:
                print("Failed, will do a last attempt in 5 seconds...")
                time.sleep(5)
                try:
                    uploadBackTest(retdata)
                except:
                    print("Failed. Cannot upload, continuing...")

def uploadBackTest(retdata):
    r = requests.post('http://167.99.227.51/bt/register.php', data=retdata)        
    result = r.json()
    if(result["success"]):
        print("Successfully uploaded to BT-Repo!")
        return True
    else:
        print("Upload FAILED! Returned a error from the server")
        print r.json()
        return False
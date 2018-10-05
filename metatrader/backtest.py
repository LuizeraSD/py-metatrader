# -*- coding: utf-8 -*-
'''
Created on 2015/01/25

@OriginAuthor: samuraitaiga
@ModifiedBy: LuizeraSD

'''
import logging
import os
import hashlib
import shutil
import requests
import re

from mt4 import get_mt4
from mt4 import DEFAULT_MT4_NAME

from __builtin__ import str

class BackTest(object):
    """
    Attributes:
      ea_name(string): ea name
      param(dict): ea parameter
      symbol(string): currency symbol. e.g.: USDJPY
      from_date(datetime.datetime): backtest from date
      to_date(datetime.datetime): backtest to date
      model(int): backtest model 
        0: Every tick
        1: Control points
        2: Open prices only
      spread(int): spread
      optimization(bool): optimization flag. optimization is enabled if True
      replace_report(bool): replace report flag. replace report is enabled if True

    """
    def __init__(self, ea_name, param, symbol, period, from_date, to_date, deposit=1000, uploadBT=False, model=0, spread=5, replace_repot=True,test_visual=False):
        self.param = param
        self.symbol = symbol
        self.period = period
        self.from_date = from_date
        self.to_date = to_date
        self.deposit = deposit
        self.uploadBT = uploadBT
        self.model = model
        self.spread = spread
        self.replace_report = replace_repot
        self.test_visual = test_visual        
        self.ea_md5 = ""
        self.paramConfig = ""
        self.base_dir = ""
        self.relative_report_dir = ""
        self.full_report_dir = ""        

        ea_name = ea_name.replace(".ex4","")
        path, ea = os.path.split(ea_name)
        if ea == "":
            ea = path
        
        self.ea_name = ea
        self.ea_fullname = ea_name
        
        mt4 = get_mt4(alias=DEFAULT_MT4_NAME)
        ea_file = os.path.join(mt4.appdata_path, 'MQL4', 'Experts', self.ea_fullname+'.ex4')
        self.ea_md5 = md5(ea_file)


    def _prepare(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
          create backtest config file and parameter file
        """
        
        self._create_tickdata_conf(alias=alias)
        self._create_ini(alias=alias)
        self._create_conf(alias=alias)
        self._create_param(alias=alias)
        self._loadParamString(alias=alias)        
    
    def _removeOldReport(self):
        #Force remove old reports if uploadBT is True
        if(self.uploadBT):
            report_file = os.path.join(self.full_report_dir, '%s.htm' % self.ea_name)
            if os.path.exists(report_file):
                os.remove(report_file)

            gif_file = os.path.join(self.full_report_dir, '%s.gif' % self.ea_name)
            if os.path.exists(gif_file):
                os.remove(gif_file)

    
    def _create_conf(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
          create config file(.conf) which is used parameter of terminal.exe
          in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\tester
          
          file contents goes to 
            TestExpert=SampleEA
            TestExpertParameters=SampleEA.set
            TestSymbol=USDJPY
            TestPeriod=M5
            TestModel=0
            TestSpread=5
            TestOptimization=true
            TestDateEnable=true
            TestFromDate=2014.09.01
            TestToDate=2015.01.05
            TestReport=SampleEA
            TestReplaceReport=false
            TestShutdownTerminal=true
			TestVisualEnable=false
        """

        #Get config file
        mt4 = get_mt4(alias=alias)
        conf_file = os.path.join(mt4.appdata_path, 'tester', '%s.conf' % self.ea_name)
        datedir = str(self.from_date.year)+"-"+str(self.from_date.month)+"-"+str(self.from_date.day)
        symbolperiod = str(self.symbol)+"-"+str(self.period)
        
        self.base_dir = os.path.join(mt4.appdata_path,'report', self.ea_name, symbolperiod)

        self.relative_report_dir = os.path.join('report', self.ea_name, symbolperiod, datedir)
        self.full_report_dir = os.path.join(mt4.appdata_path, self.relative_report_dir)
        

        if not os.path.exists(self.full_report_dir):
            os.makedirs(self.full_report_dir)

        # shutdown_terminal must be True.
        # If false, popen don't end and backtest report analyze don't start.
        shutdown_terminal = True

        with open(conf_file, 'w') as fp:
            fp.write('TestExpert=%s\n' % self.ea_fullname)
            fp.write('TestExpertParameters=%s.set\n' % self.ea_name)
            fp.write('TestSymbol=%s\n' % self.symbol)
            fp.write('TestModel=%s\n' % self.model)
            fp.write('TestPeriod=%s\n' % self.period)
            fp.write('TestSpread=%s\n' % self.spread)
            fp.write('TestOptimization=%s\n' % str(self.optimization).lower())
            fp.write('TestDateEnable=true\n')
            fp.write('TestFromDate=%s\n' % self.from_date.strftime('%Y.%m.%d'))
            fp.write('TestToDate=%s\n' % self.to_date.strftime('%Y.%m.%d'))
            #fp.write('TestReport=%s.htm\n' % self.ea_name)
            fp.write('TestReport=%s\\%s.htm\n' % (self.relative_report_dir, self.ea_name))
            fp.write('TestReplaceReport=%s\n' % str(self.replace_report).lower())
            fp.write('TestVisualEnable=%s\n' % str(self.test_visual).lower())
            fp.write('TestShutdownTerminal=%s\n' % str(shutdown_terminal).lower())
    
    def _loadParamString(self, alias=DEFAULT_MT4_NAME):
        mt4 = get_mt4(alias=alias)
        param_file = os.path.join(mt4.appdata_path, 'tester', '%s.set' % self.ea_name)

        setString = ""
        with open(param_file) as f:
            for line in f:
                if not (re.search(r'^.+\,[F,1,2,3]=', line)):
                    setString += line

        setString = setString.splitlines()
        self.paramConfig = ";".join(setString)

    def _create_param(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
          create ea parameter file(.set) in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\tester
        Args:
          ea_name(string): ea name
        """
        mt4 = get_mt4(alias=alias)
        param_file = os.path.join(mt4.appdata_path, 'tester', '%s.set' % self.ea_name)

        if(isinstance(self.param, basestring)):
            if os.path.exists(self.param):
                shutil.copy2(self.param, param_file)
                return        
        

        with open(param_file, 'w') as fp:
            for k in self.param:
                values = self.param[k].copy()
                value = values.pop('value')
                fp.write('%s=%s\n' % (k, value))
                if self.optimization:
                    if values.has_key('max') and values.has_key('interval'):
                        fp.write('%s,F=1\n' % k)
                        fp.write('%s,1=%s\n' % (k, value))
                        interval = values.pop('interval')
                        fp.write('%s,2=%s\n' % (k,interval))
                        maximum = values.pop('max')
                        fp.write('%s,3=%s\n' % (k,maximum))
                    else:
                        # if this value won't be optimized, write unused dummy data for same format.
                        fp.write('%s,F=0\n' % k)
                        fp.write('%s,1=0\n' % k)
                        fp.write('%s,2=0\n' % k)
                        fp.write('%s,3=0\n' % k)
                else:
                    if type(value) == str:
                        # this ea arg is string. then don't write F,1,2,3 section in config
                        pass
                    else:
                        # write unused dummy data for same format.
                        fp.write('%s,F=0\n' % k)
                        fp.write('%s,1=0\n' % k)
                        fp.write('%s,2=0\n' % k)
                        fp.write('%s,3=0\n' % k)

    def _create_ini(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
          create config file(.ini) which is used for the config EA
          in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\tester          
        """
        
        mt4 = get_mt4(alias=alias)
        ini_file = os.path.join(mt4.appdata_path, 'tester', '%s.ini' % self.ea_name)

        with open(ini_file, 'w') as fp:
            fp.write('<common>\n')
            fp.write('positions=2\n')
            fp.write('deposit=%s\n' % self.deposit)
            fp.write('currency=USD\n')
            fp.write('fitnes=0\n')
            fp.write('genetic=1\n')
            fp.write('</common>\n') 

    def _create_tickdata_conf(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
            create tds.config which is used for the backtest
            in %APPDATA%\\MetaQuotes\\Terminal\\<UUID>\\config
        """

        mt4 = get_mt4(alias=alias)
        conf_file = os.path.join(mt4.appdata_path, 'config', 'tds.config')        

        with open(conf_file, 'w') as fp:            
            fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fp.write('<configuration>\n')
            fp.write('  <configSections>\n')
            fp.write('      <section name="global" type="System.Configuration.AppSettingsSection, System.Configuration, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" />\n')
            fp.write('  </configSections>\n')
            fp.write('  <global>\n')
            fp.write('      <add key="UseTickDataEnabled" value="True" />\n')
            fp.write('      <add key="Source" value="Dukascopy" />\n')
            fp.write('      <add key="GMTOffset" value="2" />\n')
            fp.write('      <add key="DST" value="1" />\n')
            fp.write('      <add key="UseVariableSpread" value="True" />\n')
            fp.write('      <add key="SlippageEnabled" value="True" />\n')

            fp.write('      <add key="ReproducibleSlippage" value="True" />\n')
            fp.write('      <add key="OptimizationSlippage" value="False" /><add key="LimitOrderSlippage" value="True" />\n')
            fp.write('      <add key="StopOrderSlippage" value="True" /><add key="SlOrderSlippage" value="True" /><add key="TpOrderSlippage" value="True" />\n')
            fp.write('      <add key="LatencyBasedSlippage" value="True" /><add key="MinimumSlippageDelay" value="250" /><add key="MaximumSlippageDelay" value="250" />\n')
            fp.write('      <add key="MinimumPendingSlippageDelay" value="125" /><add key="MaximumPendingSlippageDelay" value="125" />\n')

            fp.write('      <add key="DealerStyleSlippage" value="True" />\n')
            fp.write('      <add key="MaxFavorableSlippage" value="5" /><add key="MaxUnfavorableSlippage" value="10" /><add key="UseCustomSlippageChance" value="False" />\n')
            fp.write('      <add key="CustomSlippageChance" value="100" /><add key="UseCustomFavorableChance" value="False" /><add key="FavorableSlippageChance" value="50" />\n')

            fp.write('      <add key="StandardDeviationSlippage" value="False" />\n')
            fp.write('      <add key="SlippageMean" value="0" /><add key="SlippageStDev" value="30" />\n')
            fp.write('      <add key="OverrideMinLot" value="False" />\n')
            fp.write('      <add key="MinLot" value="0.01" />\n')
            fp.write('      <add key="OverrideMaxLot" value="False" />\n')
            fp.write('      <add key="MaxLot" value="1000" />\n')
            fp.write('      <add key="OverrideLotStep" value="False" />\n')
            fp.write('      <add key="LotStep" value="0.1" />\n')
            fp.write('      <add key="OverrideLeverage" value="False" />\n')
            fp.write('      <add key="Leverage" value="500" />\n')
            fp.write('      <add key="OverrideBaseCommission" value="False" />\n')
            fp.write('      <add key="BaseCommission" value="0" />\n')
            fp.write('      <add key="OverrideCommissionType" value="False" />\n')
            fp.write('      <add key="CommissionType" value="1" />\n')
            fp.write('      <add key="OverrideCommissionPer" value="False" />\n')
            fp.write('      <add key="CommissionPer" value="0" />\n')
            fp.write('      <add key="BarsToPrefix" value="100" />\n')
            fp.write('      <add key="LiveExecutionStoploss" value="True" />\n')
            fp.write('      <add key="LiveExecutionTakeprofit" value="True" />\n')
            fp.write('      <add key="LiveExecutionStop" value="True" />\n')
            fp.write('      <add key="LiveExecutionLimit" value="True" />\n')
            fp.write('      <add key="UseFxtDuringOptimization" value="True" /><add key="SaveFxtWhenBacktesting" value="False" />\n')
            fp.write('      <add key="SaveHstFilesWhenSavingFxt" value="False" /><add key="SaveHstFilesWhenBacktesting" value="False" />\n')
            fp.write('      <add key="ReadOnlyFxtEncountered" value="3" /><add key="DeleteFxtAfterOptimization" value="True" />\n')
            fp.write('      <add key="AdjustSlTpAfterSlippage" value="False" /><add key="EnforceSlippage" value="False" />\n')
            fp.write('      <add key="SymbolSlippage" value="False" />\n')
            fp.write('  </global>\n')
            fp.write('</configuration>')

    def _get_conf_abs_path(self, alias=DEFAULT_MT4_NAME):
        mt4 = get_mt4(alias=alias)
        conf_file = os.path.join(mt4.appdata_path, 'tester', '%s.conf' % self.ea_name)
        return conf_file

    def checkIfExists(self, alias=DEFAULT_MT4_NAME):
        
        #Dont make the check if upload its disabled
        if(not self.uploadBT):
            return False

        checkData = {
            "action":"check",
            "ea":self.ea_md5,
            "paramsConfig": self.paramConfig,
            "symbol": self.symbol,
            "period": self.period,
            "ano": self.from_date.year,
            "mes": self.from_date.month
        } 
        #print checkData

        r = requests.post('http://167.99.227.51/bt/check.php', data=checkData)
        result = r.json()
        #print result
        if "exists" in result:
            print("Backtest already exists for %s in %s-%s, ignoring..." % (self.symbol, self.from_date.year, self.from_date.month))
            return True
        
        #Does not exist
        return False


    def run(self, alias=DEFAULT_MT4_NAME):
        """
        Notes:
          run backtest
        """
        from report import BacktestReport

        self.optimization = False

        self._prepare(alias=alias)
        if(not self.checkIfExists()):
            self._removeOldReport()
            bt_conf = self._get_conf_abs_path(alias=alias)
        
            mt4 = get_mt4(alias=alias)
            mt4.run(self.ea_name, conf=bt_conf)
        
            ret = BacktestReport(self)
            return ret

    def optimize(self, alias=DEFAULT_MT4_NAME):
        """
        """
        from report import OptimizationReport

        self.optimization = True
        self._prepare(alias=alias)
        bt_conf = self._get_conf_abs_path(alias=alias)
    
        mt4 = get_mt4(alias=alias)
        mt4.run(self.ea_name, conf=bt_conf)
        
        ret = OptimizationReport(self)
        return ret        


def load_from_file(dsl_file):
    pass

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
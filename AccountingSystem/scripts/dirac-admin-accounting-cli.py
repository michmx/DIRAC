#!/usr/bin/env python
########################################################################
# $HeadURL$
# File :   dirac-admin-accounting-cli
# Author : Adria Casajus
########################################################################
"""
  Command line administrative interface to DIRAC Accounting DataStore Service
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
__RCSID__ = "$Id$"

from DIRAC.Core.Base import Script

Script.localCfg.addDefaultEntry("LogLevel", "info")
Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s [option|cfgfile] ...' % Script.scriptName, ]))
Script.parseCommandLine()

from DIRAC.AccountingSystem.Client.AccountingCLI import AccountingCLI

if __name__ == "__main__":
  acli = AccountingCLI()
  acli.start()

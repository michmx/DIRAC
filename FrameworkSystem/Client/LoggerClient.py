""" This file contains the methods for accessing the Messages Stored in the LoggingDB;
    getMessagesByDate()
    getMessagesBySite()
    getMessagesByUser()
    getMessagesByFixedText()
    getMessagesByGroup()
    getMessagesBySiteNode()
    getMessages()
    getCountMessages()
    getGroupedMessages()
    getGroups()
    getSites()
    getSystems()
    getSubSystems()
    getFixedTextStrings()
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__RCSID__ = "$Id$"


from DIRAC import S_OK
from DIRAC.Core.DISET.RPCClient import RPCClient


class LoggerClient:

  def getMessagesByDate(self, beginDate=None, endDate=None,
                        startRecord=0, maxRecords=100):
    """ Query the database for all the messages between two given dates.
        If no date is provided then the records returned are those generated
        during the last 24 hours.
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'beginDate': beginDate, 'endDate': endDate},
                                    [], startRecord, maxRecords)

  def getMessagesByFixedText(self, texts, beginDate=None, endDate=None,
                             startRecord=0, maxRecords=100):
    """ Query the database for all messages whose fixed part match 'texts'
        that were generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'FixedTextString': texts,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessagesBySystem(self, system, beginDate=None, endDate=None,
                          startRecord=0, maxRecords=100):
    """ Query the database for all messages generated by system(s) 'system'
        that were generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'SystemName': system,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessagesBySite(self, site, beginDate=None, endDate=None,
                        startRecord=0, maxRecords=100):
    """ Query the database for all messages generated by 'site' that were
        generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'SiteName': site,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessagesByUser(self, userDN, beginDate=None, endDate=None,
                        startRecord=0, maxRecords=100):
    """ Query the database for all messages generated by the user: 'userDN'
        that were generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'OwnerDN': userDN,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessagesByGroup(self, group, beginDate=None, endDate=None,
                         startRecord=0, maxRecords=100):
    """ Query the database for all messages generated by the group 'Group'
        that were generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'OwnerGroup': group,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessagesBySiteNode(self, node, beginDate=None, endDate=None,
                            startRecord=0, maxRecords=100):
    """ Query the database for all messages generated at 'node' that were
        generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    return loggingQuery.getMessages({'ClientFQDN': node,
                                     'beginDate': beginDate,
                                     'endDate': endDate}, [],
                                    startRecord, maxRecords)

  def getMessages(self, showFields=[], conds={}, beginDate=None,
                  endDate=None, startRecord=0, maxRecords=100):
    """ Query the database for all messages satisfying 'conds' that were
        generated between beginDate and endDate
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)

    conds['beginDate'] = beginDate
    conds['endDate'] = endDate
    for key in showFields:
      if key not in conds:
        conds[key] = None

    result = loggingQuery.getMessages(conds, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    if showFields:
      columns = result['Value']['ParameterNames']

      fieldIndex = []
      for field in showFields:
        fieldIndex.append(columns.index(field))

      retRecords = []
      for record in result['Value']['Records']:
        retRecords.append([record[index] for index in fieldIndex])
      result['Value']['ParameterNames'] = showFields

      result['Value']['Records'] = retRecords

    return result

  def getCountMessages(self, conds={}, beginDate=None, endDate=None,
                       startRecord=0, maxRecords=100):
    """ Query the database for the number of messages that match 'conds' and
        were generated between beginDate and endDate. If no condition is
        provided it returns the total number of messages present in the
        database
    """
    conds['beginDate'] = beginDate
    conds['endDate'] = endDate

    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)

    return loggingQuery.getCountMessages(conds, {}, startRecord, maxRecords)

  def getGroupedMessages(self, fieldList=[], conds={}, groupField=None,
                         orderList=None, beginDate=None, endDate=None,
                         startRecord=0, maxRecords=100):
    """ Query the database for the number of messages that match 'conds' and
        were generated between beginDate and endDate. If no condition is
        provided it returns the total number of messages present in the
        database
    """
    conds['beginDate'] = beginDate
    conds['endDate'] = endDate
    if groupField:
      conds['groupField'] = groupField
    for key in fieldList:
      if key not in conds:
        conds[key] = None

    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getGroupedMessages(conds, orderList, startRecord, maxRecords)
    if not result['OK']:
      return result

    if fieldList:
      columnNames = result['Value']['ParameterNames']

      fieldIndex = []
      for field in fieldList:
        fieldIndex.append(columnNames.index(field))

      records = result['Value']['Records']

      retRecords = []
      for record in records:
        retRecords.append([record[index] for index in fieldIndex])
      result['Value']['ParameterNames'] = fieldList

      result['Value']['Records'] = retRecords

    return result

  def getSites(self, startRecord=0, maxRecords=100):
    """ Returns all the sites stored in the Logging DB
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getSites({}, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    return S_OK(result['Value']['Records'])

  def getSystems(self, startRecord=0, maxRecords=100):
    """ Returns all the systems stored in the Logging DB
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getSystems({}, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    return S_OK(result['Value']['Records'])

  def getSubSystems(self, startRecord=0, maxRecords=100):
    """ Returns all the subsystems stored in the Logging DB
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getSubSystems({}, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    return S_OK(result['Value']['Records'])

  def getGroups(self, startRecord=0, maxRecords=100):
    """ Returns all the groups stored in the Logging DB
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getGroups({}, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    return S_OK(result['Value']['Records'])

  def getFixedTextStrings(self, startRecord=0, maxRecords=100):
    """ Returns all the fixed strings of logging messages stored in the Logging DB
    """
    loggingQuery = RPCClient('Framework/SystemLoggingReport', timeout=10)
    result = loggingQuery.getFixedTextStrings({}, [], startRecord, maxRecords)
    if not result['OK']:
      return result

    return S_OK(result['Value']['Records'])

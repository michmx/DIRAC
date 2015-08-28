"""TransformationInfo class to be used by ILCTransformation System"""
__RCSID__ = "$Id$"

from DIRAC import gLogger, S_OK
from DIRAC.Core.Workflow.Workflow import fromXMLString

from ILCDIRAC.Core.Utilities.ProductionData import constructProductionLFNs

from DIRAC.TransformationSystem.Utilities.JobInfo import ENABLED


class TransformationInfo(object):
  """ hold information about transformations """

  def __init__(self, transformationID, transName, tClient, jobDB, logDB):
    self.log = gLogger.getSubLogger("TInfo")
    self.tID = transformationID
    self.transName = transName
    self.tClient = tClient
    self.jobDB = jobDB
    self.logDB = logDB
    self.olist = self.__getOutputList()

  def __getTransformationWorkflow(self):
    """return the workflow for the transformation"""
    res = self.tClient.getTransformationParameters(self.tID, ['Body'])
    if not res['OK']:
      self.log.error('Could not get Body from TransformationDB')
      return res
    body = res['Value']
    workflow = fromXMLString(body)
    workflow.resolveGlobalVars()
    return S_OK(workflow)

  def __getOutputList(self):
    """Get list of outputfiles"""
    resWorkflow = self.__getTransformationWorkflow()
    if not resWorkflow['OK']:
      self.log.error("Failed to get Transformation Workflow")
      raise RuntimeError("Failed to get outputlist")

    workflow = resWorkflow['Value']
    olist = []
    for step in workflow.step_instances:
      param = step.findParameter('listoutput')
      if not param:
        continue
      olist.extend(param.value)
    return olist

  def getOutputFiles(self, taskID):
    """returns list of expected lfns for given task"""
    commons = {'outputList': self.olist,
               'PRODUCTION_ID': int(self.tID),
               'JOB_ID': int(taskID),
               }
    resFiles = constructProductionLFNs(commons)
    if not resFiles['OK']:
      raise RuntimeError("Failed to create productionLFNs")
    expectedlfns = resFiles['Value']['ProductionOutputData']
    return expectedlfns

  def checkTasksStatus(self):
    """Check the status for the task of given transformation and taskID"""

    res = self.tClient.getTransformationFiles(condDict={'TransformationID': self.tID})
    if not res['OK']:
      raise RuntimeError("Failed to get transformation tasks", res['Message'])

    tasksDict = {}
    for task in res['Value']:
      taskID = task['TaskID']
      lfn = task['LFN']
      status = task['Status']
      fileID = task['FileID']
      tasksDict[taskID] = dict(FileID=fileID, LFN=lfn, Status=status)

    return tasksDict

  def setJobDone(self, job):
    """ set the taskID to Done"""
    if not ENABLED:
      return
    taskID = job.taskID
    res = self.tClient.setTaskStatus(self.transName, taskID, "Done")
    if not res['OK']:
      raise RuntimeError("Failed updating task status")
    self.__updateJobStatus("Done", "Job Finished Successfully")

  def setJobFailed(self, job):
    """ set the taskID to Done"""
    if not ENABLED:
      return
    taskID = job.taskID
    res = self.tClient.setTaskStatus(self.transName, taskID, "Failed")
    if not res['OK']:
      raise RuntimeError("Failed updating task status")
    self.__updateJobStatus("Failed", "Job forced to Failed")

  def setInputUnused(self, job):
    """set the inputfile to unused"""
    self.__setInputStatus(job, "Unused")

  def setInputProcessed(self, job):
    """set the inputfile to processed"""
    self.__setInputStatus(job, "Processed")

  def __setInputStatus(self, job, status):
    """set the input file to status"""
    if ENABLED:
      result = self.tClient.setFileStatusForTransformation(self.tID, status, [job.inputFile], force=True)
      if not result['OK']:
        gLogger.error("Failed updating status", result['Message'])
        raise RuntimeError("Failed updating file status")

  def __updateJobStatus(self, jobID, status, minorstatus=None):
    """ This method updates the job status in the JobDB
    """
    self.log.verbose("self.jobDB.setJobAttribute(%s,'Status','%s',update=True)" % (jobID, status))

    if ENABLED:
      result = self.jobDB.setJobAttribute(jobID, 'Status', status, update=True)
    else:
      return S_OK('DisabledMode')

    if result['OK']:
      if minorstatus:
        self.log.verbose("self.jobDB.setJobAttribute(%s,'MinorStatus','%s',update=True)" % (jobID, minorstatus))
        result = self.jobDB.setJobAttribute(jobID, 'MinorStatus', minorstatus, update=True)

    if not minorstatus:  # Retain last minor status for stalled jobs
      result = self.jobDB.getJobAttributes(jobID, ['MinorStatus'])
      if result['OK']:
        minorstatus = result['Value']['MinorStatus']

    logStatus = status
    result = self.logDB.addLoggingRecord(jobID, status=logStatus, minor=minorstatus, source='DataRecoveryAgent')
    if not result['OK']:
      self.log.warn(result)

    return result

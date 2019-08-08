import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import argparse
import os
import evalOneSubmissionD4
import numpy as np
import pandas as pd
import csv
import string
import time
import datetime
import pickle
from scipy.stats import rankdata
# from configEval import *
from datetime import datetime

parser = argparse.ArgumentParser(usage='python3 leaderboardRunAll.py', description=r'''
  Script evaluates new D4 entires and updates a live leaderboard table

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk

''')

parser.add_argument('--runPart', dest='runPart', default='RR',
                   help='which part of the script to run. Usually either LR or RR, where '
                        'LR means "load first part, run second part" while RR means run both parts')

parser.add_argument('--fast', dest='fast', type=int, default=1,
                   help='whether to run a fast version of the leaderboard.')

args = parser.parse_args()

TOKEN = open(os.path.expanduser('~/.dropboxTadpoleToken'), 'r').read()[:-1]




class DropboxObj:

  def __init__(self):
    self.TOKEN = TOKEN
    self.dbx = self.createDropboxInstance()


  def createDropboxInstance(self):
    # Check for an access token

    TOKEN = self.TOKEN
    if (len(TOKEN) == 0):
      sys.exit("ERROR: Looks like you didn't add your access token. "
          "Open up backupuploadDropboxAPIv2.py in a text editor and "
          "paste in your token in line 14.")

    # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")

    dbx = dropbox.Dropbox(TOKEN)
    # Check that the access token is valid
    try:
      dbx.users_get_current_account()
    except AuthError as err:
      sys.exit("ERROR: Invalid access token; try re-generating an "
            "access token from the app console on the web.")

    return dbx

  # Uploads contents of LOCALFILE to Dropbox
  def upload(self, fullPathLocal, fullPathRemote):
    print('fullPathRemote', fullPathRemote)
    with open(fullPathLocal, 'rb') as f:
      # We use WriteMode=overwrite to make sure that the settings in the file
      # are changed on upload
      print("Uploading " + fullPathLocal + " to Dropbox as " + fullPathRemote + "...")
      try:
        self.dbx.files_upload(f.read(), fullPathRemote, mode=WriteMode('overwrite'))
      except ApiError as err:
        # This checks for the specific error where a user doesn't have
        # enough Dropbox space quota to upload this file
        if (err.error.is_path() and
              err.error.get_path().error.is_insufficient_space()):
          sys.exit("ERROR: Cannot back up; insufficient space.")
        elif err.user_message_text:
          print(err.user_message_text)
          sys.exit()
        else:
          print(err)
          sys.exit()

  # Download contents of LOCALFILE to Dropbox
  def download(self, localPath, remotePath):

    print("Downloading " + remotePath + " from Dropbox to " + localPath + " ...")
    try:
      self.dbx.files_download_to_file(localPath, remotePath)
    except ApiError as err:
      if err.user_message_text:
        print(err.user_message_text)
        sys.exit()
      else:
        print(err)
        sys.exit()

  def list_folder(self, folder, subfolder):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
      path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
      res = self.dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
      print('Folder listing failed for', path, '-- assumed empty:', err)
      return {}
    else:
      rv = {}
      for entry in res.entries:
        rv[entry.name] = entry
      return rv



def formatStrRemoveNan(strFmt, n, replaceStr = '-'):
  if np.isnan(n):
    return replaceStr
  else:
    return strFmt % n


def writeHTMLtable(evalResults, htmlFile):
  html = open(htmlFile, 'w')

  ## Add this manually in skeleton13.css in the dropbox folder under ProAD/public_html/css
  manuallyAddToPageCssStyle = r'''
  <style>
tr.d0 td {
  background-color: #ffffff;
  color: black;
  max-width: 30px;
  overflow: wrap;
  text-overflow: ellipsis;
  word-wrap: break-word;
}
tr.d1 td {
  background-color: #ffffff;
  color: black;
  max-width: 30px;
  overflow: wrap;
  text-overflow: ellipsis;
  word-wrap: break-word;
}
</style>
'''

  text = 'Table last updated on %s. Update frequency: every 5 minutes' % (datetime.now().strftime('%Y-%m-%d %H:%M (BST +0)'))
  text += '<table  class="table table-dark table-striped table-hover table-sm dataTable sortable" style="align:center"  >\n'

  text += r'''
  <thead>
       <tr class="d4HeaderLive">
           <th style="width:50px"> RANK<br></th>
           <th style="width:80px"> FILE NAME</th>
           <th style="width:50px"> MAUC RANK</th>
           <th style="width:50px"> MAUC</th>
           <th style="width:50px"> BCA</th>
           <th style="width:50px"> ADAS RANK</th>
           <th style="width:50px"> ADAS MAE</th>
           <th style="width:50px"> ADAS WES</th>
           <th style="width:50px"> ADAS CPA</th>
           <th style="width:50px"> VENTS RANK</th>
           <th style="width:50px"> VENTS MAE</th>
           <th style="width:50px"> VENTS WES</th>
           <th style="width:50px"> VENTS CPA</th> 	
           <th style="width:80px"> DATE</th> 	
           
     </tr>
   </thead>

  '''

  colsToShow = ['RANK MAUC', 'MAUC', 'BCA',
    'RANK ADAS', 'ADAS MAE', 'ADAS WES', 'ADAS CPA', 'RANK VENTS', 'VENTS MAE', 'VENTS WES', 'VENTS CPA']
  text += '<tbody>'
  evalResultsPerm = evalResults.loc[:, colsToShow]
  formatStrsMeasures = ['%.1f', '%.3f', '%.3f', '%.1f', '%.2f', '%.2f', '%.2f', '%.1f', '%.2f', '%.2f', '%.2f', '%s']
  # print(list(zip(formatStrsMeasures, evalResultsPerm.loc[0, :])))
  # asda
  for f in range(evalResults['MAUC'].shape[0]):
    # text += '\n   <tr class="d%d">' % (f % 2)
    text += '\n   <tr class="rowD4Live">'
    text += '<td>%s</td>' % formatStrRemoveNan('%.1f',evalResults['RANK'].iloc[f], replaceStr='999')
    text += '<td>%s</td><td>' % evalResults['FileName'].iloc[f]
    text += '</td><td>'.join(
      [formatStrRemoveNan(strFmt,n) for strFmt, n in zip(formatStrsMeasures, evalResultsPerm.loc[f, :])])
    text += '<td class="rowD4LiveDate">%s</td>' % evalResults.loc[f, 'Date'].strftime('%Y-%m-%d %H:%M')
    text += '</td></tr>\n'

  text += '</tbody>\n</table>'

  with open(htmlFile, "w") as f:
    f.write(text)

def convRankToStr(rankVector):
  unqRanks = np.unique(rankVector)
  rankVectorStr = np.empty(rankVector.shape[0], object)
  rankVectorStr[np.isnan(rankVector)] = '-'
  for r in range(unqRanks.shape[0]):
    rCurr = unqRanks[r]
    if not np.isnan(rCurr):
      idxCurrRank = np.where(np.abs(rankVector - rCurr) < 0.001)[0]
      sizeRangeHalf = float(idxCurrRank.shape[0] - 1)/2
      if sizeRangeHalf > 0.49:
        rankVectorStr[idxCurrRank] = '%d-%d' % (round(rCurr-sizeRangeHalf), round(rCurr+sizeRangeHalf))
      else:
        rankVectorStr[idxCurrRank] = '%d' % rCurr

  return rankVectorStr

def addOtherStatsTable(resTable):

  notNanMaskMAUC = np.logical_not(np.isnan(np.array(resTable.loc[:, 'MAUC'].values.reshape(-1), float)))
  notNanMaskADAS = np.logical_not(np.isnan(np.array(resTable.loc[:, 'ADAS MAE'].values.reshape(-1), float)))
  notNanMaskVents = np.logical_not(np.isnan(np.array(resTable.loc[:, 'VENTS MAE'].values.reshape(-1), float)))

  rankMAUC = np.nan * np.ones(resTable.shape[0])
  rankADAS = np.nan * np.ones(resTable.shape[0])
  rankVENTS = np.nan * np.ones(resTable.shape[0])
  rankMAUC[notNanMaskMAUC] = rankdata(rankdata(-resTable.loc[:, 'MAUC'].values.reshape(-1)[notNanMaskMAUC],
    method='average'), method='average')
  rankADAS[notNanMaskADAS] = rankdata(rankdata(resTable.loc[:, 'ADAS MAE'].values.reshape(-1)[notNanMaskADAS], method='average'),
                      method='average')
  rankVENTS[notNanMaskVents] = rankdata(rankdata(resTable.loc[:, 'VENTS MAE'].values.reshape(-1)[notNanMaskVents], method='average'),
                       method='average')

  rankBCA = np.nan * np.ones(resTable.shape[0])
  rankAdasWes = np.nan * np.ones(resTable.shape[0])
  rankAdasCpa = np.nan * np.ones(resTable.shape[0])
  rankVentsWes = np.nan * np.ones(resTable.shape[0])
  rankVentsCpa = np.nan * np.ones(resTable.shape[0])
  rankBCA[notNanMaskMAUC] = rankdata(rankdata(-resTable.loc[:, 'BCA'].values.reshape(-1)[notNanMaskMAUC],
    method='average'), method='average')
  rankAdasWes[notNanMaskADAS] = rankdata(rankdata(resTable.loc[:, 'ADAS WES'].values.reshape(-1)[notNanMaskADAS], method='average'), method='average')
  rankAdasCpa[notNanMaskADAS] = rankdata(rankdata(resTable.loc[:, 'ADAS CPA'].values.reshape(-1)[notNanMaskADAS], method='average'), method='average')
  rankVentsWes[notNanMaskVents] = rankdata(rankdata(resTable.loc[:, 'VENTS WES'].values.reshape(-1)[notNanMaskVents], method='average'), method='average')
  rankVentsCpa[notNanMaskVents] = rankdata(rankdata(resTable.loc[:, 'VENTS CPA'].values.reshape(-1)[notNanMaskVents], method='average'), method='average')


  rankOrder = np.nan * np.ones(resTable.shape[0])

  rankSum = rankMAUC + rankADAS + rankVENTS
  nnSumMask = np.logical_not(np.isnan(rankSum))
  rankOrder[nnSumMask] = rankdata(rankSum[nnSumMask], method='average')  # make them start from 1
  print('rankOrder', rankOrder)

  resTable.loc[:, 'RANK'] = rankOrder
  resTable.loc[:, 'RANK MAUC'] = rankMAUC
  resTable.loc[:, 'RANK ADAS'] = rankADAS
  resTable.loc[:, 'RANK VENTS'] = rankVENTS

  resTable.loc[:, 'RANK BCA'] = rankBCA
  resTable.loc[:, 'RANK ADAS WES'] = rankAdasWes
  resTable.loc[:, 'RANK ADAS CPA'] = rankAdasCpa
  resTable.loc[:, 'RANK VENTS WES'] = rankVentsWes
  resTable.loc[:, 'RANK VENTS CPA'] = rankVentsCpa

  resTable.loc[:, 'RANK STR'] = convRankToStr(rankOrder)
  resTable.loc[:, 'RANK MAUC STR'] = convRankToStr(rankMAUC)
  resTable.loc[:, 'RANK ADAS STR'] = convRankToStr(rankADAS)
  resTable.loc[:, 'RANK VENTS STR'] = convRankToStr(rankVENTS)

  resTable.sort_values(by=['RANK', 'RANK MAUC'], ascending=True,inplace=True)
  resTable.reset_index(drop=True, inplace=True)

  resTable.RANK = resTable.RANK.astype(float)

  # round the numbers for easy visualisation
  roundDict = {'MAUC': 3, 'BCA': 3, 'ADAS MAE': 2, 'VENTS MAE': 4,
               'ADAS WES': 2, 'VENTS WES': 4, 'ADAS CPA': 2, 'VENTS CPA': 2}
  for c in roundDict.keys():
    resTable[c] = resTable[c].astype(float).round(roundDict[c])

  return resTable


def applyChangesDf(res, calcRandomBest=False):
  ''' add extra names to identify different submissions '''

  res.loc[np.logical_and(res.FileName == 'EMC1', np.in1d(res.ID, [1, 5])), 'FileName'] = 'EMC1-Std'
  res.loc[np.logical_and(res.FileName == 'EMC1', np.in1d(res.ID, [2,3,4,6,7,8])), 'FileName'] = 'EMC1-Custom'

  res.loc[np.logical_and(res.FileName == 'DIKU-GeneralisedLog', np.in1d(res.ID, [1, 5])), 'FileName'] = 'DIKU-GeneralisedLog-Std'
  res.loc[np.logical_and(res.FileName == 'DIKU-GeneralisedLog', np.in1d(res.ID, [3, 7])), 'FileName'] = 'DIKU-GeneralisedLog-Custom'
  res.loc[np.logical_and(res.FileName == 'DIKU-ModifiedLog', np.in1d(res.ID, [1, 5])), 'FileName'] = 'DIKU-ModifiedLog-Std'
  res.loc[np.logical_and(res.FileName == 'DIKU-ModifiedLog', np.in1d(res.ID, [3, 7])), 'FileName'] = 'DIKU-ModifiedLog-Custom'
  res.loc[np.logical_and(res.FileName == 'DIKU-ModifiedMri', np.in1d(res.ID, [1, 5])), 'FileName'] = 'DIKU-ModifiedMri-Std'
  res.loc[np.logical_and(res.FileName == 'DIKU-ModifiedMri', np.in1d(res.ID, [3, 7])), 'FileName'] = 'DIKU-ModifiedMri-Custom'

  # scale ventricles to show them as percentage points
  res.loc[:, 'VENTS MAE'] *= 100
  res.loc[:, 'VENTS WES'] *= 100


  return res


def getD2D3deepCopy(res):
  resD2 = res[res.PredictionSet == 'D2'].copy(deep=True)
  resD3 = res[np.in1d(res.PredictionSet, ['D3'])].copy(deep=True)
  resDCustom = res[np.in1d(res.PredictionSet, ['Custom'])].copy(deep=True)

  resD2.sort_values(by=['MAUC', 'BCA'], ascending=False, inplace=True)
  resD2.reset_index(drop=True, inplace=True)
  resD3.sort_values(by=['MAUC', 'BCA'], ascending=False, inplace=True)
  resD3.reset_index(drop=True, inplace=True)
  resDCustom.sort_values(by=['MAUC', 'BCA'], ascending=False, inplace=True)
  resDCustom.reset_index(drop=True, inplace=True)

  return resD2, resD3, resDCustom

def evalD4LeaderboardSubmissions(resDf, evalResFile, fileNameTag, predictionSet):

  fileListAll = ldbDropbox.list_folder(uploadsFldRemote, '/')
  fileNamesLong = [x for x in fileListAll.keys() if (x.startswith(fileNameTag) and x[-4:] == '.csv')]
  fileNamesLong.sort()
  print('fileNamesLong ', fileNamesLong)

  os.system('mkdir -p %s' % submissionsFld)
  nrEntries = len(fileNamesLong)

  fileNamesShort = [f.split('.')[0][len(fileNameTag):] for f in fileNamesLong]

  tableColumns = ('TeamName', 'PredictionSet', 'FileName', 'ID', 'RANK',
       'RANK MAUC', 'RANK ADAS', 'RANK VENTS', 'MAUC', 'BCA', 'ADAS MAE',
       'VENTS MAE', 'ADAS WES', 'VENTS WES', 'ADAS CPA', 'VENTS CPA',
       'Comments', 'Date')

  listSubIndToProc = []
  for e, f in enumerate(fileNamesShort):
    possibleIndexOfExistingEntry = \
      np.where(np.logical_and(resDf['FileName'] == f, resDf['PredictionSet'] == predictionSet))[0]
    if possibleIndexOfExistingEntry.shape[0] == 0:
      listSubIndToProc += [e]

  if len(listSubIndToProc) > 0:

    nanSeries = pd.DataFrame(np.nan, index=range(len(listSubIndToProc)), columns=tableColumns)
    nrEntriesSoFar = resDf.shape[0]
    res = resDf.append(nanSeries, ignore_index=True)


    d4Df = pd.read_csv(d4File)
    d4Df['CognitiveAssessmentDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['CognitiveAssessmentDate']]
    d4Df['ScanDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['ScanDate']]
    mapping = {'CN': 0, 'MCI': 1, 'AD': 2}
    d4Df.replace({'Diagnosis': mapping}, inplace=True)

    nrEntriesSoFar = resDf.shape[0]
    entryToAddIndex = nrEntriesSoFar
    for f in listSubIndToProc:
      fileNameLong = fileNamesLong[f]
      fileNameShort = fileNamesShort[f]
      # print('teamname ', fileNameShort)
      remotePath = '%s/%s' % (uploadsFldRemote, fileNameLong)
      localPath = '%s/%s' % (submissionsFld, fileNameLong)
      ldbDropbox.download(localPath, remotePath)

      metadataFileRemote = ldbDropbox.dbx.files_get_metadata(remotePath)


      print('Evaluating %s' % fileNameLong)
      forecastDf = pd.read_csv(localPath)
      try:
        resDf.loc[entryToAddIndex, 'TeamName'] = fileNamesShort[f]
        resDf.loc[entryToAddIndex, 'FileName'] = fileNamesShort[f]
        resDf.loc[entryToAddIndex, 'ID'] = 1
        resDf.loc[entryToAddIndex, 'PredictionSet'] = predictionSet
        resDf.loc[entryToAddIndex, 'Date'] = metadataFileRemote.server_modified

        resDf.loc[entryToAddIndex, 'MAUC': 'VENTS CPA'] = \
          evalOneSubmissionD4.evalOneSub(d4Df, forecastDf)

        entryToAddIndex += 1
      except :
        print('Error while processing submission %s' % fileNameLong)
        pass


      # if not np.isnan(resDf['MAUC'].iloc[entryToAddIndex]):
      #   entryToAddIndex += 1




  print(resDf)

  return resDf


  # else:
  #   dataStruct = pickle.load(open(evalResFile, 'rb'))
  #   fileDatesRemote = dataStruct['fileDatesRemote']
  #   resDf = dataStruct['res']



if __name__ == '__main__':

  submissionsFld = 'd4LiveSubmissions'
  evalResFile = '%s/evalResAllD4Live.npz' % submissionsFld
  dropboxRemoteFolder = '/ProAD/public_html'
  uploadsFldRemote = '/ProAD/uploads'
  d4File = '../TADPOLE_D4_corr.csv'
  ldbDropbox = DropboxObj()

  if args.fast:
    # load submissions already evaluated and only evaluate the new ones
    dataStruct = pickle.load(open(evalResFile, 'rb'))
    resDf = dataStruct['res']
  else:
    # res = pd.DataFrame(np.nan, index=range(nrEntries), columns=tableColumns)
    dataStruct = pickle.load(open('%s/resTableJune19.npz' % submissionsFld, 'rb'))
    resDf = dataStruct['res']
    # print(resDf.columns)
    # asda
    idxToKeep = ~np.in1d(resDf['TeamName'], ['Consensus', 'Randomised', 'ATRI-Biostat'])
    resDf = resDf.loc[idxToKeep, :]
    resDf.reset_index(inplace=True)

    resDf.loc[:,'Date'] = [ datetime.strptime('Jun 14 2019  2:00PM', '%b %d %Y %I:%M%p') for _ in range(resDf.shape[0])]



  nrInitEntries = resDf.shape[0]

  resDf = evalD4LeaderboardSubmissions(resDf, evalResFile, fileNameTag ='TADPOLE_Submission_D4Live_D2_', predictionSet='D2')

  resDf = evalD4LeaderboardSubmissions(resDf, evalResFile, fileNameTag='TADPOLE_Submission_D4Live_D3_',
                                       predictionSet='D3')

  nrFinalEntries = resDf.shape[0]

  if nrFinalEntries > nrInitEntries:
    dataStruct = dict(res=resDf)
    pickle.dump(dataStruct, open(evalResFile, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


  resD2, resD3, _ = getD2D3deepCopy(resDf)
  resAll = [resD2, resD3]
  predictionSets = ['D2', 'D3']

  for d in range(2):
    addOtherStatsTable(resAll[d])
    applyChangesDf(resAll[d])

    htmlFile = 'D4TableLive%s.html' % predictionSets[d]

    htmlFileFullPathRemote = '%s/%s' % (dropboxRemoteFolder, htmlFile)
    htmlFileFullPathLocal = '%s/%s' % (submissionsFld, htmlFile)
    writeHTMLtable(resAll[d], htmlFileFullPathLocal)
    ldbDropbox.upload(htmlFileFullPathLocal, htmlFileFullPathRemote)

import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import argparse
import os
import evalOneSubmission
import numpy as np
import pandas as pd
import csv
import string
import time
import datetime
import pickle
from scipy.stats import rankdata

parser = argparse.ArgumentParser(usage='python3 leaderboardRunAll.py', description=r'''
  Script uploads the leaderboard table to dropbox

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
    self.dbx = self.createDropboxInstance()

  def createDropboxInstance(self):
    # Check for an access token

    if (len(TOKEN) == 0):
      sys.exit("ERROR: Looks like you didn't add your access token. "
          "Open up backupuploadDropboxAPIv2.py in a text editor and "
          "paste in your token in line 14.")

    # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")
    print('TOKEN', '%s' % TOKEN[:-1], type(TOKEN))

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


def writeHTMLtable(evalResults, htmlFile, forecastFiles, fileDatesRemote):
  html = open(htmlFile, 'w')

  ## Add this manually in skeleton13.css in the dropbox folder under ProAD/public_html/css
  manuallyAddToPageCssStyle = r'''
  <style>
tr.d0 td {
  background-color: #ffffff;
  color: black;
  max-width: 50px;
  overflow: wrap;
  text-overflow: ellipsis;
  word-wrap: break-word;
}
tr.d1 td {
  background-color: #ffffff;
  color: black;
  max-width: 50px;
  overflow: wrap;
  text-overflow: ellipsis;
  word-wrap: break-word;
}
</style>
'''


  text = 'Table last updated on %s. ' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M (UTC+0)') )
  text += '<table  class="comictable sortable smallfont" style="width: 400px; table-layout: fixed; align:center"  >\n'
  # text += '<table  class="table" >\n'
  # text += r'''
  # <col width="15">
  # <col width="40">
  # <col width="20">
  # <col width="30">
  # <col width="40">
  # <col width="40">
  # <col width="40">
  # <col width="40">
  # <col width="35">
  # <col width="35">
  # <col width="60">'''
  #
  #



#   trStartHead = r'''<thead>
# 	<tr class="d1"><td>'''
#   trEndHead = r'''</td></tr>
# </thead>
# '''
#   text += trStartHead
#   text += '</td><td>'.join(['RANK', 'TEAM NAME', 'MAUC', 'BCA', 'ADAS MAE', 'VENTS MAE',
#     'ADAS WES', 'VENTS WES', 'ADAS CPA', 'VENTS CPA', 'DATE'])

  text += r'''
  <thead>
       <tr class="ldbHeader">
           <th style="width: 60px"> RANK<br></th>
           <th style="width: 60px"> TEAM NAME</th>
           <th style="width: 60px"> MAUC</th>
           <th style="width: 60px"> BCA</th>
           <th style="width: 60px"> ADAS MAE</th>
           <th style="width: 60px"> VENTS MAE</th>
           <th style="width: 60px"> ADAS WES</th>
           <th style="width: 60px"> VENTS WES</th>
           <th style="width: 60px"> ADAS CPA</th>
           <th style="width: 60px"> VENTS CPA</th>
           <th style="width: 60px"> DATE</th>	   	
     </tr>
   </thead>
  
  '''

  # text += trEndHead + '<tbody>'
  text += '<tbody>'
  nrFiles = len(forecastFiles)
  # print(evalResults.shape)
  # print(evalResults['MAUC'])
  formatStrsMeasures = ['%.3f','%.3f','%.3f','%.5f','%.3f','%.5f','%.3f','%.3f']
  for f in range(evalResults['MAUC'].shape[0]):
    if not np.isnan(evalResults['MAUC'].iloc[f]):
      text += '\n   <tr class="d%d">' % (f % 2)
      teamName = forecastFiles[f].split('.')[0][len('TADPOLE_Submission_Leaderboard_'):]
      # print(f, type(evalResults['TEAMNAME'].iloc[f]))
      # print(f, type('%f' % evalResults['RANK'].iloc[f]))
      # print(f, [type(n) for n in evalResults.loc[f,'MAUC':'ventsCP']])

      text += '<td>%.1f</td>'  % evalResults['RANK'].iloc[f]
      text += '<td style="word-wrap: break-word">%s</td><td>' % evalResults['TEAMNAME'].iloc[f]
      text += '</td><td>'.join(
        [ strFmt % n for strFmt, n in zip(formatStrsMeasures, evalResults.loc[f,'MAUC':'ventsCPA'])] +
        [fileDatesRemote[f].strftime('%Y-%m-%d %H:%M (UTC+0)')])
      text += '</td></tr>\n'

  text += '</tbody>\n</table>'

  with open(htmlFile, "w") as f:
    f.write(text)

def downloadLeaderboardSubmissions():
  htmlFile = 'leaderboardTable.html'
  dropboxRemoteFolder = '/ProAD/public_html'
  uploadsFldRemote = '/ProAD/uploads'
  ldbSubmissionsFld = 'leaderboardSubmissions'

  ldbDropbox = DropboxObj()

  fileListAll = ldbDropbox.list_folder(uploadsFldRemote, '/')
  fileListLdb = [x for x in fileListAll.keys() if x.startswith('TADPOLE_Submission_Leaderboard')]
  fileListLdb.sort()
  print('fileListLdb ', fileListLdb)
  os.system('mkdir -p %s' % ldbSubmissionsFld)
  nrEntries = len(fileListLdb)

  teamNames = [f.split('.')[0][len('TADPOLE_Submission_Leaderboard_'):] for f in fileListLdb]

  evalResFile = '%s/evalResAll.npz' % ldbSubmissionsFld

  # entriesList = [0,1,2]
  tableColumns = ('TEAMNAME', 'RANK' , 'MAUC', 'BCA',
    'adasMAE', 'ventsMAE', 'adasWES', 'ventsWES', 'adasCPA', 'ventsCPA')

  if args.runPart[0] == 'R':
    if args.fast:
      # load submissions already evaluated and only evaluate the new ones
      dataStruct = pickle.load(open(evalResFile, 'rb'))
      evalResults = dataStruct['evalResults']
      fileDatesRemote = dataStruct['fileDatesRemote']
      entriesList = [e for e,f in enumerate(teamNames) if (evalResults['TEAMNAME'].str.contains(f).sum() == 0)]
      nanSeries = pd.DataFrame(np.nan, index=range(len(entriesList)), columns=tableColumns)
      nrEntriesSoFar = evalResults.shape[0]
      evalResults = evalResults.append(nanSeries, ignore_index=True)
      print('teamNames', teamNames)
      print('entriesList', entriesList)
      print('evalResults', evalResults)
      # print(adsa)
    else:
      evalResults = pd.DataFrame(np.nan, index=range(nrEntries), columns=tableColumns)
      fileDatesRemote = []
      entriesList = range(nrEntries)
      nrEntriesSoFar = 0

    lb4Df = pd.read_csv('TADPOLE_LB4.csv')
    lb4Df = lb4Df[lb4Df['LB4'] == 1] # only keep the LB4 entries
    lb4Df.reset_index(drop=True, inplace=True)
    indexInTable = 0
    entryToAddIndex = nrEntriesSoFar
    for f in entriesList:
      fileName = fileListLdb[f]
      teamName = teamNames[f]
      # print('teamname ', teamName)
      remotePath = '%s/%s' % (uploadsFldRemote, fileName)
      localPath = '%s/%s' % (ldbSubmissionsFld, fileName)
      ldbDropbox.download(localPath, remotePath)

      metadataFileRemote = ldbDropbox.dbx.files_get_metadata(remotePath)
      fileDatesRemote += [metadataFileRemote.server_modified]

      print('Evaluating %s' % fileName)
      forecastDf = pd.read_csv(localPath)
      try:
        evalResults.loc[entryToAddIndex, ['MAUC', 'BCA',
      'adasMAE', 'ventsMAE', 'adasWES', 'ventsWES', 'adasCPA', 'ventsCPA']] = \
          evalOneSubmission.evalOneSub(lb4Df, forecastDf)
        evalResults.loc[entryToAddIndex, 'TEAMNAME'] = teamName
      except :
        print('Error while processing submission %s' % fileName)
        pass


      # if not np.isnan(evalResults['MAUC'].iloc[f]):

      entryToAddIndex += 1


    nanMask = np.isnan(evalResults['MAUC'])
    evalResults = evalResults[np.logical_not(nanMask)]
    evalResults.reset_index(drop = True, inplace = True)

    # # compute the ranks using MAUC
    # rankOrder = np.argsort(evalResults.as_matrix(columns = ['MAUC']).reshape(-1))[::-1]  # sort them by MAUC
    # rankOrder += 1  # make them start from 1
    # print('ranks', evalResults['MAUC'], rankOrder, evalResults.as_matrix(columns = ['MAUC']).reshape(-1))
    # for f in range(evalResults.shape[0]):
    #   evalResults.loc[f, 'RANK'] = rankOrder[f]

    dataStruct = dict(evalResults=evalResults, fileDatesRemote=fileDatesRemote)
    pickle.dump(dataStruct, open(evalResFile, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
  else:
    dataStruct = pickle.load(open(evalResFile, 'rb'))
    fileDatesRemote = dataStruct['fileDatesRemote']
    evalResults = dataStruct['evalResults']

  rankMAUC = rankdata(rankdata(-evalResults.as_matrix(columns = ['MAUC']).reshape(-1), method='average'), method='average')
  rankADAS = rankdata(rankdata(evalResults.as_matrix(columns = ['adasMAE']).reshape(-1), method='average'), method='average')
  rankVENTS = rankdata(rankdata(evalResults.as_matrix(columns = ['ventsMAE']).reshape(-1), method='average'), method='average')

  print('rankMAUC', rankMAUC)
  print('rankADAS', rankADAS)
  print('rankVENTS', rankVENTS)

  rankSum = rankMAUC + rankADAS + rankVENTS

  rankOrder = rankdata(rankSum, method='average')   # make them start from 1
  for f in range(evalResults.shape[0]):
    evalResults.loc[f, 'RANK'] = rankOrder[f]

  # print('evalResults before\n', evalResults)

  evalResults = evalResults.sort_values(by=['MAUC', 'BCA'],ascending=False)
  evalResults = evalResults.reset_index(drop=True)

  # print('evalResults after\n', evalResults)

  htmlFileFullPathRemote = '%s/%s' % (dropboxRemoteFolder, htmlFile)
  htmlFileFullPathLocal = '%s/%s' % (ldbSubmissionsFld, htmlFile)
  writeHTMLtable(evalResults, htmlFileFullPathLocal, fileListLdb, fileDatesRemote)
  ldbDropbox.upload(htmlFileFullPathLocal, htmlFileFullPathRemote)

if __name__ == '__main__':
  downloadLeaderboardSubmissions()
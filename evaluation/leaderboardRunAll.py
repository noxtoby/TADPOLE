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

parser = argparse.ArgumentParser(usage='python3 leaderboardRunAll.py', description=r'''
  Script uploads the leaderboard table to dropbox

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk

''')

TOKEN = open('/home/razvan/.dropboxTadpoleToken', 'r').read()[:-1]

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
  text = r'''
  <style>
tr.d0 td {
  background-color: #ffffff;
  color: black;
}
tr.d1 td {
  background-color: #e6e6e6;
  color: black;
}
</style>
'''
  text += '<table  class="sortable smallfont" style="width: 880px; table-layout: fixed;"  >\n'
  text += r'''
  <col width="60">
  <col width="35">
  <col width="35">
  <col width="30">
  <col width="40">
  <col width="40">
  <col width="40">
  <col width="40">
  <col width="35">
  <col width="35">
  <col width="60">'''

  trStartHead = r'''<thead>
	<tr class="d1"><td>'''
  trEndHead = r'''</td></tr>
</thead>
'''
  text += trStartHead
  text += '</td><td>'.join(['TEAM NAME', 'RANK', 'MAUC', 'BCA', 'ADAS MAE', 'VENTS MAE',
    'ADAS WES', 'VENTS WES', 'ADAS CP', 'VENTS CP', 'DATE'])
  text += trEndHead + '<tbody>'
  nrFiles = len(forecastFiles)
  print(evalResults.shape)
  print(evalResults['MAUC'])
  rankOrder = np.argsort(evalResults['MAUC'])[::-1] # sort them by MAUC, which is the first entry
  for f in range(nrFiles):
    if not np.isnan(evalResults['MAUC'].iloc[f]):
      text += '\n   <tr class="d%d"><td style="word-wrap: break-word">' % (f % 2)
      teamName = forecastFiles[f].split('.')[0][len('TADPOLE_Submission_Leaderboard_'):]
      text += '</td><td>'.join(
        [teamName, '%d' % rankOrder[f]] + [ '%.2f' % n for n in evalResults.iloc[f]] +
        [fileDatesRemote[f].strftime('%Y-%m-%d %H:%M (UTC+0)')])
      text += '</td></tr>\n'

  text += '</tbody>\n</table>'

  print('####################\n')
  print(text)
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

  evalResFile = '%s/evalResAll.npz' % ldbSubmissionsFld

  runPart = ['R', 'R']

  if runPart[0] == 'R':
    evalResults = pd.DataFrame(np.nan, index=range(nrEntries), columns=('MAUC', 'BCA',
    'adasMAE', 'ventsMAE', 'adasWES', 'ventsWES', 'adasCP', 'ventsCP'))
    lb4Df = pd.read_csv('TADPOLE_LB4.csv')
    lb4Df = lb4Df[lb4Df['LB4'] == 1] # only keep the LB4 entries
    lb4Df.reset_index(drop=True, inplace=True)
    fileDatesRemote = []
    for f in range(nrEntries):
    # for f in [2]:
      fileName = fileListLdb[f]
      remotePath = '%s/%s' % (uploadsFldRemote, fileName)
      localPath = '%s/%s' % (ldbSubmissionsFld, fileName)
      ldbDropbox.download(localPath, remotePath)

      metadataFileRemote = ldbDropbox.dbx.files_get_metadata(remotePath)
      fileDatesRemote += [metadataFileRemote.server_modified]

      print('Evaluating %s' % fileName)
      forecastDf = pd.read_csv(localPath)
      try:
        evalResults.iloc[f] = evalOneSubmission.evalOneSub(lb4Df, forecastDf)
      except :
        print('Error while processing submission %s' % fileName)
        pass


    dataStruct = dict(evalResults=evalResults, fileDatesRemote=fileDatesRemote)
    pickle.dump(dataStruct, open(evalResFile, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
  else:
    dataStruct = pickle.load(open(evalResFile, 'rb'))
    fileDatesRemote = dataStruct['fileDatesRemote']
    evalResults = dataStruct['evalResults']

  print('evalResults\n', evalResults)

  htmlFileFullPathRemote = '%s/%s' % (dropboxRemoteFolder, htmlFile)
  htmlFileFullPathLocal = '%s/%s' % (ldbSubmissionsFld, htmlFile)
  writeHTMLtable(evalResults, htmlFileFullPathLocal, fileListLdb, fileDatesRemote)
  ldbDropbox.upload(htmlFileFullPathLocal, htmlFileFullPathRemote)

if __name__ == '__main__':
  downloadLeaderboardSubmissions()
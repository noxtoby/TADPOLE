import sys

if sys.version_info[0] != 3: #or sys.version_info[1] < 5:
  print("This script requires Python 3. Tested on version 3.5")
  sys.exit(1)

import os
import numpy as np
import csv
from datetime import datetime
import pickle
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
  description='Assembles the TADPOLE_D1_D2.csv spreadsheet from several ADNI spreadsheets.'\
 ' The script takes ADNIMERGE and adds extra MRI, PET, DTI, CSF biomarkers. ' \
 r'''The script requires the following spreadsheets to be in the current folder:
    * UCSFFSL_02_01_16.csv
    * UCSFFSL_DICT_11_01_13.csv
    * UCSFFSL51ALL_08_01_16.csv
    * UCSFFSL51ALL_DICT_05_04_16.csv
    * UCSFFSX_11_02_15.csv
    * UCSFFSX_DICT_08_01_14.csv
    * UCSFFSX51_08_01_16.csv
    * UCSFFSX51_DICT_08_01_14.csv
    * BAIPETNMRC_09_12_16.csv
    * BAIPETNMRC_DICT_09_12_16.csv
    * UCBERKELEYAV45_10_17_16.csv
    * UCBERKELEYAV45_DICT_06_15_16.csv
    * UCBERKELEYAV1451_10_17_16.csv
    * UCBERKELEYAV1451_DICT_10_17_16.csv
    * DTIROI_04_30_14.csv
    * DTIROI_DICT_04_30_14.csv
    * UPENNBIOMK9_04_19_17.csv
    * UPENNBIOMK9_DICT_04_19_17.csv
    * TADPOLE_D2_column.csv - needs to be generated beforehand by MATLAB script TADPOLE_D2.m

    The simplest way to run it is with

        python3 TADPOLE_D1_D2.py

    If the spreadsheets are in a different directory (e.g. parent directory), run it as follows:

        python3 TADPOLE_D1_D2.py --spreadsheetFolder ..

    The script requires several python libraries, such as:
    numpy
    scipy
    subprocess
    pickle
    pandas
    csv
 ''', formatter_class=RawTextHelpFormatter
)

parser.add_argument('--spreadsheetFolder', dest='spreadsheetFolder', default='.',
                   help='folder of output spreadsheets')

parser.add_argument('--runPart', dest='runPart', default='0',type=int,
                   help='0-run full script   1-only the first part, generate intermediate result file 2-only second '
                        'part. If you want to generate the spreadsheet, leave it to 0.')

parser.add_argument('--cellWidth', dest='cellWidth', default='100',type=int,
                   help='decides the cell width, leave to default value. Only used by developers')

parser.add_argument('--runScripts', dest='runScripts', default='1',type=int,
                   help='whether to also run TADPOLE_D2.py and TADPOLE_D3.py. Only used by developers')

parser.add_argument('--runChecks', dest='runChecks', default='0',type=int,
                   help='whether to run sanity checks on the dataset. Only used by developers')

CN = 1
MCI = 2
AD = 3

np.random.seed(1)

args = parser.parse_args()
dataType = 'S%d' % args.cellWidth

def filterData(filterInd, isProc, subjID, visit, magStrength, sequence, scanDate,
  studyID, seriesID, imageID):
  
  isProc = isProc[filterInd]
  subjID = subjID[filterInd]
  visit = visit[filterInd]
  magStrength = magStrength[filterInd]
  sequence = sequence[filterInd]
  scanDate = [scanDate[i] for i in range(len(scanDate)) if filterInd[i]]
  studyID = studyID[filterInd]
  seriesID = seriesID[filterInd]
  imageID = imageID[filterInd]
  
  return isProc, subjID, visit, magStrength, sequence, scanDate, studyID, seriesID, imageID

def loadADNIMerge(filePath, dictPath):
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    ridInd = 0
    ptidInd = 1
    visCodeInd = 2
    mergeAll = np.ndarray((nrRows, nrCols), dtype=dataType)
    mergeAll[:] = ' '
    # mergeAll.fill('  ')
    # print('mergeAll', mergeAll)
    # print(adas)
    # print('nrRows', nrRows)
    
    for r in range(nrRows):
      # print([str.encode(word) for word in rows[r]])
      # print(np.array([str.encode(word) for word in rows[r]]))
      mergeAll[r,:] = [str.encode(word) for word in rows[r]]
    
    # print(mergeAll[:4,:])
    # print('rid 3 ', mergeAll[mergeAll[:,ridInd] == b'3',:])
    # print(adsa)
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    nrRows = len(rows)
    nrCols = len(rows[0])
    dictAll = np.ndarray((nrRows, nrCols), dtype=dataType)
    dictAll[:] = b' '
    
    for r in range(nrRows):
      # print([str.encode(word) for word in rows[r]])
      dictAll[r,:] = [str.encode(word) for word in rows[r]]
  
  return mergeAll, ridInd, ptidInd, visCodeInd, header, dictAll


def parseDX(dxChange, dxCurr, dxConv, dxConvType, dxRev):
  # returns (ADNI1_diag, ADNI2_diag) as a pair of integers
  
  if not np.isnan(dxChange):
    adni2_diag = dxChange
    # print('dxChange', dxChange)
  else:
    # print('dxCurr', dxCurr)
    # print('dxConv', dxConv)
    adni1_diag = dxCurr
    if dxConv == 0:
      adni2_diag = int(dxCurr)
    elif dxConv == 1 and dxConvType == 1:
      adni2_diag = 4
    elif dxConv == 1 and dxConvType == 3:
      adni2_diag = 5
    elif dxConv == 1 and dxConvType == 2:
      adni2_diag = 6
    elif dxConv == 2:
      adni2_diag = int(dxRev) + 6
    elif np.isnan(dxConv):
      adni2_diag = -1
    else:
      print(dxChange, dxCurr, dxConv, dxConvType, dxRev)
      return ValueError('wrong values for diagnosis')

  
  return adni2_diag

def int2bin(i):
  return str.encode('%s' % i)

def bin2int(s):
  return int(s.decode('utf-8'))

def changeDiagToLongit(filePath, mergeAll, ridInd, ptidInd, visCodeInd, header):
  '''
  
  :param filePath: file containing the diagnosis spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''
  
  df = pd.read_csv(filePath)
  # print('df', df)
  
  nrRows = df.shape[0]
  adni2DiagOrig = np.zeros(nrRows,int)
  for r in range(nrRows):
    parsedDiag = parseDX(df['DXCHANGE'][r], df['DXCURREN'][r], df['DXCONV'][r], df['DXCONTYP'][r],
    df['DXREV'][r])
    # print(df['DXCHANGE'][r], df['DXCURREN'][r], df['DXCONV'][r], df['DXCONTYP'][r],
    # df['DXREV'][r])
    # print('parsedDiag', parsedDiag)
    adni2DiagOrig[r] = parsedDiag
  
  df['adni2DiagOrig'] = adni2DiagOrig
  # print('adni2DiagOrig', adni2DiagOrig)
  
  nrRowsMerge, nrColsMerge = mergeAll.shape
  mergeAllPlus = np.ndarray((nrRowsMerge, nrColsMerge+1), dtype=dataType)
  targetPos = 8
  mergeAllPlus[:,:targetPos] = mergeAll[:,:targetPos]
  mergeAllPlus[:, targetPos] = b''
  mergeAllPlus[:, (targetPos+1):] = mergeAll[:,targetPos:]
  
  headerPlus = header[:targetPos] + ['DXCHANGE'] + header[targetPos:]
  
  sortedVisitsList = ['sc', 'bl', 'm03', 'm06', 'm12', 'm18', 'm24', 'm36', 'm48', 'm60',
    'm72', 'm84', 'm96']
  
  # print('mergeAllPlus[:, targetPos]', mergeAllPlus[:, targetPos])
  for r2 in range(nrRowsMerge):
    ridMaskDX = bin2int(mergeAllPlus[r2,ridInd]) == df['RID']
    currVisitMerge = mergeAllPlus[r2,visCodeInd].decode('utf-8')
    visCodeMaskDX = currVisitMerge == (df['VISCODE2'])
    maskAdni2DiagDX = np.logical_and(ridMaskDX, visCodeMaskDX)
    # print('np.sum(maskAdni2DiagOrig)', np.sum(maskAdni2DiagOrig))
    # print('maskAdni2DiagOrig', maskAdni2DiagOrig)
    if np.sum(maskAdni2DiagDX) == 0:
      pass
      # print('mergeAllPlus[r2,:5]', mergeAllPlus[r2,:5])
      # print('r2', r2)
      # raise ValueError('no entry was matched')
      
      # get diagnosis from previous visit, if visit & diag exist
      # allVisits = df['VISCODE2'][ridMaskDX]
      # currVisIndexInSortedVisits = [i for i in range(len(sortedVisitsList))
      #   if sortedVisitsList[i] == currVisitMerge]
      # prevVisit = sortedVisitsList[currVisIndexInSortedVisits[0]-1]
      # prevVisCodeMaskDX = prevVisit == (df['VISCODE2'])
      # maskAdni2DiagDX = np.logical_and(ridMaskDX, prevVisCodeMaskDX)

    
    if np.sum(maskAdni2DiagDX) >= 2:
      pass
      # print('mergeAllPlus[r2,:5]', mergeAllPlus[r2, :5])
      # print('r2', r2)
      # raise ValueError('more than one entry was matched')

    
    assert maskAdni2DiagDX.shape[0] == adni2DiagOrig.shape[0]
    
    # print('df[adni2DiagOrig]', df['adni2DiagOrig'])

    
    if np.sum(maskAdni2DiagDX) == 1:
      matchedDiag = df[maskAdni2DiagDX]['adni2DiagOrig'].values[0]
      
      # print('matchedDiag:\n', matchedDiag)
      mergeAllPlus[r2, targetPos] = int2bin(matchedDiag)
    
    if np.sum(maskAdni2DiagDX) >= 2:
      matchedDiag = df[maskAdni2DiagDX]['adni2DiagOrig'].values[0]
      mergeAllPlus[r2, targetPos] = int2bin(matchedDiag)
  
  # print('mergeAllPlus[:5,:10]', mergeAllPlus[:5,:10])
  # print('headerPlus[:10]', headerPlus[:10])
  # print(adsa)
  
  return mergeAllPlus, headerPlus


def copyListIntoNPCharArray(list, chararray):
  for i in range(len(list)):
    chararray[i] = list[i]

  return chararray

def appendMRIADNI1FSL(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader):
  '''
  Append Freesurfer Longitudinal data

  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''
  
  print('Appending Freesurfer ADNI1 longitudinal data from %s' % filePath)

  vc = 'VISCODE2'
  
  df = pd.read_csv(filePath)
  df['OVERALLQC_NR'] = df['OVERALLQC']
  df['TEMPQC_NR'] = df['TEMPQC']
  df['FRONTQC_NR'] = df['FRONTQC']
  df['PARQC_NR'] = df['PARQC']
  df['INSULAQC_NR'] = df['INSULAQC']
  df['OCCQC_NR'] = df['OCCQC']
  df['CWMQC_NR'] = df['CWMQC']
  df['VENTQC_NR'] = df['VENTQC']
  
  mapping = {'Pass' : 0, 'Partial' : 1, 'Fail' : 2}
  df.replace({'OVERALLQC_NR': mapping, 'TEMPQC_NR': mapping, 'FRONTQC_NR': mapping,
    'PARQC_NR': mapping, 'INSULAQC_NR': mapping, 'OCCQC_NR': mapping, 'CWMQC_NR': mapping,
    'VENTQC_NR': mapping}, inplace=True)
  df['QCSUM_NR'] = df['TEMPQC_NR'] + df['FRONTQC_NR'] + df['PARQC_NR'] + df['INSULAQC_NR'] \
    + df['OCCQC_NR'] + df['CWMQC_NR'] + df['VENTQC_NR']
  
  df.sort_values(by=['RID', 'EXAMDATE', 'OVERALLQC_NR', 'QCSUM_NR', 'RUNDATE', 'IMAGEUID'],
    ascending=[True,True,True,True,False,False], inplace=True)
  

  # print(df.shape)
  # also remove RID 1066 baseline and m12 (later duplicate, with examdate 2011-12-19).
  # this is because the dates are wrong (the 2011-12-19 is actually an ADNI2 init visit).
  # print(df[np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')])
  # print(df[np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')])
  indicesToDrop = np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')
  indicesToDrop = np.logical_or(indicesToDrop,
    np.logical_and(df['RID'] == 1066, df[vc] == 'bl'))
  indicesToDrop = np.logical_or(indicesToDrop, df['OVERALLQC'] != 'Pass')
  # print(df.shape)
  df = df[np.logical_not(indicesToDrop)]
  df.drop(['OVERALLQC_NR', 'TEMPQC_NR', 'FRONTQC_NR', 'PARQC_NR',
    'INSULAQC_NR', 'OCCQC_NR',  'CWMQC_NR', 'VENTQC_NR', 'QCSUM_NR'], axis=1, inplace=True)
  df.reset_index(drop=True, inplace=True)
  
  with open(filePath, 'r') as f:
    
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    
    nrRows, nrCols = df.shape
    
    # rowsArray = rowsArray[rowsArray[:, 9].argsort()] # sort entries by RUNDATE
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus.fill(b' ')
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    
    for r in range(nrRows)[::-1]:
      
      currVisCode = df[vc][r]
      if currVisCode == 'sc':
        if (df[vc][df['RID'][r] == df['RID']]).str.contains('bl').sum():
          pass
        else:
          currVisCode = 'bl'
      
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == str.encode('%d' % df['RID'][r]),
        mergeAll[:,visCodeInd] == str.encode(currVisCode))
      
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        series = df.iloc[r,nrColsToSkip:]
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = series
      else:
        pass
        # print('match not found for RID %s VISCODE %s' % (df['RID'][r], df['VISCODE'][r]) )
    
    headerPlus = mergeHeader + header[nrColsToSkip:]

  ridTmp = b'3'
  visCodeTmp = b'm06'
  maskTmp = np.logical_and(mergeAllPlus[:,ridInd] == ridTmp, mergeAllPlus[:,visCodeInd] == visCodeTmp)

  mergeAllPlus[mergeAllPlus == b'nan'] = b' '

  return mergeAllPlus, headerPlus

def appendMRIADNI2FSL(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, filePathADNI1, dictPath, dictAll):
  '''
  Append Freesurfer Longitudinal data from ADNI2 within the same columns as for ADNI1

  :param filePath: file containing the ADNI2 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending Freesurfer ADNI2 longitudinal data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    adni2Header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols+1), dtype=dataType)
    rowsArray[:,-1] = b' ' # add extra column at the end
    rowsArray[:,:-1] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date

    # columns in the ADNI2 spreadsheets are permuted compared to ANDI1. find the permutation
    # permutation should go from ADNI2 header to ADNI1 header
    adni2HeaderArray = np.ndarray(len(adni2Header), dtype=dataType)
    adni2HeaderArray = copyListIntoNPCharArray(adni2Header, adni2HeaderArray)
    permList = -1 * np.ones(len(mergeHeader), int)
    mergeHeaderLims = np.array([95,467])
    mergeHeaderIdx = range(mergeHeaderLims[0], mergeHeaderLims[1])
    for h in range(len(mergeHeaderIdx)):
      idx = np.where( str.encode(mergeHeader[mergeHeaderIdx[h]]) == adni2HeaderArray)[0]
      # print(idx)
      if len(idx) == 1:
        permList[h] = idx[0]
      elif len(idx) == 0:
        pass
        # print('no col matched', mergeHeader[mergeHeaderIdx[h]])
      else:
        pass
        # print('more than one col matched', mergeHeader[mergeHeaderIdx[h]])
    
    ridTmp = 23
    visCodeTmp = b'm48'
    colTmp = b'RUNDATE'

    mergeHeaderArray = np.ndarray(len(mergeHeader), dtype=dataType)
    mergeHeaderArray = copyListIntoNPCharArray(mergeHeader, mergeHeaderArray)

    indexTmpColumn = int(np.where(mergeHeaderArray == colTmp)[0])
    colInx = np.array(range((indexTmpColumn - 5), (indexTmpColumn + 5)), int)
    
    for r in range(nrRows):
      currVisCode = rowsArray[r,3]
      if currVisCode == b'scmri':
        currVisCode = b'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r,1],
        mergeAll[:,visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        currRow = rowsArray[r,:]
        mergeAll[indexInAdniMerge,(mergeHeaderLims[0]):] = \
          [currRow[permList[i]] for i in range(len(mergeHeaderIdx))]
      else:
        pass
        # print('match not found for row %d' % r )


  
  ssNameTag = '%s_%s' % (filePathADNI1[:-4].split('/')[-1], filePath[:-4].split('/')[-1])
  headerPlus = mergeHeader[:mergeHeaderLims[0]] + ['%s_%s' % (h, ssNameTag) for h in mergeHeader[mergeHeaderLims[0]:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[3:]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus.fill(b' ')
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)


  return mergeAll, headerPlus, dictAllPlus

def appendMriADNI1FSX(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader):
  '''
  Appends MRI Freesurfer Cross-sectional data to the dataset

  :param filePath: file containing the ADNI1 s/s
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending Freesurfer ADNI1 X-sectional data from %s' % filePath)

  df = pd.read_csv(filePath)
  df['OVERALLQC_NR'] = df['OVERALLQC']
  df['TEMPQC_NR'] = df['TEMPQC']
  df['FRONTQC_NR'] = df['FRONTQC']
  df['PARQC_NR'] = df['PARQC']
  df['INSULAQC_NR'] = df['INSULAQC']
  df['OCCQC_NR'] = df['OCCQC']
  df['CWMQC_NR'] = df['CWMQC']
  df['VENTQC_NR'] = df['VENTQC']

  mapping = {'Pass' : 0, 'Partial' : 1, 'Fail' : 2}
  df.replace({'OVERALLQC_NR': mapping, 'TEMPQC_NR': mapping, 'FRONTQC_NR': mapping,
    'PARQC_NR': mapping, 'INSULAQC_NR': mapping, 'OCCQC_NR': mapping, 'CWMQC_NR': mapping,
    'VENTQC_NR': mapping}, inplace=True)
  df['QCSUM_NR'] = df['TEMPQC_NR'] + df['FRONTQC_NR'] + df['PARQC_NR'] + df['INSULAQC_NR'] \
    + df['OCCQC_NR'] + df['CWMQC_NR'] + df['VENTQC_NR']

  df.sort_values(by=['RID', 'EXAMDATE', 'OVERALLQC_NR', 'QCSUM_NR', 'RUNDATE', 'IMAGEUID'],
    ascending=[True,True,True,True,False,False], inplace=True)

  df.drop(['OVERALLQC_NR', 'TEMPQC_NR', 'FRONTQC_NR', 'PARQC_NR',
    'INSULAQC_NR', 'OCCQC_NR',  'CWMQC_NR', 'VENTQC_NR', 'QCSUM_NR'], axis=1, inplace=True)
  df.reset_index(drop=True, inplace=True)

  with open(filePath, 'r') as f:

    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]

    nrRows, nrCols = df.shape

    # rowsArray = rowsArray[rowsArray[:, 9].argsort()] # sort entries by RUNDATE

    nrColsToSkip = 2
    nrExtraCols = nrCols - nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'

    nrColsSoFar = mergeAll.shape[1]

    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus.fill(b' ')
    mergeAllPlus[:,:nrColsSoFar] = mergeAll

    for r in range(nrRows)[::-1]:

      currVisCode = df['VISCODE'][r]
      if currVisCode == 'sc':
        if (df['VISCODE'][df['RID'][r] == df['RID']]).str.contains('bl').sum():
          pass
        else:
          currVisCode = 'bl'
      elif isinstance(currVisCode, float) and np.isnan(currVisCode):
        continue

      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == str.encode('%d' % df['RID'][r]),
        mergeAll[:,visCodeInd] == str.encode(currVisCode))

      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        series = df.iloc[r,nrColsToSkip:]
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = series
      else:
        pass
        # print('match not found for RID ', df['RID'][r])

  mergeAllPlus[mergeAllPlus == b'nan'] = b' '
  headerPlus = mergeHeader + header[nrColsToSkip:]

  return mergeAllPlus, headerPlus

def appendMriADNI2FSX(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, filePathADNI1, dictPath, dictAll):
  '''
  Append Freesurfer Longitudinal data from ADNI2 within the same columns as for ADNI1

  :param filePath: file containing the ADNI2 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending Freesurfer ADNI2 X-sectional data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    adni2Header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])

    rowsArray = np.ndarray((nrRows, nrCols + 1), dtype = dataType)
    rowsArray[:, -1] = b' '  # add extra column at the end
    rowsArray[:, :-1] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()]  # sort entries by the exam date

    # rowsArray = rowsArray[rowsArray[:,12] == b'Pass',:]
    # nrRows = rowsArray.shape[0]

    # columns in the ADNI2 spreadsheets are permuted compared to ANDI1. find the permutation
    # permutation should go from ADNI2 header to ADNI1 header
    adni2HeaderArray = np.ndarray(len(adni2Header), dtype = dataType)
    adni2HeaderArray = copyListIntoNPCharArray(adni2Header, adni2HeaderArray)
    permList = -1 * np.ones(len(mergeHeader), int)
    mergeHeaderLims = np.array([467, 831])
    mergeHeaderIdx = range(mergeHeaderLims[0], mergeHeaderLims[1])
    for h in range(len(mergeHeaderIdx)):
      idx = np.where(str.encode(mergeHeader[mergeHeaderIdx[h]]) == adni2HeaderArray)[0]
      if len(idx) == 1:
        permList[h] = idx[0]
      elif len(idx) == 0:
        pass
        # print('no col matched', mergeHeader[mergeHeaderIdx[h]])
      else:
        pass
        # print('more than one col matched', mergeHeader[mergeHeaderIdx[h]])

    for r in range(nrRows):
      currVisCode = rowsArray[r, 3]
      if currVisCode == b'scmri':
        currVisCode = b'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:, ridInd] == rowsArray[r, 1],
                                        mergeAll[:, visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        currRow = rowsArray[r, :]
        mergeAll[indexInAdniMerge, (mergeHeaderLims[0]):] = [currRow[permList[i]] for i in range(len(mergeHeaderIdx))]
      else:
        pass
        # print('match not found for row %d' % r)

  ssNameTag = '%s_%s' % (filePathADNI1[:-4].split('/')[-1], filePath[:-4].split('/')[-1])
  headerPlus = mergeHeader[:mergeHeaderLims[0]] + ['%s_%s' % (h, ssNameTag) for h in mergeHeader[mergeHeaderLims[0]:]]

  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])

    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype = dataType)
    dictAllPlus.fill(b' ')
    dictAllPlus[:nrRowsSoFar, :] = dictAll

    for r in range(nrRowsDict):
      dictAllPlus[nrRowsSoFar + r, :] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = '%s_%s' % (rows[r][1], ssNameTag)

  return mergeAll, headerPlus, dictAllPlus


def appendFdgPet(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictPath, dictAll):
  '''
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending FDG PET data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype=dataType)
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    
    for r in range(nrRows):
      currVisCode = rowsArray[r][2]
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0],
        mergeAll[:,visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        pass
        # print('match not found for row %d' % r )
  
  ssNameTag = filePath[:-4].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
  
  return mergeAllPlus, headerPlus, dictAllPlus

def appendAv45Pet(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictPath, dictAll):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending AV45 PET data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype=dataType)
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll

    
    for r in range(nrRows):
      currVisCode = rowsArray[r][2]
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0], mergeAll[:,visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        pass
        # print('match not found for row %d' % r )
  
  ssNameTag = filePath[:-4].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
  
  return mergeAllPlus, headerPlus, dictAllPlus

def appendAv1451Pet(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictPath, dictAll):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending AV1451 PET data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype=dataType)
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    
    for r in range(nrRows):
      currVisCode = rowsArray[r][2]
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0], mergeAll[:,visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        pass
        # print('match not found for row %d' % r )
  
  ssNameTag = filePath[:-4].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)

  
  return mergeAllPlus, headerPlus, dictAllPlus

def appendDTI(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictPath, dictAll):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending DTI data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype=dataType)
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 11].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag describing the current spreadsheet
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    
    for r in range(nrRows):
      currVisCode = rowsArray[r][2]
      if currVisCode == b'scmri':
        currVisCode = b'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0],
        mergeAll[:,visCodeInd] == currVisCode)
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        pass
        # print('match not found for row %d' % r )
  
  ssNameTag = filePath[:-4].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  ridTmp = b'4354'
  viscodeTmp = b'm03'
  indxTmp = np.logical_and(mergeAllPlus[:,ridInd] == ridTmp,
                           mergeAllPlus[:,visCodeInd] == viscodeTmp)
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
  
  return mergeAllPlus, headerPlus, dictAllPlus


def appendCSF(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictPath, dictAll):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Appending CSF data from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag describing the current spreadsheet
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    
    for r in range(nrRows):
      currVisCode = rows[r][2]
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == str.encode(rows[r][0]),
        mergeAll[:,visCodeInd] == str.encode(currVisCode))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        if '>' in rows[r][9]:
          rows[r][9] = '%d' % int(rows[r][12].split(' ')[4])

        mergeAllPlus[indexInAdniMerge, nrColsSoFar:] = rows[r][nrColsToSkip:]

      else:
        pass
        # print('match not found for row %d' % r )
  
  ssNameTag = filePath[:-4].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype=dataType)
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
  
  return mergeAllPlus, headerPlus, dictAllPlus

def convDxchange(n):
  if n == '':
    return -1
  n = int(n)
  if n in np.array([1,7,9]):
    return CN
  elif n in np.array([2,4,8]):
    return MCI
  elif n in np.array([3,5,6]):
    return AD
  else:
    return -1


def addDcolumns(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictAll):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''

  print('Adding D1 and D2 columns from %s' % filePath)

  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    assert nrRows == mergeAll.shape[0]
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype=dataType)
    rowsArray[:,:] = rows
    
    nrExtraCols = 2
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype=dataType)
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:4] = mergeAll[:,:4] # place D1 and D2 in columns 4 and 5
    mergeAllPlus[:,(4+nrExtraCols):] = mergeAll[:,4:]
    headerPlus = mergeHeader[:4] + ['D1', 'D2'] + mergeHeader[4:] #headerPlus = mergeHeader[:4] + ['D1', 'D2'] + mergeHeader[4:]
    
    nrRowsMergeAll = mergeAllPlus.shape[0]
    for r in range(nrRowsMergeAll):
      nrVisits = np.sum(mergeAll[:,ridInd] == mergeAll[r,ridInd])
      if nrVisits >= 2:
        isInD1 = '1'
      else:
        isInD1 = '0'

      
      binaryInd = np.logical_and(rowsArray[:,0] == mergeAll[r,ridInd],
        rowsArray[:, 1] == mergeAll[r, visCodeInd])
      indexInRowsArray = np.where(binaryInd)[0]
      assert indexInRowsArray.shape[0] == 1
      mergeAllPlus[r, 4] = isInD1 # D1
      mergeAllPlus[r, 5] = rowsArray[indexInRowsArray[0]][2] # D2
  
  # add entries also in the dictionary
  nrRowsSoFar = dictAll.shape[0]
  dictAllPlusRows = nrRowsSoFar + 3
  nrColsDict = dictAll.shape[1]
  
  dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S300')
  dictAllPlus[:, :] = b' '
  dictAllPlus[:4, :] = dictAll[:4,:]
  dictAllPlus[7:, :] = dictAll[4:,:] # place dict entries for D1 and D2 in rows 4 and 5
  
  dictAllPlus[4, 1] = b'D1'
  dictAllPlus[4, 5] = b'Denotes whether participant belongs to dataset D1'
  
  dictAllPlus[5, 1] = b'D2'
  dictAllPlus[5, 5] = b'Denotes whether participant belongs to dataset D2'

  dictAllPlus[6, 1] = b'DXCHANGE'
  dictAllPlus[6, 5] = b'1=Stable:NL to NL, 2=Stable:MCI to MCI, 3=Stable:AD to AD, ' \
                      b'4=Conv:NL to MCI, 5=Conv:MCI to AD, 6=Conv:NL to AD, ' \
                      b'7=Rev:MCI to NL, 8=Rev:AD to MCI, 9=Rev:AD to NL, -1=Not available'


  
  return mergeAllPlus, headerPlus, dictAllPlus

def decodeIfBinary(s):
  if s == '':
    return s
  else:
    return s.decode('utf-8')

def checkFSXvalsAgainstADNIMERGE(tadpoleDF, mriADNI1FileFSX, otherSSvisCodeStr, ssNameTag,
                                 ignoreMissingCols = False):
  nrRows, nrCols = tadpoleDF.shape
  colListOtherSS = list(ssDF.columns.values)
  colListTadpoleDF = list(tadpoleDF.columns.values)

  tadpoleDF[['Hippocampus', 'ST29SV%s' % ssNameTag, 'ST88SV%s' % ssNameTag]] = \
    tadpoleDF[['Hippocampus', 'ST29SV%s' % ssNameTag, 'ST88SV%s' % ssNameTag]].apply(pd.to_numeric, errors='coerce')


  tadpoleDF['HIPPOSUM'] = tadpoleDF['ST29SV%s' % ssNameTag] + tadpoleDF['ST88SV%s' % ssNameTag]
  for r in range(nrRows):

    valsNan = np.isnan(tadpoleDF['Hippocampus'][r]) or (np.isnan(tadpoleDF['ST29SV%s' % ssNameTag][r]) and \
                 np.isnan(tadpoleDF['ST88SV%s' % ssNameTag][r]))
    if valsNan:
      continue

    valsNotEq = tadpoleDF['Hippocampus'][r] != (tadpoleDF['ST29SV%s' % ssNameTag][r] + tadpoleDF['ST88SV%s' % ssNameTag][r])
    if valsNotEq:
      print('entries dont match\n ', tadpoleDF[['RID','VISCODE', 'Hippocampus', 'ST29SV%s' % ssNameTag,\
        'ST88SV%s' % ssNameTag, 'HIPPOSUM']].iloc[r])

  # Conclusion: the reason why entries above don't match is because UCSFFSX has duplicate entries for the same subject and viscode.



def performChecks(tadpoleDF, ssDF, otherSSfile, otherSSvisCodeStr, ssNameTag, ignoreMissingCols=False):
  nrRows, nrCols = ssDF.shape
  colListOtherSS = list(ssDF.columns.values)
  colListTadpoleDF = list(tadpoleDF.columns.values)

  missingColsList = []
  if ignoreMissingCols:
    for c in range(4, nrCols):
      matchColNameTadpoleDFInd = np.where([i == '%s%s' % (colListOtherSS[c], ssNameTag) for i in colListTadpoleDF])[0]
      if matchColNameTadpoleDFInd.shape[0] == 0:
        missingColsList += [c]

      if matchColNameTadpoleDFInd.shape[0] > 1:
        raise ValueError('more than one column matches')

  notMatchList = []
  print('------ Checking %s ---------' % otherSSfile)
  for r in range(nrRows)[::100]:
    print('r=', r)
    otherSSViscodeCurr = ssDF[otherSSvisCodeStr][r]
    if otherSSViscodeCurr == 'sc' or otherSSViscodeCurr == 'scmri':
      otherSSViscodeCurr = 'bl'

    if otherSSViscodeCurr == 'nv':
      continue

    maskIdxInTadpoleDF = np.logical_and(tadpoleDF['RID'] == ssDF['RID'][r],
                                        tadpoleDF['VISCODE'] == otherSSViscodeCurr)
    if np.where(maskIdxInTadpoleDF)[0].shape[0] == 0:
      if isinstance(otherSSViscodeCurr, float) and np.isnan(otherSSViscodeCurr):
        continue
      else:
        print(ssDF['RID'][r], otherSSViscodeCurr)
        print('entry not found in tadpole Data')
        continue

    matchIndexInTadpoleDF = np.where(maskIdxInTadpoleDF)[0][0]
    # print('matchIndexInTadpoleDF', matchIndexInTadpoleDF)
    for c in range(4,nrCols):
      if c in missingColsList:
        continue

      matchColNameTadpoleDFInd = np.where([i == '%s%s' % (colListOtherSS[c], ssNameTag) for i in colListTadpoleDF])[0]
      if matchColNameTadpoleDFInd.shape[0] != 1:
        print('%s%s' % (colListOtherSS[c], ssNameTag))
        print([colListTadpoleDF[i] for i in matchColNameTadpoleDFInd])

        raise ValueError('more than one column matches ... or no col matches')
      matchColNameTadpoleDF = colListTadpoleDF[matchColNameTadpoleDFInd[0]]
      valTadpoleDF = tadpoleDF[matchColNameTadpoleDF][matchIndexInTadpoleDF]
      valOtherSS = ssDF[colListOtherSS[c]][r]

      try:
        valTadpoleDF = float(valTadpoleDF)
      except ValueError:
        pass

      try:
        valOtherSS = float(valOtherSS)
      except ValueError:
        pass

      valTadpoleDFIntOrFloat = isinstance(valTadpoleDF, float) or isinstance(valTadpoleDF, int)
      valOtherSSIntOrFloat =  isinstance(valOtherSS, float) or isinstance(valOtherSS, int)
      notFloatsAndAlmostEq = not (valTadpoleDFIntOrFloat and valOtherSSIntOrFloat and
                                  (np.abs(valOtherSS - valTadpoleDF) < 0.000001))

      oldValTadpoleDF = valTadpoleDF
      oldValOtherSS = valOtherSS
      valTadpoleDF = str(valTadpoleDF)
      valOtherSS = str(valOtherSS)

      valsNotEq = valTadpoleDF != valOtherSS
      notBothNaN = not (isinstance(valTadpoleDF, float) and isinstance(valOtherSS, float) and
          np.isnan(valTadpoleDF) and np.isnan(valOtherSS))
      notFS = matchColNameTadpoleDF != 'FSVERSION' and matchColNameTadpoleDF != 'FSVERSION_bl' and \
              matchColNameTadpoleDF != 'ABETA_UPENNBIOMK9_04_19_17'
      notNanAndEmpty = not((valTadpoleDF == ' ' and valOtherSS == 'nan') or
                           (valTadpoleDF == 'nan' and valOtherSS == ' '))
      currSubVisitMask = np.logical_and(ssDF['RID'] == ssDF['RID'][r], ssDF[otherSSvisCodeStr] == ssDF[
        otherSSvisCodeStr][r])
      notDupEntry = not (np.sum(currSubVisitMask) > 1)

      if valsNotEq and notBothNaN and notFS and notNanAndEmpty and notFloatsAndAlmostEq and notDupEntry:
        keysTadpoleDF = [tadpoleDF['RID'][matchIndexInTadpoleDF], tadpoleDF['VISCODE'][matchIndexInTadpoleDF]]
        notMatchList += [[keysTadpoleDF, matchColNameTadpoleDF, valTadpoleDF, valOtherSS]]
        print('values dont match:', keysTadpoleDF, matchColNameTadpoleDF, valTadpoleDF, valOtherSS)
        print(type(oldValTadpoleDF))
        print(type(oldValOtherSS))

def dropIndicesFSLADNI1(df):
  vc = 'VISCODE2'
  indicesToDrop = np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')
  indicesToDrop = np.logical_or(indicesToDrop, np.logical_and(df['RID'] == 1066, df[vc] == 'bl'))
  indicesToDrop = np.logical_or(indicesToDrop, df['OVERALLQC'] != 'Pass')
  df = df[np.logical_not(indicesToDrop)]
  return df

def checkDatasets(df):
  # check D1. all subjects should have at least two visits
  d1RIDs = np.unique(df['RID'][df['D1'] == 1])
  nrUnqRids = d1RIDs.shape[0]
  ridNotOk = []
  for r in range(nrUnqRids):
    nrVisitsCurr = np.sum(df['RID'] == d1RIDs[r])
    if nrVisitsCurr < 2:
      print('only one visit for D1 rid', d1RIDs[r])
      ridNotOk += [d1RIDs[r]]

  # check D2 - make sure DXARMREG_table.PTSTATUS==1 and REGISTRY_table['RGSTATUS']==1
  # *** Active, passed screening, etc.
  REGISTRY_file = '%s/REGISTRY.csv' % args.spreadsheetFolder
  ROSTER_file = '%s/ROSTER.csv' % args.spreadsheetFolder
  # *** specifics on EMCI/LMCI/etc
  ARM_file = '%s/ARM.csv' % args.spreadsheetFolder
  DXSUM_file = '%s/DXSUM_PDXCONV_ADNIALL.csv' % args.spreadsheetFolder
  REGISTRY_table = pd.read_csv(REGISTRY_file)

  dfREG_table = df.merge(REGISTRY_table, 'left', left_on=['RID', 'VISCODE'], right_on=['RID', 'VISCODE2'])

  ridNotOk = []

  dfREG_table.sort_values(by=['RID', 'EXAMDATE_x'],
    ascending=[True,True], inplace=True)
  dfREG_table.reset_index(drop=True, inplace=True)


  for r in range(dfREG_table.shape[0]):
    partEnrolled = dfREG_table['PTSTATUS'][r] == 1
    currPartMask = dfREG_table['RID'] == dfREG_table['RID'][r]
    partEnrolledAll = (dfREG_table['PTSTATUS'][currPartMask] == 1) #& (dfREG_table['RGSTATUS'][currPartMask] == 1)
    atLeastOnePtStatusEq1 = (dfREG_table['PTSTATUS'][currPartMask] == 1).any()
    noPtStatusEq1 = not ((dfREG_table['PTSTATUS'][currPartMask & (dfREG_table['Phase'] == 'ADNI2')] == 2).any())
    # partEnrolledLastVisit = partEnrolledAll.iloc[-1]
    partEnrolled = atLeastOnePtStatusEq1 and noPtStatusEq1
    adni2Phase = dfREG_table['COLPROT'][r] == 'ADNI2'

    if adni2Phase and dfREG_table['D2'][r] == 1 and not partEnrolled:
      print('participant in D2 but not enrolled\n', dfREG_table[['COLPROT', 'RID', 'VISCODE_x', 'VISCODE_y', 'D2',
                                                                                                         'PTSTATUS']][
        currPartMask],
            partEnrolled, partEnrolledAll)
      ridNotOk += [dfREG_table['RID'][r]]

  unqRIDnotOk = np.unique(ridNotOk)
  print('unqRIDnotOk', unqRIDnotOk) # should only show 1148, but that is only due to misalignment in the
  # checking function between the tables.

def checkSpreadsheetsExist(spreadsheetList, d2File):
  missingSS = []
  for s in spreadsheetList:
    if not os.path.isfile(s):
      missingSS += [s]

  if len(missingSS) != 0:
    print('\nERROR 1: The following required spreadsheets could not be found:\n\t *', '\n\t * '.join(missingSS), '\n')

  if not os.path.isfile(d2File):
    print('\n\nERROR 2: D2 column file ', d2File, ' could not be found. You need to first generate it using the MATLAB script TADPOLE_D2.m\n\n')

  if len(missingSS) != 0 or (not os.path.isfile(d2File)):
    raise ValueError('Several spreadsheets are missing')

# print(args.runPart)
if args.runPart == 0:
  runPart = ['R', 'R']
elif args.runPart == 1:
  runPart = ['R', 'L']
elif args.runPart == 2:
  runPart = ['L', 'R']
else:
  raise ValueError('--runPart can only be 0, 1 or 2')


mergePlusFileP1 = 'mergePlusPartialP1_S%d.npz' % args.cellWidth

adniMergeFile = '%s/ADNIMERGE.csv' % args.spreadsheetFolder
adniMergeDict = '%s/ADNIMERGE_DICT.csv' % args.spreadsheetFolder

diagFile = '%s/DXSUM_PDXCONV_ADNIALL.csv' % args.spreadsheetFolder

# Longitudinal FreeSurfer
mriADNI1FileFSL = '%s/UCSFFSL_02_01_16.csv' % args.spreadsheetFolder
mriADNI1DictFSL = '%s/UCSFFSL_DICT_11_01_13.csv' % args.spreadsheetFolder
mriADNI2FileFSL = '%s/UCSFFSL51ALL_08_01_16.csv' % args.spreadsheetFolder
mriADNI2DictFSL = '%s/UCSFFSL51ALL_DICT_05_04_16.csv' % args.spreadsheetFolder

############ Cross-sectional FreeSurfer ############
mriADNI1FileFSX = '%s/UCSFFSX_11_02_15.csv' % args.spreadsheetFolder
mriADNI1DictFSX = '%s/UCSFFSX_DICT_08_01_14.csv' % args.spreadsheetFolder
mriADNI2FileFSX = '%s/UCSFFSX51_08_01_16.csv' % args.spreadsheetFolder
mriADNI2DictFSX = '%s/UCSFFSX51_DICT_08_01_14.csv' % args.spreadsheetFolder

fdgPetFile = '%s/BAIPETNMRC_09_12_16.csv' % args.spreadsheetFolder
fdgPetDict = '%s/BAIPETNMRC_DICT_09_12_16.csv' % args.spreadsheetFolder

av45File = '%s/UCBERKELEYAV45_10_17_16.csv' % args.spreadsheetFolder
av45Dict = '%s/UCBERKELEYAV45_DICT_06_15_16.csv' % args.spreadsheetFolder

av1451File = '%s/UCBERKELEYAV1451_10_17_16.csv' % args.spreadsheetFolder
av1451Dict = '%s/UCBERKELEYAV1451_DICT_10_17_16.csv' % args.spreadsheetFolder

dtiFile = '%s/DTIROI_04_30_14.csv' % args.spreadsheetFolder
dtiDict = '%s/DTIROI_DICT_04_30_14.csv' % args.spreadsheetFolder

csfFile = '%s/UPENNBIOMK9_04_19_17.csv' % args.spreadsheetFolder
csfDict = '%s/UPENNBIOMK9_DICT_04_19_17.csv' % args.spreadsheetFolder

d2File = '%s/TADPOLE_D2_column.csv' % args.spreadsheetFolder

spreadsheetList = [adniMergeFile, adniMergeDict, diagFile, mriADNI1FileFSL, mriADNI1DictFSL, mriADNI2FileFSL,
  mriADNI2DictFSL, mriADNI1FileFSX, mriADNI1DictFSX, mriADNI2FileFSX, mriADNI2DictFSX, fdgPetFile, fdgPetDict,
  av45File, av45Dict, av1451File, av1451Dict, dtiFile, dtiDict, csfFile, csfDict]
checkSpreadsheetsExist(spreadsheetList, d2File)

tadpoleFile = 'TADPOLE_D1_D2.csv'
tadpoleDictFile = 'TADPOLE_D1_D2_Dict.csv'
tadpolePart2File = 'TADPOLE_D1_D2_Part2.csv'

mergeAll, ridInd, ptidInd, visCodeInd, header, dictAll = loadADNIMerge(adniMergeFile, adniMergeDict)

mergeAll, header = changeDiagToLongit(diagFile, mergeAll, ridInd, ptidInd, visCodeInd,
  header) # also modified header DX_bl ->DX_longitudinal

# Longitudinal FreeSurfer
mergeAll, header = appendMRIADNI1FSL(mriADNI1FileFSL, mergeAll, ridInd, ptidInd, visCodeInd, header)
# print(ads)
mergeAll, header, dictAll = appendMRIADNI2FSL(mriADNI2FileFSL, mergeAll, ridInd, ptidInd, visCodeInd, header, mriADNI1FileFSL, mriADNI1DictFSL, dictAll)

# Cross-sectional FreeSurfer
mergeAll, header = appendMriADNI1FSX(mriADNI1FileFSX, mergeAll, ridInd, ptidInd, visCodeInd, header)

mergeAll, header, dictAll = appendMriADNI2FSX(mriADNI2FileFSX, mergeAll, ridInd, ptidInd, visCodeInd, header,
                                              mriADNI1FileFSX, mriADNI1DictFSX, dictAll)

mergeAll, header, dictAll = appendFdgPet(fdgPetFile, mergeAll, ridInd, ptidInd, visCodeInd, header, fdgPetDict,
                                         dictAll)

mergeAll, header, dictAll = appendAv45Pet(av45File, mergeAll, ridInd, ptidInd, visCodeInd, header, av45Dict, dictAll)

mergeAll, header, dictAll = appendAv1451Pet(av1451File, mergeAll, ridInd, ptidInd, visCodeInd, header, av1451Dict,
                                            dictAll)

# don't use PIB as there are only around 200 entries in the spreadsheet, and is only available for ADNI1.
# pibFile = 'MRI/PIBPETSUVR.csv'
# mergeAll, header = appendAv45Pet(pibFile, mergeAll, ridInd, ptidInd, visCodeInd, header)

mergeAll, header, dictAll = appendDTI(dtiFile, mergeAll, ridInd, ptidInd, visCodeInd, header, dtiDict, dictAll)

mergeAll, header, dictAll = appendCSF(csfFile, mergeAll, ridInd, ptidInd, visCodeInd, header, csfDict, dictAll)

mergeAll, header, dictAll = addDcolumns(d2File, mergeAll, ridInd, ptidInd, visCodeInd, header, dictAll)

assert len(header) == mergeAll.shape[1]

with open(tadpoleFile, 'w') as f:
  f.write(','.join(header) + '\n')
  for r in range(mergeAll.shape[0]):
    f.write(','.join([decodeIfBinary(mergeAll[r, c]) for c in range(mergeAll.shape[1])]))
    f.write('\n')

with open(tadpoleDictFile, 'w') as f:
  for r in range(dictAll.shape[0]):
    f.write(','.join(['"%s"' % decodeIfBinary(dictAll[r, c]) for c in range(dictAll.shape[1])]))
    f.write('\n')


######### Perform checks ###################


performChecksFlag = False

if performChecksFlag:
  tadpoleDF = pd.read_csv(tadpoleFile)
  ssNameTag = ''
  ssDF = pd.read_csv(adniMergeFile)
  performChecks(tadpoleDF, ssDF, adniMergeFile, otherSSvisCodeStr = 'VISCODE', ssNameTag=ssNameTag)

  ssNameTag = '_%s_%s' % (mriADNI1FileFSL[:-4].split('/')[-1], mriADNI2FileFSL[:-4].split('/')[-1])
  ssDF = pd.read_csv(mriADNI1FileFSL)
  ssDF = dropIndicesFSLADNI1(ssDF)
  ssDF.reset_index(drop = True, inplace = True)
  performChecks(tadpoleDF, ssDF, mriADNI1FileFSL, otherSSvisCodeStr = 'VISCODE', ssNameTag=ssNameTag)
  ssDF = pd.read_csv(mriADNI2FileFSL)
  performChecks(tadpoleDF, ssDF, mriADNI2FileFSL, otherSSvisCodeStr = 'VISCODE2', ssNameTag=ssNameTag,
                ignoreMissingCols=True)

  ssNameTag = '_%s_%s' % (mriADNI1FileFSX[:-4].split('/')[-1], mriADNI2FileFSX[:-4].split('/')[-1])
  ssDF = pd.read_csv(mriADNI1FileFSX)
  # should only show mismatch for RID 830 at bl, but this is because it tried to match the screening visit to tadpole bl visit.
  performChecks(tadpoleDF, ssDF, mriADNI1FileFSX, otherSSvisCodeStr = 'VISCODE', ssNameTag=ssNameTag)
  ssDF = pd.read_csv(mriADNI2FileFSX)
  performChecks(tadpoleDF, ssDF, mriADNI2FileFSX, otherSSvisCodeStr = 'VISCODE2', ssNameTag=ssNameTag,
                ignoreMissingCols=True)

  ssNameTag = '_%s' % fdgPetFile[:-4].split('/')[-1]
  ssDF = pd.read_csv(fdgPetFile)
  performChecks(tadpoleDF, ssDF, fdgPetFile, otherSSvisCodeStr = 'VISCODE2', ssNameTag = ssNameTag)

  ssNameTag = '_%s' % av45File[:-4].split('/')[-1]
  ssDF = pd.read_csv(av45File)
  performChecks(tadpoleDF, ssDF, av45File, otherSSvisCodeStr = 'VISCODE2', ssNameTag = ssNameTag)

  ssNameTag = '_%s' % av1451File[:-4].split('/')[-1]
  ssDF = pd.read_csv(av1451File)
  performChecks(tadpoleDF, ssDF, av1451File, otherSSvisCodeStr = 'VISCODE2', ssNameTag = ssNameTag)

  ssNameTag = '_%s' % dtiFile[:-4].split('/')[-1]
  ssDF = pd.read_csv(dtiFile)
  performChecks(tadpoleDF, ssDF, dtiFile, otherSSvisCodeStr = 'VISCODE2', ssNameTag = ssNameTag)

  ssNameTag = '_%s' % csfFile[:-4].split('/')[-1]
  ssDF = pd.read_csv(csfFile)
  performChecks(tadpoleDF, ssDF, csfFile, otherSSvisCodeStr = 'VISCODE2', ssNameTag = ssNameTag)

  checkDatasets(tadpoleDF)

if args.runChecks:
  tadpoleDF = pd.read_csv(tadpoleFile)
  ssNameTag = '_%s_%s' % (mriADNI1FileFSX[:-4].split('/')[-1], mriADNI2FileFSX[:-4].split('/')[-1])
  ssDF = pd.read_csv(mriADNI1FileFSX)
  adniMergeDF = pd.read_csv(adniMergeFile)
  checkFSXvalsAgainstADNIMERGE(tadpoleDF, mriADNI1FileFSX, otherSSvisCodeStr = 'VISCODE', ssNameTag = ssNameTag)
  # the reason why entries above don't match is because UCSFFSX has duplicate entries for the same subject and viscode.


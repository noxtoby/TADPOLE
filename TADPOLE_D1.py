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
  description='Assembles the TADPOLE_D1.csv spreadsheet from several ADNI spreadsheets.'\
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
    * D2_column.csv
 ''', formatter_class=RawTextHelpFormatter
)

CN = 1
MCI = 2
AD = 3

np.random.seed(1)

args = parser.parse_args()

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
    mergeAll = np.ndarray((nrRows, nrCols), dtype='S100')
    mergeAll[:] = ' '
    # mergeAll.fill('  ')
    print('mergeAll', mergeAll)
    # print(adas)
    print('nrRows', nrRows)
    
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
    dictAll = np.ndarray((nrRows, nrCols), dtype='S100')
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
    else:
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
  print('df', df)
  
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
  print('adni2DiagOrig', adni2DiagOrig)
  
  nrRowsMerge, nrColsMerge = mergeAll.shape
  mergeAllPlus = np.ndarray((nrRowsMerge, nrColsMerge+1), dtype='S100')
  targetPos = 8
  mergeAllPlus[:,:targetPos] = mergeAll[:,:targetPos]
  mergeAllPlus[:, targetPos] = b''
  mergeAllPlus[:, (targetPos+1):] = mergeAll[:,targetPos:]
  
  headerPlus = header[:targetPos] + ['DXCHANGE'] + header[targetPos:]
  
  sortedVisitsList = ['sc', 'bl', 'm03', 'm06', 'm12', 'm18', 'm24', 'm36', 'm48', 'm60',
    'm72', 'm84', 'm96']
  
  print('mergeAllPlus[:, targetPos]', mergeAllPlus[:, targetPos])
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
      print('mergeAllPlus[r2,:5]', mergeAllPlus[r2, :5])
      print('r2', r2)
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
  
  print('mergeAllPlus[:5,:10]', mergeAllPlus[:5,:10])
  print('headerPlus[:10]', headerPlus[:10])
  # print(adsa)
  
  return mergeAllPlus, headerPlus


def appendMRIADNI1(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader):
  '''
  
  :param filePath: file containing the ADNI1 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''
  
  # if visCodeInd==2:
  #   vc = 'VISCODE2'
  # else:
  #   vc = 'VISCODE'
  vc = 'VISCODE2'
  
  df = pd.read_csv(filePath)
  print('df', df)
  # print(asdas)
  df['OVERALLQC_NR'] = df['OVERALLQC']
  df['TEMPQC_NR'] = df['TEMPQC']
  df['FRONTQC_NR'] = df['FRONTQC']
  df['PARQC_NR'] = df['PARQC']
  df['INSULAQC_NR'] = df['INSULAQC']
  df['OCCQC_NR'] = df['OCCQC']
  df['CWMQC_NR'] = df['CWMQC']
  df['VENTQC_NR'] = df['VENTQC']
  
  mapping = {'Pass' : 0, 'Partial' : 1, 'Fail' : 2}
  print(df['OVERALLQC_NR'][:50])
  df.replace({'OVERALLQC_NR': mapping, 'TEMPQC_NR': mapping, 'FRONTQC_NR': mapping,
    'PARQC_NR': mapping, 'INSULAQC_NR': mapping, 'OCCQC_NR': mapping, 'CWMQC_NR': mapping,
    'VENTQC_NR': mapping}, inplace=True)
  print(df['OVERALLQC_NR'][:50])
  # print(adsa)
  df['QCSUM_NR'] = df['TEMPQC_NR'] + df['FRONTQC_NR'] + df['PARQC_NR'] + df['INSULAQC_NR'] \
    + df['OCCQC_NR'] + df['CWMQC_NR'] + df['VENTQC_NR']
  
  df.sort_values(by=['RID', 'EXAMDATE', 'OVERALLQC_NR', 'QCSUM_NR', 'RUNDATE', 'IMAGEUID'],
    ascending=[True,True,True,True,False,False], inplace=True)
  
  # ridTmp = 23
  # visCodeTmp = 'm48'
  # indexTmpInDf = np.logical_and(df['RID'] == ridTmp, df[vc] == visCodeTmp)
  # print('df[indexTmpInDf]\n', df[indexTmpInDf])
  # print(dsas)
  
  print(df.shape)
  # also remove RID 1066 baseline and m12 (later duplicate, with examdate 2011-12-19).
  # this is because the dates are wrong (the 2011-12-19 is actually an ADNI2 init visit).
  # print(df[np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')])
  # print(df[np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')])
  indicesToDrop = np.logical_and(df['RID'] == 1066, df['EXAMDATE'] == '2011-12-19')
  indicesToDrop = np.logical_or(indicesToDrop,
    np.logical_and(df['RID'] == 1066, df[vc] == 'bl'))
  indicesToDrop = np.logical_or(indicesToDrop, df['OVERALLQC'] != 'Pass')
  print(df.shape)
  df = df[np.logical_not(indicesToDrop)]
  df.drop(['OVERALLQC_NR', 'TEMPQC_NR', 'FRONTQC_NR', 'PARQC_NR',
    'INSULAQC_NR', 'OCCQC_NR',  'CWMQC_NR', 'VENTQC_NR', 'QCSUM_NR'], axis=1, inplace=True)
  df.reset_index(drop=True, inplace=True)
  
  print(df.shape)
  # print(adsas)
  
  with open(filePath, 'r') as f:
    
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    
    nrRows, nrCols = df.shape
    
    # rowsArray = rowsArray[rowsArray[:, 9].argsort()] # sort entries by RUNDATE
    
    nrExtraCols = nrCols-3 # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus.fill(b' ')
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    # mergeAllPlus[:,nrColsSoFar] = b'Freesurfer ROIs'
    
    for r in range(nrRows)[::-1]:
      
      currVisCode = df[vc][r]
      if currVisCode == 'sc':
        # print(df['VISCODE2'][df['RID'][r] == df['RID']])
        # print(adsa)
        if (df[vc][df['RID'][r] == df['RID']]).str.contains('bl').sum():
          # print(df['VISCODE2'][df['RID'][r] == df['RID']])
          # print(adas)
          pass
        else:
          currVisCode = 'bl'
      
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == str.encode('%d' % df['RID'][r]),
        mergeAll[:,visCodeInd] == str.encode(currVisCode))
      
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        # print(df.iloc[[r]])
        series = df.iloc[r,3:]
        # print(series.shape)
        # print(mergeAllPlus[indexInAdniMerge,nrColsSoFar:].shape)
        # print(series[0,3:].shape)
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = series
      else:
        print('match not found for row %d' % r )
    
    headerPlus = mergeHeader + header[3:]
  
  mergeAllPlus[mergeAllPlus == b'nan'] = b' '
  
  print()
  
  return mergeAllPlus, headerPlus

def copyListIntoNPCharArray(list, chararray):
  for i in range(len(list)):
    chararray[i] = list[i]
  
  return chararray

def appendMRIADNI2(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, filePathADNI1, dictPath, dictAll):
  '''
  :param filePath: file containing the ADNI2 spreadsheet
  :param mergeAll: np chararray with all the information so far
  :param ridInd: index of the RID column
  :param ptidInd: index of the participant ID column
  :param visCodeInd: index of the visit code column
  :param mergeHeader: header for the data so far
  :return:
  '''
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    adni2Header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols+1), dtype='S100')
    rowsArray[:,-1] = b' ' # add extra column at the end
    rowsArray[:,:-1] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    # columns in the ADNI2 spreadsheets are permuted compared to ANDI1. find the permutation
    # permutation should go from ADNI2 header to ADNI1 header
    adni2HeaderArray = np.ndarray(len(adni2Header), dtype='S100')
    # adni2HeaderArray[:] = [str.encode(x) for x in adni2Header ]
    adni2HeaderArray = copyListIntoNPCharArray(adni2Header, adni2HeaderArray)
    # print('adni2HeaderArray', adni2HeaderArray)
    # print('adni2Header', adni2Header)
    # print(asdas)
    permList = -1 * np.ones(len(mergeHeader), int)
    print([(mergeHeader[i],i) for i in range(len(mergeHeader))])
    print('adni2HeaderArray', adni2HeaderArray)
    mergeHeaderLims = np.array([95,467])
    mergeHeaderIdx = range(mergeHeaderLims[0], mergeHeaderLims[1])
    for h in range(len(mergeHeaderIdx)):
      idx = np.where( str.encode(mergeHeader[mergeHeaderIdx[h]]) == adni2HeaderArray)[0]
      # print(idx)
      if len(idx) == 1:
        permList[h] = idx[0]
      elif len(idx) == 0:
        pass
        print('no col matched', mergeHeader[h])
      else:
        pass
        print('more than one col matched', mergeHeader[h])
    
    print('permList', permList)
    print('mergeHeader[mergeHeaderLims[0]:]', mergeHeader[mergeHeaderLims[0]:])
    print('headers zipped:', list(zip([adni2HeaderArray[permList[i]] for i in
      range(len(mergeHeaderIdx))],
      [mergeHeader[i] for i in mergeHeaderIdx])))
    print(mergeAll[0,mergeHeaderLims[0]:].shape, len(mergeHeaderIdx))
    
    ridTmp = 23
    visCodeTmp = b'm48'
    colTmp = b'RUNDATE'
    
    print(mergeAll[:4,:])
    print('np.sum(mergeAll[:,ridInd] == str.encode(ridTmp))',
      np.sum(mergeAll[:,ridInd] == str.encode('%d' % ridTmp)))
    print('np.sum(mergeAll[:, visCodeInd] == visCodeTmp)', np.sum(mergeAll[:, visCodeInd] == visCodeTmp))
    indexTmpEntry = np.logical_and(mergeAll[:,ridInd] == str.encode('%d' % ridTmp),
      mergeAll[:, visCodeInd] == visCodeTmp)
    print('np.sum(indexTmpEntry)', np.sum(indexTmpEntry))
    mergeHeaderArray = np.ndarray(len(mergeHeader), dtype='S100')
    mergeHeaderArray = copyListIntoNPCharArray(mergeHeader, mergeHeaderArray)
    
    print('mergeHeader', mergeHeader)
    print('mergeHeaderArray', mergeHeaderArray)
    indexTmpColumn = int(np.where(mergeHeaderArray == colTmp)[0])
    print('indexTmpEntry', indexTmpEntry)
    print('indexTmpColumn', indexTmpColumn)
    colInx = np.array(range((indexTmpColumn - 5), (indexTmpColumn + 5)), int)
    print('mergeHeaderArray', mergeHeaderArray[colInx])
    print('mergeAll(indexTmpEntry, indexTmpColumn)',
      mergeAll[indexTmpEntry, :][:,colInx])
    
    # print(adsa)
    
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
        print('match not found for row %d' % r )

  
  ssNameTag = '%s_%s' % (filePathADNI1.split('.')[0].split('/')[-1],
  filePath.split('.')[0].split('/')[-1])
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
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus.fill(b' ')
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
  
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype='S100')
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    # mergeAllPlus[:,nrColsSoFar] = b'BAI_FDG_PET_NMRC'
    
    for r in range(nrRows):
      # print('rid ', rows[r][0], mergeAll[:,ridInd])
      # print('viscode ', rows[r][2], mergeAll[:,visCodeInd])
      currVisCode = rowsArray[r][2]
      # if currVisCode == 'sc':
      #   currVisCode = 'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0],
        mergeAll[:,visCodeInd] == currVisCode)
      # print('np.sum(indexInAdniMerge)', np.sum(indexInAdniMerge))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        print('match not found for row %d' % r )
  
  ssNameTag = filePath.split('.')[0].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[nrColsToSkip:]
    
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype='S100')
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    currSpreadsheetTag = 'AV45_UCBERKLEY_10_17_16'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    # mergeAllPlus[:,nrColsSoFar] = str.encode(currSpreadsheetTag)

    
    for r in range(nrRows):
      # print('rid ', rows[r][0], mergeAll[:,ridInd])
      # print('viscode ', rows[r][2], mergeAll[:,visCodeInd])
      currVisCode = rowsArray[r][2]
      # if currVisCode == 'sc':
      #   currVisCode = 'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0], mergeAll[:,visCodeInd] == currVisCode)
      # print('np.sum(indexInAdniMerge)', np.sum(indexInAdniMerge))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        print('match not found for row %d' % r )
  
  ssNameTag = filePath.split('.')[0].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[nrColsToSkip:]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
    
    # print(adsa)
  
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype='S100')
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 4].argsort()] # sort entries by the exam date
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag saying 'Freesurfer ROIs'
    currSpreadsheetTag = 'AV1451_UCBERKLEY_10_17_16'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    # mergeAllPlus[:,nrColsSoFar] = str.encode(currSpreadsheetTag)
    
    for r in range(nrRows):
      # print('rid ', rows[r][0], mergeAll[:,ridInd])
      # print('viscode ', rows[r][2], mergeAll[:,visCodeInd])
      currVisCode = rowsArray[r][2]
      # if currVisCode == 'sc':
      #   currVisCode = 'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0], mergeAll[:,visCodeInd] == currVisCode)
      # print('np.sum(indexInAdniMerge)', np.sum(indexInAdniMerge))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        print('match not found for row %d' % r )
  
  ssNameTag = filePath.split('.')[0].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
    # print(mergeAll[:4,:])
    # print('rid 3 ', mergeAllPlus[mergeAllPlus[:,ridInd] == b'3',:])
    # for e in range(10):
    #   print('entry %d ' % e, mergeAllPlus[e, :])
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[nrColsToSkip:]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
    
    # print(adsa)
  
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype='S100')
    rowsArray[:,:] = rows
    rowsArray = rowsArray[rowsArray[:, 11].argsort()] # sort entries by the exam date
    # print('rowsArray[:,:5]', rowsArray[:,:5])
    # print(asdsa)
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag describing the current spreadsheet
    currSpreadsheetTag = 'DTIROI_04_30_14'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    mergeAllPlus[:,nrColsSoFar] = str.encode(currSpreadsheetTag)
    
    for r in range(nrRows):
      currVisCode = rowsArray[r][2]
      if currVisCode == b'scmri':
        currVisCode = b'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == rowsArray[r][0],
        mergeAll[:,visCodeInd] == currVisCode)
      # print('np.sum(indexInAdniMerge)', np.sum(indexInAdniMerge))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        mergeAllPlus[indexInAdniMerge,nrColsSoFar:] = rowsArray[r][nrColsToSkip:]
      else:
        print('match not found for row %d' % r )
  
  ssNameTag = filePath.split('.')[0].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  ridTmp = b'4354'
  viscodeTmp = b'm03'
  indxTmp = np.logical_and(mergeAllPlus[:,ridInd] == ridTmp,
                           mergeAllPlus[:,visCodeInd] == viscodeTmp)
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[nrColsToSkip:]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
    
    # print(adsa)
  
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    
    nrColsToSkip = 3
    nrExtraCols = nrCols-nrColsToSkip # add one extra column for a tag describing the current spreadsheet
    currSpreadsheetTag = 'CSF_UPENNBIOMK9_04_19_17'
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:nrColsSoFar] = mergeAll
    # mergeAllPlus[:,nrColsSoFar] = str.encode(currSpreadsheetTag)
    
    for r in range(nrRows):
      # print('rid ', rows[r][0], mergeAll[:,ridInd])
      # print('viscode ', rows[r][2], mergeAll[:,visCodeInd])
      currVisCode = rows[r][2]
      # if currVisCode == 'sc':
      #   currVisCode = 'bl'
      indexInAdniMerge = np.logical_and(mergeAll[:,ridInd] == str.encode(rows[r][0]),
        mergeAll[:,visCodeInd] == str.encode(currVisCode))
      # print('np.sum(indexInAdniMerge)', np.sum(indexInAdniMerge))
      assert np.sum(indexInAdniMerge) <= 1
      if np.sum(indexInAdniMerge) > 0:
        if '>' in rows[r][9]:
          rows[r][9] = '%d' % int(rows[r][12].split(' ')[4])
          # print(rows[r][9])
          # print(adass)
        mergeAllPlus[indexInAdniMerge, nrColsSoFar:] = rows[r][nrColsToSkip:]

      
      else:
        print('match not found for row %d' % r )
  
  ssNameTag = filePath.split('.')[0].split('/')[-1]
  headerPlus = mergeHeader + ['%s_%s' % (h, ssNameTag) for h in header[nrColsToSkip:]]
  
  with open(dictPath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    # rows = [rows[0]] + rows[nrColsToSkip:]
    header = rows[0]
    nrRowsDict = len(rows)
    nrColsDict = len(rows[0])
    
    nrRowsSoFar = dictAll.shape[0]
    dictAllPlusRows = nrRowsSoFar + nrRowsDict
    dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S100')
    dictAllPlus[:, :] = b' '
    dictAllPlus[:nrRowsSoFar, :] = dictAll
    
    for r in range(nrRowsDict):
      # print([str.encode(word) for word in rows[r]])
      dictAllPlus[nrRowsSoFar+r,:] = [str.encode(word) for word in rows[r]]
      dictAllPlus[nrRowsSoFar + r, 1] = \
        '%s_%s' % (rows[r][1], ssNameTag)
    
    # print(adsa)
  
  return mergeAllPlus, headerPlus, dictAllPlus

def convDxchange(n):
  # print('n', type(n))
  if n == '':
    return -1
  n = int(n)
  if n in np.array([1,7,9]):
    # print('return CN')
    return CN
  elif n in np.array([2,4,8]):
    # print('return MCI')
    return MCI
  elif n in np.array([3,5,6]):
    # print('return AD')
    return AD
  else:
    # print('return -1')
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
  with open(filePath, 'r') as f:
    reader = csv.reader(f, delimiter = ',', quotechar = '"')
    rows = [row for row in reader]
    header = rows[0]
    rows = rows[1:]  # ignore first line which is the column titles
    nrRows = len(rows)
    nrCols = len(rows[0])
    assert nrRows == mergeAll.shape[0]
    
    rowsArray = np.ndarray((nrRows, nrCols), dtype='S100')
    rowsArray[:,:] = rows
    
    nrExtraCols = 5
    
    nrColsSoFar = mergeAll.shape[1]
    
    mergeAllPlus = np.ndarray((mergeAll.shape[0], nrColsSoFar + nrExtraCols), dtype='S100')
    mergeAllPlus[:,:] = b' '
    mergeAllPlus[:,:4] = mergeAll[:,:4] # place D1 and D2 in columns 4 and 5
    mergeAllPlus[:,(4+nrExtraCols):] = mergeAll[:,4:]
    headerPlus = mergeHeader[:4] + ['D1', 'D2', 'LB1', 'LB2', 'LB4'] + mergeHeader[4:] #headerPlus = mergeHeader[:4] + ['D1', 'D2', 'D1_1', 'D1_2', 'D1_4'] + mergeHeader[4:]


    
    # D1_1 - prelim training set
    # D1_2 - prelim prediction set
    # D1_4 - prelim test set
    
    #  D1_2
      # contains 200 CN, 200 MCI subjects who have at least one extra visits (excluding last timepoint)
      # only timepoints up to an AD diagnosis, and excluding the last timepoint
    # D1_4
      # contains same subjects as D1_2, just the last timepoint (this timepoint can be AD)
    # D1_1 contains the remaining subjects
    
    unqRids = np.unique(mergeAll[:,ridInd])
    nrSubjLong = unqRids.shape[0]
    atLeastThreeTimeptsMask = np.zeros(nrSubjLong, bool)
    ctlMciMask = np.zeros(nrSubjLong, bool) # subjects with at least one visit diagnosed as CN or MCI
    diagPenultimLong = -1 * np.ones(nrSubjLong, int) # diagnosis at penultimate visit: 1-CN 2-MCI 3-AD
    ctlMciDxchange = [b'1', b'2', b'4', b'7', b'8', b'9']
    ctlDxchange = [b'1', b'7', b'9']
    mciDxchange = [b'2', b'4', b'8']
    adDxChange = [b'3', b'5', b'6']
    for s in range(unqRids.shape[0]):
      maskCurrSubj = mergeAll[:,ridInd] == unqRids[s]
      if np.sum(maskCurrSubj) >= 3:
        atLeastThreeTimeptsMask[s] = True
      
      dxchangeCurrSubj = mergeAll[maskCurrSubj, 8]
      # make sure subject has at least one timepoint with CN or MCI diagnosis.
      if np.sum(np.in1d(dxchangeCurrSubj, ctlMciDxchange)) >= 1:
        ctlMciMask = True
      
      visitsOrder = np.argsort(mergeAll[maskCurrSubj, 6]) # find order from EXAMDATE
      if dxchangeCurrSubj.shape[0] >= 2:
        # print('------------')
        # print('dxchangeCurrSubj[visitsOrder]', dxchangeCurrSubj[visitsOrder])
        # print('dxchangeCurrSubj[visitsOrder][-2]', dxchangeCurrSubj[visitsOrder][-2])
        # print('decodeIfBinary(dxchangeCurrSubj[visitsOrder][-2])',
        #   decodeIfBinary(dxchangeCurrSubj[visitsOrder][-2]))
        # print('convDxchange(decodeIfBinary(dxchangeCurrSubj[visitsOrder][-2]))',
        #   convDxchange(decodeIfBinary(dxchangeCurrSubj[visitsOrder][-2])))
        
        # print('dxchangeCurrSubj[visitsOrder]', dxchangeCurrSubj[visitsOrder])
        diagPenultimLong[s] = convDxchange(decodeIfBinary(dxchangeCurrSubj[visitsOrder][-2])) # take penultimate diagnosis
        if diagPenultimLong[s] == AD or diagPenultimLong[s] == -1:
          # if penultimate diagnosis was AD check earlier visits
          if np.sum(np.in1d([ convDxchange(decodeIfBinary(d)) for d in dxchangeCurrSubj], [CN])) > 0:
            # if there was a previous CN visit
            print('found CN visit')
            diagPenultimLong[s] = CN
          if np.sum(np.in1d([ convDxchange(decodeIfBinary(d)) for d in dxchangeCurrSubj], [MCI])) > 0:
            # if there was a previous CN visit
            diagPenultimLong[s] = MCI
          print('found MCI visit')
    
    # now take the potential RIDs and sample 200 CN and 100 MCI
    filterMask = np.logical_and(atLeastThreeTimeptsMask, ctlMciMask)
    potentialRIDsD1_2 = unqRids[filterMask]
    diagPenPotLong = diagPenultimLong[filterMask]
    nrPotRIDs = potentialRIDsD1_2.shape[0]
    potRIDsCN = potentialRIDsD1_2[diagPenPotLong == CN]
    potRIDsMCI = potentialRIDsD1_2[diagPenPotLong == MCI]
    
    nrCN = 200
    nrMCI = 200
    selectedRIDsCN = np.random.choice(potRIDsCN, nrCN)
    selectedRIDsMCI = np.random.choice(potRIDsMCI, nrMCI)
    selectedRIDs = np.concatenate((selectedRIDsCN, selectedRIDsMCI), axis=0)
    nrSelRIDs = selectedRIDs.shape[0]
    
    print('selectedRIDsCN', selectedRIDsCN)
    print('selectedRIDsMCI', selectedRIDsMCI)
    print('selectedRIDs', selectedRIDs)
    print('selectedRIDs.shape', selectedRIDs.shape)
    # print(adas)
    
    D1_2 = np.zeros(mergeAllPlus.shape[0], int)
    D1_4 = np.zeros(mergeAllPlus.shape[0], int)
    
    for s in range(nrSelRIDs):
      maskCurrSubj = mergeAll[:, ridInd] == selectedRIDs[s]
      dxchangeCurrSubj = mergeAll[maskCurrSubj, 8]
      visitsCurrSubj = mergeAll[maskCurrSubj, visCodeInd]
      visitsOrder = np.argsort(mergeAll[maskCurrSubj, 6])  # find order from EXAMDATE
      diagConvOrdered = np.array([convDxchange(decodeIfBinary(d)) for d in dxchangeCurrSubj[visitsOrder]])
      diagNotADMask = diagConvOrdered != AD
      
      if np.sum(diagNotADMask) == diagConvOrdered.shape[0]:
        # there was no visit with AD diagnosis, so simply just take
        # the last visit for D1_4 and the rest for D1_2
        lastVisitMask = np.logical_and(mergeAll[:, ridInd] == selectedRIDs[s],
          visitsCurrSubj[visitsOrder][-1] == mergeAll[:, visCodeInd])
        D1_4[lastVisitMask] = 1
        otherVisitsMask = np.logical_and(mergeAll[:, ridInd] == selectedRIDs[s],
          np.in1d(mergeAll[:, visCodeInd], visitsCurrSubj[visitsOrder][:-1]))
        D1_2[otherVisitsMask] = 1
      else:
        # there was at least one visit with AD diagnosis, so simply assign D1_2
        # all visits up to the AD visit, and then D1_4 will be that AD visit.
        visitsCurrSubjOrdered = visitsCurrSubj[visitsOrder]
        # find fist zero entry in diagNotADMask
        firstAdVisitInd = np.where(diagConvOrdered == AD)[0][0]
        if firstAdVisitInd > 0:
          visitsD1_2 = visitsCurrSubjOrdered[:firstAdVisitInd]
          visitD1_4 = visitsCurrSubjOrdered[firstAdVisitInd]
          
          lastVisitMask = np.logical_and(mergeAll[:, ridInd] == selectedRIDs[s],
            visitD1_4 == mergeAll[:, visCodeInd])
          D1_4[lastVisitMask] = 1
          otherVisitsMask = np.logical_and(mergeAll[:, ridInd] == selectedRIDs[s],
            np.in1d(mergeAll[:, visCodeInd], visitsD1_2) )
          D1_2[otherVisitsMask] = 1
          
          print('dxchange lastVisit', mergeAll[lastVisitMask, 8])
          print('dxchange otherVisitsMask', mergeAll[otherVisitsMask, 8])
          # print(adas)

    
    # set D1_1 to be everything not included in D1_2 and D1_4
    notD1orD4Mask = np.logical_not(np.logical_or(D1_2 == 1, D1_4 == 1))
    ridNotSelectedMask = np.logical_not(np.in1d(mergeAll[:, ridInd], selectedRIDs))
    D1_1 = ridNotSelectedMask.astype(int)
    
    nrRowsMergeAll = mergeAllPlus.shape[0]
    for r in range(nrRowsMergeAll):
      nrVisits = np.sum(mergeAll[:,ridInd] == mergeAll[r,ridInd])
      if nrVisits >= 2:
        isInD1 = '1'
      else:
        isInD1 = '0'
      
      # print('rowsArray[:,:2]', rowsArray[:,:2])
      # print('mergeAll[r,ridInd]', mergeAll[r,ridInd])
      # print('np.sum(rowsArray[:,0] == mergeAll[r,ridInd])',
      #   np.sum(rowsArray[:,0] == mergeAll[r,ridInd]))
      
      binaryInd = np.logical_and(rowsArray[:,0] == mergeAll[r,ridInd],
        rowsArray[:, 1] == mergeAll[r, visCodeInd])
      indexInRowsArray = np.where(binaryInd)[0]
      # print('indexInRowsArray', indexInRowsArray)
      assert indexInRowsArray.shape[0] == 1
      mergeAllPlus[r, 4] = isInD1 # D1
      mergeAllPlus[r, 5] = rowsArray[indexInRowsArray[0]][2] # D2
      
      mergeAllPlus[r, 6] = D1_1[r]  # D1_1
      mergeAllPlus[r, 7] = D1_2[r] # D1_2
      mergeAllPlus[r, 8] = D1_4[r] # D1_4
  
  # add entries also in the dictionary
  nrRowsSoFar = dictAll.shape[0]
  dictAllPlusRows = nrRowsSoFar + 6
  nrColsDict = dictAll.shape[1]
  
  dictAllPlus = np.ndarray((dictAllPlusRows, nrColsDict), dtype='S300')
  dictAllPlus[:, :] = b' '
  dictAllPlus[:4, :] = dictAll[:4,:]
  dictAllPlus[10:, :] = dictAll[4:,:] # place dict entries for D1 and D2 in rows 4 and 5
  
  dictAllPlus[4, 1] = b'D1'
  dictAllPlus[4, 5] = b'Denotes whether participant belongs to dataset D1'
  
  dictAllPlus[5, 1] = b'D2'
  dictAllPlus[5, 5] = b'Denotes whether participant belongs to dataset D2'
  
  dictAllPlus[6, 1] = b'D1_1'
  dictAllPlus[6, 5] = b'Denotes whether participant belongs to dataset D1_1'
  
  dictAllPlus[7, 1] = b'D1_2'
  dictAllPlus[7, 5] = b'Denotes whether participant belongs to dataset D2_2'
  
  dictAllPlus[8, 1] = b'D1_4'
  dictAllPlus[8, 5] = b'Denotes whether participant belongs to dataset D1_4'

  
  dictAllPlus[9, 1] = b'DXCHANGE'
  dictAllPlus[9, 5] = b'1=Stable:NL to NL, 2=Stable:MCI to MCI, 3=Stable:AD to AD, ' \
                      b'4=Conv:NL to MCI, 5=Conv:MCI to AD, 6=Conv:NL to AD, ' \
                      b'7=Rev:MCI to NL, 8=Rev:AD to MCI, 9=Rev:AD to NL'

  
  # dictAllPlus = dictAllPlus[:,[0,1,2,3,4,5,7,8,9,10,11,6]]
  
  return mergeAllPlus, headerPlus, dictAllPlus

def decodeIfBinary(s):
  if s == '':
    return s
  else:
    return s.decode('utf-8')

print('Calling TADPOLE_D2.py')
import subprocess
subprocess.call(['python','TADPOLE_D2.py'])
print('TADPOLE_D2.py finished')

runPart = 1

mergePlusFileP1 = 'mergePlusPartialP1.npz'

# Longitudinal FreeSurfer
mriADNI1FileFSL = 'UCSFFSL_02_01_16.csv'
mriADNI1DictFSL = 'UCSFFSL_DICT_11_01_13.csv'
mriADNI2FileFSL = 'UCSFFSL51ALL_08_01_16.csv'
mriADNI2DictFSL = 'UCSFFSL51ALL_DICT_05_04_16.csv'

############ TO DO: Cross-sectional FreeSurfer ############
mriADNI1FileFSX = 'UCSFFSX_11_02_15.csv'
mriADNI1DictFSX = 'UCSFFSX_DICT_08_01_14.csv'
mriADNI2FileFSX = 'UCSFFSX51_08_01_16.csv'
mriADNI2DictFSX = 'UCSFFSX51_DICT_08_01_14.csv'

if runPart in [0,1]:
  adniMergeFile = 'ADNIMERGE.csv'
  adniMergeDict = 'ADNIMERGE_DICT.csv'
  mergeAll, ridInd, ptidInd, visCodeInd, header, dictAll = loadADNIMerge(adniMergeFile, adniMergeDict)
  
  diagFile = 'DXSUM_PDXCONV_ADNIALL.csv'
  mergeAll, header = changeDiagToLongit(diagFile, mergeAll, ridInd, ptidInd, visCodeInd,
    header) # also modified header DX_bl ->DX_longitudinal
  
  # uniqueRids = np.unique(mergeAll[:, ridInd])
  # print('mergeAll[: ridInd]', mergeAll[:, ridInd])
  # print('uniqueRids', uniqueRids)
  # print('nr of subjects in D1', uniqueRids.shape)
  # diags = [b'CN', b'EMCI', b'LMCI', b'AD']
  # diagInd = 7
  # for d in range(len(diags)):
  #   # print('mergeAll[:, diagInd]', mergeAll[:, diagInd])
  #   # print('mergeAll[:, diagInd] == diags[d]', np.sum(mergeAll[:, diagInd] == diags[d]))
  #   print('diag %s - %d' % (diags[d],
  #     np.unique(mergeAll[mergeAll[:, diagInd] == diags[d], ridInd]).shape[0]))
  # print(adsas)
  
  # Longitudinal FreeSurfer
  mergeAll, header = appendMRIADNI1(mriADNI1FileFSL, mergeAll, ridInd, ptidInd, visCodeInd, header)
  mergeAll, header, dictAll = appendMRIADNI2(mriADNI2FileFSL, mergeAll, ridInd, ptidInd, visCodeInd, header, mriADNI1FileFSL, mriADNI1DictFSL, dictAll)
  # Cross-sectional FreeSurfer
  print('\n\n ************ Find me and fix me: need a new function that joins UCSFFSX tables to ADNIMERGE ************ \n\n\n')
  #mergeAll, header = appendMRIADNI1(mriADNI1FileFSX, mergeAll, ridInd, ptidInd, visCodeInd, header)
  #mergeAll, header, dictAll = appendMRIADNI2(mriADNI2FileFSX, mergeAll, ridInd, ptidInd, visCodeInd, header, mriADNI1FileFSX, mriADNI1DictFSX, dictAll)
  
  fdgPetFile = 'BAIPETNMRC_09_12_16.csv'
  fdgPetDict = 'BAIPETNMRC_DICT_09_12_16.csv'
  mergeAll, header, dictAll = appendFdgPet(fdgPetFile, mergeAll, ridInd, ptidInd, visCodeInd, header,
    fdgPetDict, dictAll)
  
  av45File = 'UCBERKELEYAV45_10_17_16.csv'
  av45Dict = 'UCBERKELEYAV45_DICT_06_15_16.csv'
  mergeAll, header, dictAll = appendAv45Pet(av45File, mergeAll, ridInd, ptidInd, visCodeInd, header,
    av45Dict, dictAll)
  
  av1451File = 'UCBERKELEYAV1451_10_17_16.csv'
  av1451Dict = 'UCBERKELEYAV1451_DICT_10_17_16.csv'
  mergeAll, header, dictAll = appendAv1451Pet(av1451File, mergeAll, ridInd, ptidInd, visCodeInd, header,
    av1451Dict, dictAll)
  
  # don't use PIB as there are only around 200 entries in the spreadsheet, and is only available for ADNI1.
  # pibFile = 'MRI/PIBPETSUVR.csv'
  # mergeAll, header = appendAv45Pet(pibFile, mergeAll, ridInd, ptidInd, visCodeInd, header)
  
  dtiFile = 'DTIROI_04_30_14.csv'
  dtiDict = 'DTIROI_DICT_04_30_14.csv'
  mergeAll, header, dictAll = appendDTI(dtiFile, mergeAll, ridInd, ptidInd, visCodeInd, header, dtiDict, dictAll)
  
  csfFile = 'UPENNBIOMK9_04_19_17.csv'
  csfDict = 'UPENNBIOMK9_DICT_04_19_17.csv'
  mergeAll, header, dictAll = appendCSF(csfFile, mergeAll, ridInd, ptidInd, visCodeInd, header,
    csfDict, dictAll)
  
  dataStruct = dict(mergeAll=mergeAll, ridInd=ridInd, ptidInd=ptidInd, visCodeInd=visCodeInd,
    header=header, dictAll=dictAll)
  pickle.dump(dataStruct, open(mergePlusFileP1, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
else:
  dataStruct = pickle.load(open(mergePlusFileP1, 'rb'))
  mergeAll = dataStruct['mergeAll']
  ridInd = dataStruct['ridInd']
  ptidInd = dataStruct['ptidInd']
  visCodeInd = dataStruct['visCodeInd']
  header = dataStruct['header']
  dictAll = dataStruct['dictAll']

d2File = 'TADPOLE_D2_column.csv'
mergeAll, header, dictAll = addDcolumns(d2File, mergeAll, ridInd, ptidInd, visCodeInd, header, dictAll)

print('len(header)', len(header))
print('mergeAll.shape[1]', mergeAll.shape[1])
assert len(header) == mergeAll.shape[1]

print('mergeAll', mergeAll)
print('mergeAll[0,:]', mergeAll[0, :])
with open('TADPOLE_D1_D2.csv', 'w') as f:
  f.write(','.join(header) + '\n')
  for r in range(mergeAll.shape[0]):
    f.write(','.join([decodeIfBinary(mergeAll[r, c]) for c in range(mergeAll.shape[1])]))
    f.write('\n')

# fromColInd = 900
# with open('TADPOLE_D1_D2_Part2.csv', 'w') as f:
#   f.write(','.join(header[:4] + header[fromColInd:]) + '\n')
#   for r in range(mergeAll.shape[0]):
#     f.write(','.join([decodeIfBinary(mergeAll[r, c]) for c in [0,1,2,3] + list(range(fromColInd, mergeAll.shape[1]))]))
#     f.write('\n')

with open('TADPOLE_D1_D2_Dict.csv', 'w') as f:
  for r in range(dictAll.shape[0]):
    f.write(','.join(['"%s"' % decodeIfBinary(dictAll[r, c]) for c in range(dictAll.shape[1])]))
    f.write('\n')

print('Calling TADPOLE_D3.py')
import subprocess
subprocess.call(['python','TADPOLE_D3.py'])
print('TADPOLE_D3.py finished')

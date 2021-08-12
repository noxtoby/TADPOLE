'''
This Python script computes summary statistics for datasets D1-D4 for the TADPOLE white paper (Table 2).

Author: Razvan V. Marinescu

To run the script, download from ADNI the following spreadsheets:

ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16
TMPINFR04_BAIPETNMRC_09_12_16
CTX_LH_MEDIALORBITOFRONTAL_SIZE_UCBERKELEYAV45_10_17_16
CTX_LH_SUPERIORPARIETAL_UCBERKELEYAV1451_10_17_16
FA_IFO_L_DTIROI_04_30_14
ABETA_UPENNBIOMK9_04_19_17

'''


import pandas as pd
import os
import sys
import numpy as np
import pickle

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 55)
pd.set_option('display.width', 5000)

mriCol = 'ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16'
fdgCol = 'TMPINFR04_BAIPETNMRC_09_12_16'
av45Col = 'CTX_LH_MEDIALORBITOFRONTAL_SIZE_UCBERKELEYAV45_10_17_16'
av1451Col = 'CTX_LH_SUPERIORPARIETAL_UCBERKELEYAV1451_10_17_16'
dtiCol = 'FA_IFO_L_DTIROI_04_30_14'
csfCol = 'ABETA_UPENNBIOMK9_04_19_17'


runPart = ['R', 'R'] # parseDataframes, buildTable

durationOfD4 = 1.4 # years since Jan 2018 -- e.g. if evaluation is done in april 2019, the duration is 1.4

if runPart[0] == 'R':
  d12PD = pd.read_csv('TADPOLE_D1_D2.csv')
  colsNeeded = list(d12PD.columns[:20]) + ['MMSE', mriCol,
    fdgCol, av45Col, av1451Col, dtiCol, csfCol, 'Years_bl']
  # print('colsNeeded', colsNeeded)
  # print(adsa)
  d12PD = d12PD[colsNeeded]
  d1PD = d12PD[d12PD.D1 == 1]
  d2PD = d12PD[d12PD.D2 == 1]
  d3PD = pd.read_csv('TADPOLE_D3.csv')

  mapping = {'NL':'CN', 'MCI':'LMCI', 'Dementia':'AD',
  'NL to MCI':'LMCI', 'MCI to Dementia':'AD', 'NL to Dementia':'AD',
  'MCI to NL':'CN', 'Dementia to MCI':'LMCI', 'Dementia to NL':'CN'}
  d3PD['DX_bl'] = d3PD.loc[:, 'DX'].map(mapping)

  d3PD['Years_bl'] = np.zeros(d3PD.shape[0])
  d3PD.loc[np.isnan(d3PD[mriCol]), mriCol] = ' '

  d3PD[fdgCol] = np.zeros(d3PD.shape[0])
  d3PD[av45Col] = np.zeros(d3PD.shape[0])
  d3PD[av1451Col] = np.zeros(d3PD.shape[0])
  d3PD[dtiCol] = np.zeros(d3PD.shape[0])
  d3PD[csfCol] = np.zeros(d3PD.shape[0])

  d3PD[fdgCol] = d3PD[fdgCol].replace(0, ' ', regex=True)
  d3PD[av45Col] = d3PD[av45Col].replace(0, ' ', regex=True)
  d3PD[av1451Col] = d3PD[av1451Col].replace(0, ' ', regex=True)
  d3PD[dtiCol] = d3PD[dtiCol].replace(0, ' ', regex=True)
  d3PD[csfCol] = d3PD[csfCol].replace(0, ' ', regex=True)

  d4PD = pd.read_csv('TADPOLE_D4_full.csv')
  d4PD[mriCol] = d4PD['Ventricles']
  d4PD.loc[np.isnan(d4PD[mriCol]), mriCol] = ' '

  d4PD[fdgCol] = np.zeros(d4PD.shape[0])
  d4PD[av45Col] = np.zeros(d4PD.shape[0])
  d4PD[av1451Col] = np.zeros(d4PD.shape[0])
  d4PD[dtiCol] = np.zeros(d4PD.shape[0])
  d4PD[csfCol] = np.zeros(d4PD.shape[0])

  d4PD[fdgCol] = d4PD[fdgCol].replace(0, ' ', regex=True)
  d4PD[av45Col] = d4PD[av45Col].replace(0, ' ', regex=True)
  d4PD[av1451Col] = d4PD[av1451Col].replace(0, ' ', regex=True)
  d4PD[dtiCol] = d4PD[dtiCol].replace(0, ' ', regex=True)
  d4PD[csfCol] = d4PD[csfCol].replace(0, ' ', regex=True)


  pdAll = [d1PD, d2PD, d3PD, d4PD]
  pickle.dump(pdAll, open('statDfParsed.npz', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

pdAll = pickle.load(open('statDfParsed.npz', 'rb'))

dbLabels = ['D1', 'D2', 'D3', 'D4']
demoDf = pd.DataFrame(columns=['Measure', 'D1', 'D2', 'D3', 'D4'], index=range(22))

if runPart[1] == 'R':

  for db in range(4):

    curPd = pdAll[db]
    # subjects
    nrSubjUnq = np.unique(curPd.RID).shape[0]

    nrVisits = curPd.shape[0]
    dLabel = dbLabels[db]

    c = 0
    demoDf.loc[c, 'Measure'] = 'Subjects'
    demoDf.loc[c, dLabel] = nrSubjUnq

    # average visits per subj
    avgNrVisits2 = float(nrVisits) / nrSubjUnq

    diagGr = [['CN', 'SMC'], ['EMCI', 'LMCI', 'MCI'], ['AD']]
    nrGr = len(diagGr)

    for g in range(nrGr):
      curPdGr = curPd[np.in1d(curPd.DX_bl, diagGr[g])]

      blMask = curPdGr.Years_bl == 0
      nrGr = np.sum(blMask)

      curPdByRidGr = curPdGr.groupby(['RID'], as_index=False)

      c += 1
      percNrGr = 100 * float(nrGr) / nrSubjUnq
      demoDf.loc[c, 'Measure'] = 'Number (%)'
      demoDf.loc[c, dLabel] = '%d (%.1f%%)' % (nrGr, percNrGr)

      c += 1
      avgNrVisitsGr = float(np.mean(curPdByRidGr.count().AGE))
      stdNrVisitsGr = float(np.std(curPdByRidGr.count().AGE))
      demoDf.loc[c, 'Measure'] = 'Visits per subject'
      demoDf.loc[c, dLabel] = '%.1f (%.1f)' % (avgNrVisitsGr, stdNrVisitsGr)

      c += 1
      meanAgeBlGr = float(np.mean(curPdByRidGr.min().AGE))
      stdAgeBlGr = float(np.std(curPdByRidGr.min().AGE))
      demoDf.loc[c, 'Measure'] = 'Age'
      demoDf.loc[c, dLabel] = '%.1f (%.1f)' % (meanAgeBlGr, stdAgeBlGr)


      c += 1
      percMales = 100 * float(np.sum(curPdGr.PTGENDER[blMask] == 'Male')) / nrGr
      demoDf.loc[c, 'Measure'] = 'Gender (% male)'
      demoDf.loc[c, dLabel] = '%.1f%%' % percMales

      c += 1
      mmseBlList = curPdGr.MMSE[blMask]
      print('mmseBlList', mmseBlList)
      meanMmseGr = float(np.mean(mmseBlList))
      stdMmseGr = float(np.std(mmseBlList))
      demoDf.loc[c, 'Measure'] = 'MMSE'
      demoDf.loc[c, dLabel] = '%.1f (%.1f)' % (meanMmseGr, stdMmseGr)

      print('db', db)
      c += 1
      if g < 2:
        # c += 1
        if db < 2: # for D1/D2/D3
          # make 1.1 years because 1-year followup is not exact, there's some variability
          followupMask = np.logical_and(curPdGr.Years_bl <= durationOfD4, curPdGr.Years_bl > 0.001)
          print(curPdGr.RID.shape)

          nrConv = np.unique(curPdGr.RID[followupMask][np.in1d(curPdGr.DXCHANGE[followupMask], [4,5,6])]).shape[0]
          percConv = 100 * float(nrConv) / nrGr
          demoDf.loc[c, 'Measure'] = 'Converters'
          demoDf.loc[c, dLabel] = '%d (%.1f%%)' % (nrConv, percConv)


      if db == 3: # for D4
        if g > 0:
          nrConv = np.unique(curPdGr.RID[np.in1d(curPdGr.DX_LastVisitADNI2, diagGr[g-1])]).shape[0]
          percConv = 100 * float(nrConv) / nrGr
          demoDf.loc[c, 'Measure'] = 'Converters'
          demoDf.loc[c, dLabel] = '%d (%.1f%%)' % (nrConv, percConv)

    c+= 1

    labels = ['Cognitive', 'MRI', 'FDG', 'AV45', 'AV1451', 'DTI', 'CSF']
    # % who have various data: cognitive, MRI, etc ..
    dataCols = ['MMSE', mriCol, fdgCol, av45Col, av1451Col, dtiCol, csfCol]
    for col in range(len(dataCols)):
      if labels[col] in ['Cognitive']:
        # print(curPd[dataCols[col]])
        # print(adsa)
        mask = np.isnan(curPd[dataCols[col]])
      else:
        mask = np.in1d(curPd[dataCols[col]], [' ', '-4'])
      c += 1
      nrWithData = np.sum(~mask)
      percWithData = 100 * float(nrWithData) / nrVisits
      demoDf.loc[c, 'Measure'] = labels[col]
      demoDf.loc[c, dLabel] = '%d (%.1f%%)' % (nrWithData, percWithData)



  demoDf = demoDf.replace(np.nan, '', regex=True)
  pickle.dump(demoDf, open('statTable.npz', 'wb'), protocol = pickle.HIGHEST_PROTOCOL)


demoDf = pickle.load(open('statTable.npz', 'rb'))
demoDf = demoDf.replace(np.nan, '-', regex=True)
demoDf.to_csv('statTable.csv',index=False)
demoDf.to_latex('statTable.tex',index=False)
print(demoDf)

##### the following are estimates from the White paper. Not used anymore.

runEstD4WhitePaper = False

if runEstD4WhitePaper:
  print('-------- database D4 -----------')

  # estimate dropout rate from ADNI1->ADNI2. Use same dropout rate to estimate total nr of subj in ADNI3.

  ADNI1Ind = d12PD.COLPROT == 'ADNI1'

  ADNIGO2Ind = np.in1d(d12PD.COLPROT, ['ADNIGO', 'ADNI2'])


  d12ByRID = d12PD.groupby(['RID'], as_index=False)
  nrSubjADNI1 = np.sum(d12ByRID.COLPROT.apply(
    lambda x: np.in1d('ADNI1', x)).astype('bool'))
  nrSubjADNI1andADNIGO2 = np.sum(d12ByRID.COLPROT.apply(
    lambda x: np.in1d('ADNI1', x) & (np.in1d('ADNI2',x) | np.in1d('ADNIGO',x))).astype('bool'))

  dropoutRate = nrSubjADNI1andADNIGO2 / nrSubjADNI1

  nrSubjD2 = np.sum(d12ByRID.D2.apply(
    lambda x: np.in1d(1, x)).astype('bool'))
  nrSubjD4 = int(nrSubjD2 * dropoutRate)

  d12oneYear = d12PD[('2012-06-01' < d12PD.EXAMDATE) & ( d12PD.EXAMDATE < '2013-06-01')] # filter entries in first year of ADNI2
  d12oneYearByRID = d12oneYear.groupby(['RID'], as_index=False)

  nrVisits = d12oneYear.shape[0]

  nrCTLD2 = 38
  nrMCID2 = 57
  nrADD2 = 5


  nrCtlD3 = nrCTLD2 * 0.96 + nrMCID2 * 0.04
  nrMCID3 = nrCTLD2 *  0.04 + nrMCID2 * 0.83 + nrADD2 * 0.03
  nrADD3 = nrCTLD2 * 0 + nrMCID2 * 0.14 + nrADD2 * 0.86

  nrD3sum = nrCtlD3 + nrMCID3 + nrADD3

  nrCtlD3norm = nrCtlD3/nrD3sum
  nrMCID3norm = nrMCID3/nrD3sum
  nrADD3norm = nrADD3/nrD3sum
  # find average number of visits by using the estimated from ADNI3 procedures manual at https://adni.loni.usc.edu/wp-content/uploads/2012/10/ADNI3-Procedures-Manual_v3.0_20170627.pdf
  # CN - 2 visits/year    MCI/AD - 1 visit/year
  avgNrVisits = round(nrCtlD3norm * 1 + nrMCID3norm * 1 + nrADD3norm * 1)
  # print(np.concatenate((np.ones(int(nrCtlD3)) * 2, np.ones(int(nrMCID3)) * 1, np.ones(int(nrADD3)) * 1),axis=0))
  stdNrVisits = np.std(np.concatenate((np.ones(int(nrCtlD3)) * 1, np.ones(int(nrMCID3)) * 1, np.ones(int(nrADD3)) * 1),axis=0))

  # % who have cognitive
  nrMMSE = float(np.sum(~np.isnan(d12oneYear.MMSE))) / nrVisits
  # % who have MRI
  nrMRI = float(np.sum(d12oneYear.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16 != ' ')) / nrVisits
  # % who have FDG
  nrFDG = float(np.sum(~np.in1d(d12oneYear.TMPINFR04_BAIPETNMRC_09_12_16, [' ', '-4']))) / nrVisits
  # % who have AV45
  nrAV45 = float(np.sum(~np.in1d(d12oneYear.CTX_LH_MEDIALORBITOFRONTAL_SIZE_UCBERKELEYAV45_10_17_16, [' ', '-4']))) / nrVisits
  # % who have AV1451
  #nrAV1451 = float(np.sum(~np.in1d(d12oneYear.CTX_LH_SUPERIORPARIETAL_UCBERKELEYAV1451_10_17_16, [' ', '-4']))) / nrVisits
  # in ADNI3 every subject will have a tau PET scan at baseline, so in theory we expect 50%. However, we'll consider
  # an estimate that is similar to AV45 ..
  nrAV1451 = nrAV45
  # % who have DIT
  nrDTI = float(np.sum(d12oneYear.FA_IFO_L_DTIROI_04_30_14 != ' ')) / nrVisits
  # % who have CSF
  nrCSF = float(np.sum(d12oneYear.ABETA_UPENNBIOMK9_04_19_17 != ' ')) / nrVisits

  # print('nrSubjD2', nrSubjD2)
  print('dropoutRate', dropoutRate)
  print('nrSubjD4', nrSubjD4)
  print('avgVisits', avgNrVisits)
  print('stdNrVisits', stdNrVisits)
  print('nrCTL', nrCtlD3)
  print('nrMCI', nrMCID3)
  print('nrAD', nrADD3)
  print('nrMMSE', nrMMSE)
  print('nrMRI', nrMRI)
  print('nrFDG', nrFDG)
  print('nrAV45', nrAV45)
  print('nrAV1451', nrAV1451)
  print('nrDTI', nrDTI)
  print('nrCSF', nrCSF)

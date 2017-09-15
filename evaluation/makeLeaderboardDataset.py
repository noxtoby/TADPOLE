import os
import numpy as np
import csv
from datetime import datetime
import dateutil
import pickle
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
  description=r'''
  TADPOLE Challenge 2017: http://tadpole.grand-challenge.org
  
  Script that constructs the leaderboard datasets.

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk
  (Honourable mention: Neil P. Oxtoby)
  
 ''', formatter_class=RawTextHelpFormatter
)

parser.add_argument('--spreadsheetFolder', dest='spreadsheetFolder', default='..',
                   help='folder of output spreadsheets')


CN = 1
MCI = 2
AD = 3

np.random.seed(1)

args = parser.parse_args()


def makeLBcolumns(filePath, adniMergeDf):

  # LB1 - prelim training set
  # LB2 - prelim prediction set
  # LB4 - prelim test set

  # LB2
  # contains CN and MCI subjects from ADNI1 who have at least one visit in ADNI GO/2
  # these subjects must be CN or MCI at last timepoint in ADNI1
  # LB4
  # contains same subjects as LB2, just the next timepoint (from ADNI GO/2)
  # LB1 contains all the remaining subjects

  unqRids = np.unique(adniMergeDf['RID'])
  nrSubjLong = unqRids.shape[0]
  atLeastTwoTimeptsInAdni1Mask = np.zeros(nrSubjLong, bool)
  atLeastOneTimeptInAdniGo2Mask = np.zeros(nrSubjLong, bool)
  lastKnownDiag = np.zeros(nrSubjLong, int)  # subjects with at least one visit diagnosed as CN or MCI
  ctlDxchange = [1, 7, 9]
  mciDxchange = [2, 4, 8]
  adDxChange = [3, 5, 6]
  adniGOor2Mask = np.logical_or(adniMergeDf['COLPROT'] == 'ADNIGO',
    adniMergeDf['COLPROT'] == 'ADNI2')

  for s in range(unqRids.shape[0]):
    maskCurrSubjADNI1 = np.logical_and(adniMergeDf['RID'] == unqRids[s],
      adniMergeDf['COLPROT'] == 'ADNI1')
    if np.sum(maskCurrSubjADNI1) >= 2:
      atLeastTwoTimeptsInAdni1Mask[s] = True
    else:
      continue

    dxchangeCurrSubjADNI1 =  adniMergeDf['DXCHANGE'][maskCurrSubjADNI1]
    visitsOrder = np.argsort(adniMergeDf['EXAMDATE'][maskCurrSubjADNI1])  # find order from EXAMDATE
    dxchangeCurrSubjOrdADNI1 = dxchangeCurrSubjADNI1.iloc[visitsOrder]

    dxchangeCurrSubjOrdFiltADNI1 = dxchangeCurrSubjOrdADNI1[
      np.logical_not(np.isnan(dxchangeCurrSubjOrdADNI1))]

    # make sure subject has last timepoint with CN or MCI diagnosis.
    if np.in1d(dxchangeCurrSubjOrdFiltADNI1.iloc[-1], ctlDxchange):
      lastKnownDiag[s] = CN
    elif np.in1d(dxchangeCurrSubjOrdFiltADNI1.iloc[-1], mciDxchange):
      lastKnownDiag[s] = MCI
    elif np.in1d(dxchangeCurrSubjOrdFiltADNI1.iloc[-1], adDxChange):
      lastKnownDiag[s] = AD
    else:
      raise TypeError('diag not recognised', dxchangeCurrSubjOrdFiltADNI1.iloc[-1])

    maskCurrSubjADNIGo2 = np.logical_and(adniMergeDf['RID'] == unqRids[s], adniGOor2Mask)
    if np.sum(maskCurrSubjADNIGo2) >= 1:
      atLeastOneTimeptInAdniGo2Mask[s] = True


  lastDiagCnMCI = np.logical_or(lastKnownDiag == CN, lastKnownDiag == MCI)
  filterMask = np.logical_and(atLeastTwoTimeptsInAdni1Mask, lastDiagCnMCI)
  filterMask = np.logical_and(filterMask, atLeastOneTimeptInAdniGo2Mask)

  potentialRIDsLB2 = unqRids[filterMask]
  lastKnownDiag = lastKnownDiag[filterMask]
  nrPotRIDs = potentialRIDsLB2.shape[0]
  potRIDsCN = potentialRIDsLB2[lastKnownDiag == CN]
  potRIDsMCI = potentialRIDsLB2[lastKnownDiag == MCI]

  # now take the potential RIDs and sample 2/3 of data for training
  nrCN = int(potRIDsCN.shape[0] * 2.0/ 3)
  nrMCI = int(potRIDsMCI.shape[0]  * 2.0/ 3)
  selectedRIDsCN = np.random.choice(potRIDsCN, nrCN)
  selectedRIDsMCI = np.random.choice(potRIDsMCI, nrMCI)
  selectedRIDs = np.concatenate((selectedRIDsCN, selectedRIDsMCI), axis=0)
  nrSelRIDs = selectedRIDs.shape[0]

  LB2 = np.zeros(adniMergeDf.shape[0], int)
  LB4 = np.zeros(adniMergeDf.shape[0], int)

  for s in range(nrSelRIDs):
    # for the current subject s, set all the visits in ADNI1 to be in LB2
    maskCurrSubjADNI1 = np.logical_and(adniMergeDf['RID'] == selectedRIDs[s],
      adniMergeDf['COLPROT'] == 'ADNI1')
    LB2[maskCurrSubjADNI1] = 1

    # for the current subject s, set all the visits in ADNIGO/2 to be in LB4
    maskCurrSubjADNIGO2 = np.logical_and(adniMergeDf['RID'] == selectedRIDs[s], adniGOor2Mask)
    LB4[maskCurrSubjADNIGO2] = 1

  # set LB1 to be all other subjects not included in LB2 and LB4
  notLB2orLB4Mask = np.logical_not(np.logical_or(LB2 == 1, LB4 == 1))
  ridNotSelectedMask = np.logical_not(np.in1d(adniMergeDf['RID'], selectedRIDs))
  LB1 = ridNotSelectedMask.astype(int)

  return LB1, LB2, LB4


tadpoleFile = '%s/TADPOLE_D1_D2.csv' % args.spreadsheetFolder
tadpoleDf = pd.read_csv(tadpoleFile, low_memory=False)
d2File = 'D2_column.csv'
LB1, LB2, LB4 = makeLBcolumns(d2File, tadpoleDf)

# build data frame for LB1 and LB2
lb12Df = pd.DataFrame(np.nan,index=range(LB1.shape[0]), columns=('RID', 'PTID', 'VISCODE'
  ,'DXCHANGE', 'DX', 'COLPROT', 'ORIGPROT', 'EXAMDATE'
  ,'LB1', 'LB2'))

lb12Df['RID'] = tadpoleDf['RID']
lb12Df['PTID'] = tadpoleDf['PTID']
lb12Df['VISCODE'] = tadpoleDf['VISCODE']
lb12Df['LB1'] = LB1
lb12Df['LB2'] = LB2
lb12Df['DXCHANGE'] = tadpoleDf['DXCHANGE']
lb12Df['DX'] = tadpoleDf['DX']
lb12Df['COLPROT'] = tadpoleDf['COLPROT']
lb12Df['ORIGPROT'] = tadpoleDf['ORIGPROT']
lb12Df['EXAMDATE'] = tadpoleDf['EXAMDATE']

lb12Df.to_csv('TADPOLE_LB1_LB2.csv',index=False)
print('TADPOLE_LB1_LB2.csv created in local folder')

# build data frame for LB4
lb4Df = pd.DataFrame(np.nan,index=range(LB4.shape[0]), columns=('RID', 'LB4', 'CognitiveAssessmentDate', 'Diagnosis', 'ADAS13', 'ScanDate', 'Ventricles'
))

lb4Df['RID'] = tadpoleDf['RID']
lb4Df['LB4'] = LB4
lb4Df['CognitiveAssessmentDate'] = tadpoleDf['EXAMDATE']
lb4Df['Diagnosis'] = tadpoleDf['DXCHANGE']
lb4Df['ADAS13'] = tadpoleDf['ADAS13']
lb4Df['ScanDate'] = tadpoleDf['EXAMDATE'] # for now set the scan date to be EXAMDATE
lb4Df['Ventricles'] = tadpoleDf['Ventricles'] / tadpoleDf['ICV'] # uses FS X-sectional volumes from ADNIMERGE



# convert diagnoses such as 'MCI to Dementia' to 'Dementia', etc ...
# ctlDxchange = [1, 7, 9] mciDxchange = [2, 4, 8] adDxChange = [3, 5, 6]
mapping = {1:'CN', 7:'CN', 9:'CN', 2:'MCI', 4:'MCI', 8:'MCI', 3:'AD', 5:'AD', 6:'AD'}
lb4Df.replace({'Diagnosis': mapping}, inplace=True)
lb4Df = lb4Df[lb4Df['LB4'] == 1]
lb4Df.reset_index(drop=True, inplace=True)

lb4Df.to_csv('TADPOLE_LB4.csv',index=False)
print('TADPOLE_LB4.csv created in local folder')



###### Make the Leaderboard submission skeleton (or template) ##################
###### This file is not used by other scripts (and thus not necessary), ########
######  it is for participants' reference only #################################

nrOfForecastsPerSubj = 7*12 # 7 years * 12 months
unqRIDs = np.unique(lb12Df['RID'][lb12Df['LB2'] == 1])
nrUnqRIDs = unqRIDs.shape[0]
lbSubmissionDf = pd.DataFrame('', index=range(nrUnqRIDs*nrOfForecastsPerSubj), columns=('RID', 'Forecast Month', 'Forecast Date',
'CN relative probability', 'MCI relative probability', 'AD relative probability',	'ADAS13',	'ADAS13 50% CI lower',
'ADAS13 50% CI upper', 'Ventricles_ICV', 'Ventricles_ICV 50% CI lower',	'Ventricles_ICV 50% CI upper'))

# lastDateLB4Str = np.max(lb4Df['CognitiveAssessmentDate'][lb4Df['LB4'] == 1])
# print('lastDateLB4Str', lastDateLB4Str) # last date for LB2 is 2011-04-20, most finish at 2010-04-xx
# first date for LB4 is 2010-05-14
# set the forecasts to start from 2010-05.
# There will be very few subjects in LB2 who have visits after this date, but that is ok,
# since the evaluation script will only use the predictions closest to the LB4 visits.

forecastStartDate = datetime.strptime('2010-05-01', '%Y-%m-%d')

for s in range(nrUnqRIDs):
  for f in range(nrOfForecastsPerSubj):
    indexInDf = s*nrOfForecastsPerSubj + f

    # set forecast date start to be one month after EXAMDATE. The predictions have to go for 7 years
    forecastDateCurr = forecastStartDate + dateutil.relativedelta.relativedelta(months=f)
    lbSubmissionDf.iloc[indexInDf] = [unqRIDs[s], f+1, forecastDateCurr.strftime('%Y-%m'), '', '', '', '', '', '', '', '','']


lbSubmissionDf.to_csv('TADPOLE_Submission_Leaderboard_TeamName.csv',index=False)
print('Submission skeleton TADPOLE_Submission_Leaderboard_TeamName.csv created in local folder')
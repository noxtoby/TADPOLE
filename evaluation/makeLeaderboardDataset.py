import os
import numpy as np
import csv
from datetime import datetime
import pickle
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
  description=r'''
  Script that constructs the leaderboard datasets.

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk

 ''', formatter_class=RawTextHelpFormatter
)

CN = 1
MCI = 2
AD = 3

np.random.seed(1)

args = parser.parse_args()


def makeDcolumns(filePath, adniMergeDf):



  # LB1 - prelim training set
  # LB2 - prelim prediction set
  # LB4 - prelim test set

  #  LB2
  # contains CN and MCI subjects from ADNI1 who have at least one visit in ADNI GO/2
  # these subjects must be CN or MCI at last timepoint in ADNI1
  # LB4
  # contains same subjects as D1_2, just the next timepoint (from ADNI GO/2)
  # LB1 contains all the remaining subjects

  unqRids = np.unique(adniMergeDf['RID'])
  nrSubjLong = unqRids.shape[0]
  atLeastTwoTimeptsInAdni1Mask = np.zeros(nrSubjLong, bool)
  atLeastOneTimeptInAdniGo2Mask = np.zeros(nrSubjLong, bool)
  lastDiag = np.zeros(nrSubjLong, int)  # subjects with at least one visit diagnosed as CN or MCI
  ctlMciDxchange = ['1', '2', '4', '7', '8', '9']
  ctlDxchange = ['1', '7', '9']
  mciDxchange = ['2', '4', '8']
  adDxChange = ['3', '5', '6']
  adniGOor2Mask = np.logical_or(adniMergeDf['COLPROT'] == 'ADNIGO',
    adniMergeDf['COLPROT'] == 'ADNI2')

  for s in range(unqRids.shape[0]):
    maskCurrSubjADNI1 = np.logical_and(adniMergeDf['RID'] == unqRids[s],
      adniMergeDf['COLPROT'] == 'ADNI1')
    if np.sum(maskCurrSubjADNI1) >= 2:
      atLeastTwoTimeptsInAdni1Mask[s] = True
    else:
      continue

    dxchangeCurrSubjADNI1 =  adniMergeDf['DXCHANGE']
    visitsOrder = np.argsort(adniMergeDf['EXAMDATE'][maskCurrSubjADNI1])  # find order from EXAMDATE
    dxchangeCurrSubjOrdADNI1 = dxchangeCurrSubjADNI1[visitsOrder]
    dxchangeCurrSubjOrdFiltADNI1 = dxchangeCurrSubjOrdADNI1[dxchangeCurrSubjOrdADNI1 != '']
    # print(dxchangeCurrSubjOrdFilt, dxchangeCurrSubjOrd)
    # print(adsa)
    # make sure subject has last timepoint with CN or MCI diagnosis.
    if np.in1d(dxchangeCurrSubjOrdFiltADNI1[-1], ctlDxchange):
      lastDiag[s] = CN
    elif np.in1d(dxchangeCurrSubjOrdFiltADNI1[-1], mciDxchange):
      lastDiag[s] = MCI
    elif np.in1d(dxchangeCurrSubjOrdFiltADNI1[-1], adDxChange):
      lastDiag[s] = AD

    maskCurrSubjADNIGo2 = np.logical_and(adniMergeDf['RID'] == unqRids[s], adniGOor2Mask)
    if np.sum(maskCurrSubjADNIGo2) >= 1:
      atLeastOneTimeptInAdniGo2Mask[s] = True

  lastDiagCnMCI = np.logical_or(lastDiag == CN, lastDiag == MCI)
  # print('atLeastTwoTimeptsInAdni1Mask', np.sum(atLeastTwoTimeptsInAdni1Mask))
  filterMask = np.logical_and(atLeastTwoTimeptsInAdni1Mask, lastDiagCnMCI)
  # print('atLeastTwoTimeptsInAdni1Mask, lastDiagCnMCI', np.sum(filterMask))
  filterMask = np.logical_and(filterMask, atLeastOneTimeptInAdniGo2Mask)


  potentialRIDsLB2 = unqRids[filterMask]
  lastDiag = lastDiag[filterMask]
  nrPotRIDs = potentialRIDsLB2.shape[0]
  potRIDsCN = potentialRIDsLB2[lastDiag == CN]
  potRIDsMCI = potentialRIDsLB2[lastDiag == MCI]

  # now take the potential RIDs and sample 2/3 of data for training
  nrCN = int(potRIDsCN.shape[0] / 1.5)
  nrMCI = int(potRIDsMCI.shape[0] / 1.5)
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
    # visitsOrderADNIGO2 = np.argsort(mergeAll[maskCurrSubjADNIGO2, 6])  # find order from EXAMDATE
    # currSubjADNIGO2IdxOrd = np.where(maskCurrSubjADNIGO2)[0][visitsOrderADNIGO2]
    # LB4[currSubjADNIGO2IdxOrd[0]] = 1
    LB4[maskCurrSubjADNIGO2] = 1

  # set LB1 to be all other subjects not included in LB2 and LB4
  notLB2orLB4Mask = np.logical_not(np.logical_or(LB2 == 1, LB4 == 1))
  ridNotSelectedMask = np.logical_not(np.in1d(adniMergeDf['RID'], selectedRIDs))
  LB1 = ridNotSelectedMask.astype(int)


adniMergeFile = 'TADPOLE_D1_D2.csv'
adniMergeDf = pd.read_csv(adniMergeFile)
d2File = 'D2_column.csv'
makeDcolumns(d2File, adniMergeDf)


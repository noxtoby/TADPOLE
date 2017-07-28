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

def makeDcolumns(filePath, mergeAll, ridInd, ptidInd, visCodeInd, mergeHeader, dictAll):
  '''

  :param filePath: file containing the ADNI1 s/s
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
    headerPlus = mergeHeader[:4] + ['D1', 'D2', 'D1_1', 'D1_2', 'D1_4'] + mergeHeader[4:]



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




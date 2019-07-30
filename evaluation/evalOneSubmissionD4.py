import pandas as pd
import time
import random
import numpy as np
from datetime import timedelta
from datetime import datetime
import MAUC
import argparse

parser = argparse.ArgumentParser(usage='python3 evalOneSubmission.py',
  description=r'''
  TADPOLE Evaluation Script:
  The program computes the following matrics:

  Clinical diagnosis prediction:

  1. Multiclass area under the receiver operating curve (mAUC)
  2. Balanced classification accuracy (BCA)

  Continuous feature predictions:
  3. Mean Absolute Error (MAE)
  4. Coverage Probability Accuracy (CPA)
  5. Weighted Error Score (WES)

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk

  ''')

def calcBCA(estimLabels, trueLabels, nrClasses):

  # Balanced Classification Accuracy

  bcaAll = []
  for c0 in range(nrClasses):
    # c0 can be either CTL, MCI or AD

    # one example when c0=CTL
    # TP - label was estimated as CTL, and the true label was also CTL
    # FP - label was estimated as CTL, but the true label was not CTL (was either MCI or AD).
    TP = np.sum((estimLabels == c0) & (trueLabels == c0))
    TN = np.sum((estimLabels != c0) & (trueLabels != c0))
    FP = np.sum((estimLabels == c0) & (trueLabels != c0))
    FN = np.sum((estimLabels != c0) & (trueLabels == c0))

    # sometimes the sensitivity of specificity can be NaN, if the user doesn't forecast one of the classes.
    # In this case we assume a default value for sensitivity/specificity
    if (TP+FN) == 0:
      sensitivity = 0.5
    else:
      sensitivity = (1. * TP)/(TP+FN)

    if (TN+FP) == 0:
      specificity = 0.5
    else:
      specificity = (1. * TN)/(TN+FP)

    bcaCurr = 0.5*(sensitivity+specificity)
    bcaAll += [bcaCurr]
    # print('bcaCurr %f TP %f TN %f FP %f FN %f' % (bcaCurr, TP, TN, FP, FN))

  return np.mean(bcaAll)

def parseData(d4Df, forecastDf, diagLabels):

  trueDiag = d4Df['Diagnosis']
  trueADAS = d4Df['ADAS13']
  trueVents = d4Df['Ventricles']

  nrSubj = d4Df.shape[0]

  zipTrueLabelAndProbs = []

  hardEstimClass = -1 * np.ones(nrSubj, int)
  adasEstim = -1 * np.ones(nrSubj, float)
  adasEstimLo = -1 * np.ones(nrSubj, float)  # lower margin
  adasEstimUp = -1 * np.ones(nrSubj, float)  # upper margin
  ventriclesEstim = -1 * np.ones(nrSubj, float)
  ventriclesEstimLo = -1 * np.ones(nrSubj, float)  # lower margin
  ventriclesEstimUp = -1 * np.ones(nrSubj, float)  # upper margin

  invalidResultReturn = (None,None,None,None,None,None,None,None,None,None,None)
  invalidFlag = False
  # for each subject in D4 match the closest user forecasts
  for s in range(nrSubj):
    currSubjMask = d4Df['RID'].iloc[s] == forecastDf['RID']
    currSubjData = forecastDf[currSubjMask]

    # if subject is missing
    if currSubjData.shape[0] == 0:
      print('WARNING: Subject RID %s missing from user forecasts' % d4Df['RID'].iloc[s])
      invalidFlag = True
      continue

    # if not all forecast months are present
    if currSubjData.shape[0] < 4*12: # check if at least 4 years worth of forecasts exist
      print('WARNING: Missing forecast months for subject with RID %s' % d4Df['RID'].iloc[s])
      invalidFlag = True
      continue

    currSubjData = currSubjData.reset_index(drop=True)

    timeDiffsScanCog = [d4Df['CognitiveAssessmentDate'].iloc[s] - d for d in currSubjData['Forecast Date']]
    indexMin = np.argsort(np.abs(timeDiffsScanCog))[0]

    pCN = currSubjData['CN relative probability'].iloc[indexMin]
    pMCI = currSubjData['MCI relative probability'].iloc[indexMin]
    pAD = currSubjData['AD relative probability'].iloc[indexMin]

    # normalise the relative probabilities by their sum
    pSum = (pCN + pMCI + pAD)
    pCN /= pSum
    pMCI /= pSum
    pAD /= pSum

    if np.isnan(pSum):
      hardEstimClass[s] = -1
    else:
      hardEstimClass[s] = np.argmax([pCN, pMCI, pAD])

    adasEstim[s] = currSubjData['ADAS13'].iloc[indexMin]
    adasEstimLo[s] = currSubjData['ADAS13 50% CI lower'].iloc[indexMin]
    adasEstimUp[s] = currSubjData['ADAS13 50% CI upper'].iloc[indexMin]

    # for the mri scan find the forecast closest to the scan date,
    # which might be different from the cognitive assessment date
    timeDiffsScanMri = [d4Df['ScanDate'].iloc[s] - d for d in currSubjData['Forecast Date']]
    indexMinMri = np.argsort(np.abs(timeDiffsScanMri))[0]

    ventriclesEstim[s] = currSubjData['Ventricles_ICV'].iloc[indexMinMri]
    ventriclesEstimLo[s] = currSubjData['Ventricles_ICV 50% CI lower'].iloc[indexMinMri]
    ventriclesEstimUp[s] = currSubjData['Ventricles_ICV 50% CI upper'].iloc[indexMinMri]
    # print('%d probs' % d4Df['RID'].iloc[s], pCN, pMCI, pAD)

    # print(trueDiag.iloc[s])
    if not np.isnan(trueDiag.iloc[s]):
      zipTrueLabelAndProbs += [(trueDiag.iloc[s], [pCN, pMCI, pAD])]


  # if invalidFlag:
  #   # if at least one subject was missing or if
  #   raise ValueError('Submission was incomplete. Please resubmit')

  # If there are NaNs in D4, filter out them along with the corresponding user forecasts
  # This can happen if rollover subjects don't come for visit in ADNI3.
  notNanMaskDiag = np.logical_not(np.isnan(trueDiag))
  trueDiagFilt = trueDiag[notNanMaskDiag]
  hardEstimClassFilt = hardEstimClass[notNanMaskDiag]

  notNanMaskADAS = np.logical_not(np.isnan(trueADAS))
  trueADASFilt = trueADAS[notNanMaskADAS]
  adasEstim = adasEstim[notNanMaskADAS]
  adasEstimLo = adasEstimLo[notNanMaskADAS]
  adasEstimUp = adasEstimUp[notNanMaskADAS]

  notNanMaskVents = np.logical_not(np.isnan(trueVents))
  trueVentsFilt = trueVents[notNanMaskVents]
  ventriclesEstim = ventriclesEstim[notNanMaskVents]
  ventriclesEstimLo = ventriclesEstimLo[notNanMaskVents]
  ventriclesEstimUp = ventriclesEstimUp[notNanMaskVents]

  assert trueDiagFilt.shape[0] == hardEstimClassFilt.shape[0]
  assert trueADASFilt.shape[0] == adasEstim.shape[0] == adasEstimLo.shape[0] == adasEstimUp.shape[0]
  assert trueVentsFilt.shape[0] == ventriclesEstim.shape[0] == \
         ventriclesEstimLo.shape[0] == ventriclesEstimUp.shape[0]

  return zipTrueLabelAndProbs, hardEstimClassFilt, adasEstim, adasEstimLo, adasEstimUp, \
    ventriclesEstim, ventriclesEstimLo, ventriclesEstimUp, trueDiagFilt, trueADASFilt, trueVentsFilt


def evalOneSubReturnAll(d4Df, forecastDf):
  """
    Evaluates one submission.

  Parameters
  ----------
  d4Df - Pandas data frame containing the D4 dataset
  subDf - Pandas data frame containing user forecasts for D2 subjects.

  Returns
  -------
  mAUC - multiclass Area Under Curve
  bca - balanced classification accuracy
  adasMAE - ADAS13 Mean Aboslute Error
  ventsMAE - Ventricles Mean Aboslute Error
  adasCovProb - ADAS13 Coverage Probability for 50% confidence interval
  ventsCovProb - Ventricles Coverage Probability for 50% confidence interval

  """
  # print(forecastDf[['RID', 'Forecast Month', 'Forecast Date', ]])
  # print(forecastDf['Forecast Date'].dtype)
  if not np.issubdtype(forecastDf['Forecast Date'].dtype, np.datetime64):
    forecastDf['Forecast Date'] = [datetime.strptime(x, '%Y-%m') for x in forecastDf['Forecast Date']] # considers every month estimate to be the actual first day 2017-01
  # if isinstance(d4Df['Diagnosis'].iloc[0], str):


  diagLabels = ['CN', 'MCI', 'AD']

  zipTrueLabelAndProbs, hardEstimClass, adasEstim, adasEstimLo, adasEstimUp, \
      ventriclesEstim, ventriclesEstimLo, ventriclesEstimUp, trueDiagFilt, trueADASFilt, trueVentsFilt = \
    parseData(d4Df, forecastDf, diagLabels)
  zipTrueLabelAndProbs = list(zipTrueLabelAndProbs)

  ########## compute metrics for the clinical status #############

  ##### Multiclass AUC (mAUC) #####
  # print('zipTrueLabelAndProbs', zipTrueLabelAndProbs)
  if np.isnan(zipTrueLabelAndProbs[0][1][0]):
    mAUC = np.nan
    bca = np.nan
  else:
    nrClasses = len(diagLabels)
    mAUC = MAUC.MAUC(zipTrueLabelAndProbs, num_classes=nrClasses)

    ### Balanced Classification Accuracy (BCA) ###
    trueDiagFilt = trueDiagFilt.astype(int)
    bca = calcBCA(hardEstimClass, trueDiagFilt, nrClasses=nrClasses)



  ####### compute metrics for Ventricles and ADAS13 ##########

  #### Mean Absolute Error (MAE) #####

  # print('adasEstim',adasEstim)
  # print('trueADASFilt', trueADASFilt)
  # print(das)
  if (adasEstim == 0).all():
    adasEstim = np.nan * adasEstim

  if (ventriclesEstim == 0).all():
    ventriclesEstim = np.nan * ventriclesEstim


  adasErrors = np.abs(adasEstim - trueADASFilt)
  ventsErrors = np.abs(ventriclesEstim - trueVentsFilt)
  adasMAE = np.mean(adasErrors)
  ventsMAE = np.mean(ventsErrors)

  ##### Weighted Error Score (WES) ####
  # use abs value as one team (BIGS) put the intervals the other way around
  adasNullConfMask = (np.abs(adasEstimUp - adasEstimLo)) != 0
  if adasNullConfMask.all() and (not np.isnan(adasEstimUp).all()):
    adasCoeffs = 1.0/(np.abs(adasEstimUp - adasEstimLo))
    adasCoeffs[np.isnan(adasCoeffs)] = 0
  else:
    adasCoeffs = np.ones(adasEstimUp.shape[0])


  adasWES = np.sum(adasCoeffs * adasErrors)/np.sum(adasCoeffs)

  if np.sum(adasCoeffs) == 0:
    print(adasEstimUp)
    print(adasEstimLo)
    import pdb
    pdb.set_trace()


  ventNullConfMask = (np.abs(ventriclesEstimUp - ventriclesEstimLo)) != 0
  if ventNullConfMask.all() and (not np.isnan(ventriclesEstimUp).all()):
    ventsCoeffs = 1.0 / np.abs(ventriclesEstimUp - ventriclesEstimLo)
    ventsCoeffs[np.isnan(ventsCoeffs)] = 0
  else:
    ventsCoeffs = np.ones(ventriclesEstimUp.shape[0])


  ventsWES = np.sum(ventsCoeffs * ventsErrors)/np.sum(ventsCoeffs)

  if np.sum(ventsCoeffs) == 0:
    print(ventriclesEstimUp)
    print(ventriclesEstimLo)
    import pdb
    pdb.set_trace()

  #### Coverage Probability Accuracy (CPA) ####

  adasCovProb = np.sum((adasEstimLo < trueADASFilt) &
                       (adasEstimUp > trueADASFilt))/trueADASFilt.shape[0]
  adasCPA = np.abs(adasCovProb - 0.5)

  ventsCovProb = np.sum((ventriclesEstimLo < trueVentsFilt) &
                        (ventriclesEstimUp > trueVentsFilt))/trueVentsFilt.shape[0]
  # print((ventriclesEstimLo < trueVentsFilt) &
  #                       (ventriclesEstimUp > trueVentsFilt))
  ventsCPA = np.abs(ventsCovProb - 0.5)

  if ventsMAE > 20 or ventsWES > 20:
    # if score is too high it means they didn't normalise ventricle volume for ICV.
    # We can't fix this easily, so set them as NaNs.
    ventsMAE = np.nan
    ventsWES = np.nan

  if np.isnan(adasMAE):
    adasWES = np.nan
    adasCPA = np.nan

  if np.isnan(ventsMAE):
    ventsWES = np.nan
    ventsCPA = np.nan


  return mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA, hardEstimClass, trueDiagFilt, adasErrors, ventsErrors


def evalOneSub(d4Df, forecastDf):
  """
    Evaluates one submission.

  Parameters
  ----------
  d4Df - Pandas data frame containing the D4 dataset
  subDf - Pandas data frame containing user forecasts for D2 subjects.

  Returns
  -------
  mAUC - multiclass Area Under Curve
  bca - balanced classification accuracy
  adasMAE - ADAS13 Mean Aboslute Error
  ventsMAE - Ventricles Mean Aboslute Error
  adasCovProb - ADAS13 Coverage Probability for 50% confidence interval
  ventsCovProb - Ventricles Coverage Probability for 50% confidence interval

  """

  mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA, _, _, _, _ \
    = evalOneSubReturnAll(d4Df, forecastDf)

  return mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA

def evalOneSubWithFormatting(d4Df, subDf):
  d4Df['CognitiveAssessmentDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['CognitiveAssessmentDate']]
  d4Df['ScanDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['ScanDate']]
  if not np.issubdtype(d4Df['Diagnosis'].dtype, np.number):
    mapping = {'CN': 0, 'MCI': 1, 'AD': 2}
    d4Df.replace({'Diagnosis': mapping}, inplace=True)

  subDf[['Forecast Date']] = subDf[['Forecast Date']].astype(str)

  # don't catch the exception here, as this main function is used to test if the submission if correct
  return evalOneSub(d4Df, subDf)

def printMetricsRes(mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA):
  print('########### Metrics for clinical status ##################')
  print('mAUC', mAUC)
  print('bca', bca)
  print('\n########### Mean Absolute Error (MAE) ##################')
  print('adasMAE', adasMAE, 'ventsMAE', ventsMAE)
  print('\n########### Weighted Error Score (WES) ##################')
  print('adasWES', adasWES, 'ventsWES', ventsWES)
  print('\n########### Coverage Probability Accuracy ##################')
  print('adasCPA', adasCPA, 'ventsCPA', ventsCPA)

  print('\n\n########### File is ready for submission to TADPOLE ###########')

def printMetricsResCompact(mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA):
  print('DX:    mAUC:%f   bca:%f' %(mAUC, bca))
  print('ADAS:  MAE :%f   WES:%f   CPA:%f' % (adasMAE, adasWES, adasCPA))
  print('VENTS: MAE :%f   WES:%f   CPA:%f' % (ventsMAE, ventsWES, ventsCPA))

if __name__ == "__main__":

  parser.add_argument('--d4File', dest='d4File', help='CSV file containing the D4 dataset. '\
    'Needs to be in the same format of D4_dummy.csv')

  parser.add_argument('--forecastFile', dest='forecastFile', help='CSV file containing the user '
    'forecasts for subjects in D2. Needs to be in the same format as '
    'TADPOLE_Submission_TeamName1.xlsx or TADPOLE_Submission_Leaderboard_TeamName1.csv')

  parser.add_argument('--leaderboard', action='store_true', help='pass this flag if the submission is a leaderboard submission. It ensures the filename is in the right format')

  args = parser.parse_args()

  d4File = args.d4File
  forecastFile = args.forecastFile

  if args.leaderboard:
    if ('TADPOLE_Submission_Leaderboard_' not in forecastFile) or (not forecastFile.endswith('.csv')):
      raise ValueError('Leaderboard submission filename is not in the correct format: TADPOLE_Submission_Leaderboard_TeamName.csv')
  else:
    if ('TADPOLE_Submission_' not in forecastFile) or (not forecastFile.endswith('.csv')):
      raise ValueError('Submission filename is not in the correct format: TADPOLE_Submission_TeamName.csv.')

  d4Df = pd.read_csv(d4File)
  subDf = pd.read_csv(forecastFile)


  # don't catch the exception here, as this main function is used to test if the submission if correct
  mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA = \
    evalOneSubWithFormatting(d4Df, subDf)

  printMetricsRes(mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA)



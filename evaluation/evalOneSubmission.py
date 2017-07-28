import pandas as pd
import time
import random
import numpy as np
from datetime import timedelta
from datetime import datetime
import MAUC
import argparse

argparse.ArgumentParser(usage='python3 evalOneSubmission.py',
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
    for c1 in range(c0+1,nrClasses):
      # c0 = positive class  &  c1 = negative class
      TP = np.sum((hardEstimClass == c0) & (d4Df['Diagnosis'] == c0))
      TN = np.sum((hardEstimClass == c1) & (d4Df['Diagnosis'] == c1))
      FP = np.sum((hardEstimClass == c1) & (d4Df['Diagnosis'] == c0))
      FN = np.sum((hardEstimClass == c0) & (d4Df['Diagnosis'] == c1))

      bcaCurr = 0.5*(TP/(TP+FN)+TN/(TN+FP))
      bcaAll += [bcaCurr]

  return np.mean(bcaAll)

def parseData(d4Df, subDf, diagLabels):
  nrSubj = d4Df.shape[0]

  zipTrueLabelAndProbs = []

  hardEstimClass = -1 * np.ones(nrSubj, int)
  adasEstim = -1 * np.ones(nrSubj, float)
  adasEstimLo = -1 * np.ones(nrSubj, float)  # lower margin
  adasEstimUp = -1 * np.ones(nrSubj, float)  # upper margin
  ventriclesEstim = -1 * np.ones(nrSubj, float)
  ventriclesEstimLo = -1 * np.ones(nrSubj, float)  # lower margin
  ventriclesEstimUp = -1 * np.ones(nrSubj, float)  # upper margin

  # for each subject match the closest forecasts
  for s in range(nrSubj):
    currSubjMask = d4Df['RID'].iloc[s] == subDf['RID']
    currSubjData = subDf[currSubjMask]
    currSubjData = currSubjData.reset_index(drop=True)

    timeDiffsScanCog = [d4Df['CogAssessmentDate'].iloc[s] - d for d in currSubjData['ForecastDate']]
    indexMin = np.argsort(np.abs(timeDiffsScanCog))[0]
    # print('timeDiffsScanMri', indexMin, timeDiffsScanMri)

    pCN = currSubjData['CNRelativeProbability'].iloc[indexMin]
    pMCI = currSubjData['MCIRelativeProbability'].iloc[indexMin]
    pAD = currSubjData['ADRelativeProbability'].iloc[indexMin]

    hardEstimClass[s] = np.argmax([pCN, pMCI, pAD])

    adasEstim[s] = currSubjData['ADAS13'].iloc[indexMin]
    adasEstimLo[s] = currSubjData['ADAS1350_CILower'].iloc[indexMin]
    adasEstimUp[s] = currSubjData['ADAS1350_CIUpper'].iloc[indexMin]

    # for the mri scan find the forecast closest to the scan date,
    # which might be different from the cognitive assessment date
    timeDiffsScanMri = [d4Df['ScanDate'].iloc[s] - d for d in currSubjData['ForecastDate']]
    indexMinMri = np.argsort(np.abs(timeDiffsScanMri))[0]

    ventriclesEstim[s] = currSubjData['Ventricles_ICV'].iloc[indexMinMri]
    ventriclesEstimLo[s] = currSubjData['Ventricles_ICV50_CILower'].iloc[indexMinMri]
    ventriclesEstimUp[s] = currSubjData['Ventricles_ICV50_CIUpper'].iloc[indexMinMri]
    # print('%d probs' % d4Df['RID'].iloc[s], pCN, pMCI, pAD)

    zipTrueLabelAndProbs += [(trueDiag.iloc[s], [pCN, pMCI, pAD])]


  return zipTrueLabelAndProbs, hardEstimClass, adasEstim, adasEstimLo, adasEstimUp, \
    ventriclesEstim, ventriclesEstimLo, ventriclesEstimUp

d4Df = pd.read_csv('D4_dummy.csv')
subDf = pd.read_csv('ExampleForecastFromD2.csv')

subDf['ForecastDate'] = [datetime.strptime(x, '%Y-%m') for x in subDf['ForecastDate']] # considers every month estimate to be the actual first day 2017-01
d4Df['CogAssessmentDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['CogAssessmentDate']]
d4Df['ScanDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['ScanDate']]


mapping = {'CN' : 0, 'MCI' : 1, 'AD' : 2}
d4Df.replace({'Diagnosis':mapping}, inplace=True)

trueDiag = d4Df['Diagnosis']
trueADAS = d4Df['ADAS13']
trueVents = d4Df['Ventricles']

diagLabels = ['CN', 'MCI', 'AD']

zipTrueLabelAndProbs, hardEstimClass, adasEstim, adasEstimLo, adasEstimUp, \
    ventriclesEstim, ventriclesEstimLo, ventriclesEstimUp = parseData(d4Df, subDf, diagLabels)
zipTrueLabelAndProbs = list(zipTrueLabelAndProbs)

########## compute metrics for the clinical status #############
print('########### Metrics for clinical status ##################')

# Multiclass AUC

nrClasses = len(diagLabels)
mAUC = MAUC.MAUC(zipTrueLabelAndProbs, num_classes=nrClasses)

bca = calcBCA(hardEstimClass, trueDiag, nrClasses=nrClasses)
print('Clinical diagnosis metrics: should give around 0.5 since they were generated randomly')
print('mAUC', mAUC)
print('bca', bca)

####### compute metrics for Ventricles and ADAS13 ##########

#### Mean Absolute Error (MAE) #####

adasMAE = np.mean(np.abs(adasEstim - trueADAS))
ventsMAE = np.mean(np.abs(ventriclesEstim - trueVents))
print('########### Mean Absolute Error (MAE) ##################')
print('MAE should be around sqrt(2/pi)*sigma, which is 1.190 for ADAS and 1910 for Ventricles')
print('adasMAE', adasMAE, 'ventsMAE', ventsMAE)

##### Weighted Error Score (WES) ####
adasCoeffs = 1/(adasEstimUp - adasEstimLo)
adasWES = np.sum(adasCoeffs * np.abs(adasEstim - trueADAS))/np.sum(adasCoeffs)

ventsCoeffs = 1/(ventriclesEstimUp - ventriclesEstimLo)
ventsWES = np.sum(ventsCoeffs * np.abs(ventriclesEstim - trueVents))/np.sum(ventsCoeffs)

print('WES should be similar to MAE, since the coefficients are almost equal.')
print('adasWES', adasWES, 'ventsWES', ventsWES)

#### Coverage Probability Accuracy (CPA) ####
print('########### Coverage Probability Accuracy (CPA) ##################')

adasActualCoverageProb = np.sum((adasEstimLo < trueADAS) & (adasEstimUp > trueADAS))/trueADAS.shape[0]
adasCPA = np.abs(adasActualCoverageProb - 0.5)

ventsActualCoverageProb = np.sum((ventriclesEstimLo < trueVents) &
                                 (ventriclesEstimUp > trueVents))/trueVents.shape[0]
ventsCPA = np.abs(ventsActualCoverageProb - 0.5)

print('adasCPA', adasCPA, 'ventsCPA', ventsCPA)
# print('adasActualCoverageProb', adasActualCoverageProb)
# print('ventsActualCoverageProb', ventsActualCoverageProb)

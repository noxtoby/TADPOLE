import pandas as pd
import time
import random
import numpy as np
from datetime import timedelta
from datetime import datetime
import argparse


argparse.ArgumentParser(usage='python3 makeDummyD4.py',
  description=r'''
  The program creates a dummy D4 dataset from an already generated forecast CSV spreadsheet:

    TADPOLE_Submission_TeamName1.csv

  This spreadsheet is assumed to be in the current folder.

  This is done by randomly selecting some months as ADNI3 future visits
  and making the D4 entries by adding noise to the estimated values.

  Author: Razvan V. Marinescu, razvan.marinescu.14@ucl.ac.uk

  ''')


stdDateFormat = '%Y-%m-%d'

def strTimeProp(start, end, format, prop):
  """Get a time at a proportion of a range of two formatted times.

  start and end should be strings specifying times formated in the
  given format (strftime-style), giving an interval [start, end].
  prop specifies how a proportion of the interval to be taken after
  start.  The returned time will be in the specified format.
  """

  stime = time.mktime(time.strptime(start, format))
  etime = time.mktime(time.strptime(end, format))

  ptime = stime + prop * (etime - stime)

  return datetime.fromtimestamp(ptime)

def randomDate(start, end, prop):
  return strTimeProp(start, end, stdDateFormat, prop)

df = pd.read_csv('TADPOLE_Submission_TeamName1.csv')
# print('df', df)

unqSubj = np.unique(df['RID'])
nrUnqSubj = unqSubj.shape[0]
startDate = '2018-03-10'
endDate = '2019-02-28'
# perturb the cognitive assessment date from the scan date by max 10 days
tdeltaCog = timedelta(days=10)

df['Forecast Date'] = [datetime.strptime(x, '%Y-%m') for x in df['Forecast Date']] # considers every month estimate to be the actual first day 2017-01
diagStr = ['CN', 'MCI', 'AD']

trueDf = pd.DataFrame(np.nan,index=range(nrUnqSubj), columns=('RID', 'CognitiveAssessmentDate',
  'Diagnosis', 'ADAS13', 'ScanDate', 'Ventricles'))

np.random.seed(1)

for s in range(nrUnqSubj):
  # select random months from each subject as ADNI3 follow-ups
  randDateScanCurr = randomDate(startDate, endDate, random.random())
  currSubjMask = df['RID'] == unqSubj[s]
  currSubjData = df[currSubjMask]
  currSubjData = currSubjData.reset_index(drop=True)

  # set the cognitive assessment date to be slightly different,
  # as this has always been the case in ADNI
  randDateCog = randomDate((randDateScanCurr-tdeltaCog).strftime(stdDateFormat),
    (randDateScanCurr+tdeltaCog).strftime(stdDateFormat), random.random())

  # find the closest estimates, add noise and set them as the true D4
  timeDiffsScanMri = [randDateScanCurr - d for d in currSubjData['Forecast Date']]
  indexMin = np.argsort(np.abs(timeDiffsScanMri))[0]

  randDiag = diagStr[np.random.randint(0,3)]

  # std=50%_CI/(2*0.67) .. taken from en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule#Table_of_numerical_values
  adasStd = (currSubjData['ADAS13 50% CI upper'].iloc[indexMin] -
             currSubjData['ADAS13 50% CI lower'].iloc[indexMin])/(2*0.67)
  # print('adasStd', adasStd)
  randADAS = round(np.random.normal(loc=currSubjData['ADAS13'].iloc[indexMin], scale=adasStd))
  ventStd = (currSubjData['Ventricles_ICV 50% CI upper'].iloc[indexMin] -
             currSubjData['Ventricles_ICV 50% CI lower'].iloc[indexMin])/(2*0.67)
  # print('ventStd', ventStd)
  randVent = np.random.normal(loc=currSubjData['Ventricles_ICV'].iloc[indexMin], scale=ventStd)

  # set these randomly generated values to be the true measurements (i.e. D4 dataset)
  trueDf.iloc[s] = [unqSubj[s], randDateCog.strftime(stdDateFormat), randDiag, randADAS, randDateScanCurr.strftime(stdDateFormat), randVent]

trueDf.RID = trueDf.RID.astype(int)
trueDf.ADAS13 = trueDf.ADAS13.astype(int)
trueDf.Ventricles = trueDf.Ventricles.astype(float)

trueDf.to_csv('D4_dummy.csv',index=False)

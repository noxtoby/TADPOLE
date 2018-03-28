import pandas as pd
import os
import sys
import numpy as np

d12PD = pd.read_csv('TADPOLE_D1_D2.csv')

d1PD = d12PD[d12PD.D1 == 1]
d2PD = d12PD[d12PD.D2 == 1]
d3PD = pd.read_csv('TADPOLE_D3.csv')

pdAll = [d1PD, d2PD, d3PD]

dbLabels = ['D1', 'D2', 'D3']

for db in range(2):

  curPd = pdAll[db]

  # subjects
  nrSubjUnq = np.unique(curPd.RID).shape[0]

  nrVisits = curPd.shape[0]

  # average visits per subj
  avgNrVisits2 = float(nrVisits) / nrSubjUnq

  curPdByRID = curPd.groupby(['RID'], as_index=False)
  avgNrVisits = np.mean(curPdByRID.count().COLPROT)
  stdNrVisits = np.std(curPdByRID.count().COLPROT)

  # diagnosis at BL
  nrCTL = np.sum(curPd.DX_bl == 'CN')
  nrMCI = np.sum(np.in1d(curPd.DX_bl, ['EMCI', 'LMCI']))
  nrAD = np.sum(curPd.DX_bl == 'AD')
  sumDX = nrCTL + nrMCI + nrAD
  nrCTL /= sumDX
  nrMCI /= sumDX
  nrAD /= sumDX

  # % who have cognitive
  nrMMSE = float(np.sum(~np.isnan(curPd.MMSE))) / nrVisits

  # % who have MRI
  nrMRI = float(np.sum(curPd.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16 != ' ' ))/nrVisits

  # % who have FDG
  nrFDG = float(np.sum(~np.in1d(curPd.TMPINFR04_BAIPETNMRC_09_12_16,  [' ', '-4'])))/nrVisits

  # % who have AV45
  nrAV45 = float(np.sum(~np.in1d(curPd.CTX_LH_MEDIALORBITOFRONTAL_SIZE_UCBERKELEYAV45_10_17_16,  [' ', '-4'])))/nrVisits

  # % who have AV1451
  nrAV1451 = float(np.sum(~np.in1d(curPd.CTX_LH_SUPERIORPARIETAL_UCBERKELEYAV1451_10_17_16, [' ', '-4'])))/nrVisits

  # % who have DIT
  nrDTI = float(np.sum(curPd.FA_IFO_L_DTIROI_04_30_14 != ' ' ))/nrVisits

  # % who have CSF
  nrCSF = float(np.sum(curPd.ABETA_UPENNBIOMK9_04_19_17 != ' ' ))/nrVisits

  print('-------- database %s -----------' % dbLabels[db])
  print('nrSubjUnq', nrSubjUnq)
  print('nrVisits', nrVisits)
  print('avgVisits', avgNrVisits)
  print('avgNrVisits2',  avgNrVisits2)
  print('stdNrVisits', stdNrVisits)
  print('nrMMSE', nrMMSE)
  print('nrCTL', nrCTL)
  print('nrMCI', nrMCI)
  print('nrAD', nrAD)
  print('nrMRI', nrMRI)
  print('nrFDG', nrFDG)
  print('nrAV45', nrAV45)
  print('nrAV1451', nrAV1451)
  print('nrDTI', nrDTI)
  print('nrCSF',nrCSF)

  # print(type(curPd.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16.loc[12717]))
  # print(curPd.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16.loc[12717] == ' ')
  # print(pd.isnull(curPd.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16.loc[12717]))
  # print(asd)
  #
  # print(asdsa)


######### now for D3 ###########

curPd = d3PD

# subjects
nrSubjUnq = np.unique(curPd.RID).shape[0]

nrVisits = curPd.shape[0]

# average visits per subj
avgNrVisits = float(nrVisits) / nrSubjUnq

curPd[['DX']] = curPd[['DX']].astype(str)

mapping = {
  # 'NL' : 'NL', 'MCI' : 'MCI', 'Dementia' : 'Dementia',
  'NL to MCI': 'MCI', 'MCI to NL':'NL',
  'MCI to Dementia':'Dementia', 'Dementia to MCI':'MCI', 'NL to Dementia':'Dementia', 'Dementia to NL':'NL'}
# curPd.replace({'DX': mapping})


# print(np.unique(curPd.DX))
# print(ads)

# diagnosis at BL
nrCTL = np.sum(np.in1d(curPd.DX, ['NL']))
nrMCI = np.sum(np.in1d(curPd.DX, ['MCI']))
nrAD = np.sum(np.in1d(curPd.DX, ['Dementia']))
sumDX = nrCTL + nrMCI + nrAD
nrCTL /= sumDX
nrMCI /= sumDX
nrAD /= sumDX

# % who have cognitive
nrMMSE = float(np.sum(~np.isnan(curPd.MMSE))) / nrVisits

# % who have MRI

nrMRI = float(np.sum(np.isnan(curPd.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16))) / nrVisits

print('-------- database D3 -----------')
print('nrSubjUnq', nrSubjUnq)
print('nrVisits', nrVisits)
print('avgVisits', avgNrVisits)
print('nrMMSE', nrMMSE)
print('nrCTL', nrCTL)
print('nrMCI', nrMCI)
print('nrAD', nrAD)
print('nrMRI', nrMRI)


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

# print('nrSubjADNI1', nrSubjADNI1)
# print('nrSubjADNI1andADNIGO2', nrSubjADNI1andADNIGO2)
# print('dropoutRate', dropoutRate)
# print()
# print(d12PD[d12PD.D2 == 1])
# print('nrSubjD2Old', np.unique(d12PD[d12PD.D2 == 1].RID))

nrSubjD2 = np.sum(d12ByRID.D2.apply(
  lambda x: np.in1d(1, x)).astype('bool'))
nrSubjD4 = nrSubjD2 * dropoutRate

d12oneYear = d12PD[('2012-06-01' < d12PD.EXAMDATE) & ( d12PD.EXAMDATE < '2013-06-01')] # filter entries in first year of ADNI2
d12oneYearByRID = d12oneYear.groupby(['RID'], as_index=False)
# print('d12oneYearByRID.count()', d12oneYearByRID.count().COLPROT)
# avgNrVisits = np.mean(d12oneYearByRID.count().COLPROT)


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
avgNrVisits = nrCtlD3norm * 2 + nrMCID3norm * 1 + nrADD3norm * 1
# print(np.concatenate((np.ones(int(nrCtlD3)) * 2, np.ones(int(nrMCID3)) * 1, np.ones(int(nrADD3)) * 1),axis=0))
stdNrVisits = np.std(np.concatenate((np.ones(int(nrCtlD3)) * 2, np.ones(int(nrMCID3)) * 1, np.ones(int(nrADD3)) * 1),axis=0))

# % who have cognitive
nrMMSE = float(np.sum(~np.isnan(d12oneYear.MMSE))) / nrVisits
# % who have MRI
nrMRI = float(np.sum(d12oneYear.ST60TS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16 != ' ')) / nrVisits
# % who have FDG
nrFDG = float(np.sum(~np.in1d(d12oneYear.TMPINFR04_BAIPETNMRC_09_12_16, [' ', '-4']))) / nrVisits
# % who have AV45
nrAV45 = float(np.sum(~np.in1d(d12oneYear.CTX_LH_MEDIALORBITOFRONTAL_SIZE_UCBERKELEYAV45_10_17_16, [' ', '-4']))) / nrVisits
# % who have AV1451
nrAV1451 = float(np.sum(~np.in1d(d12oneYear.CTX_LH_SUPERIORPARIETAL_UCBERKELEYAV1451_10_17_16, [' ', '-4']))) / nrVisits
# % who have DIT
nrDTI = float(np.sum(d12oneYear.FA_IFO_L_DTIROI_04_30_14 != ' ')) / nrVisits
# % who have CSF
nrCSF = float(np.sum(d12oneYear.ABETA_UPENNBIOMK9_04_19_17 != ' ')) / nrVisits

print('nrSubjD2', nrSubjD2)
print('dropoutRate', dropoutRate)
print('nrSubjD4', nrSubjD4)
print('avgVisits', avgNrVisits)
print('stdNrVisits', stdNrVisits)
print('nrMMSE', nrMMSE)
print('nrCTL', nrCtlD3)
print('nrMCI', nrMCID3)
print('nrAD', nrADD3)
print('nrMRI', nrMRI)
print('nrFDG', nrFDG)
print('nrAV45', nrAV45)
print('nrAV1451', nrAV1451)
print('nrDTI', nrDTI)
print('nrCSF', nrCSF)
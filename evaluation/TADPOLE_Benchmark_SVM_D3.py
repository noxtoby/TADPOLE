#Benchmark_SVM.py
#
#Submission using linear support vector machine on ADAS13 and VentVol (+ APOE as covariate).
#
#Adapted by Razvan Marinescu, based on script by Vikram Venkatraghavan, Ester Bron.
#============
#Date:
#12 Nov 2017



print('Load data and select features')

# Read in TADPOLE File
import os

str_exp = ''

tadpoleD1D2File = '../TADPOLE_D1_D2.csv'
tadpoleD3File = '../TADPOLE_D3.csv'

import pandas as pd
import numpy as np
from datetime import datetime
D1Only=pd.read_csv(tadpoleD1D2File)

# drop all D2 subjects
D1Only = D1Only[D1Only['D2'] == 0].copy()

# Create Diagnosis variable based on DXCHANGE
idx_mci=D1Only['DXCHANGE']==4
D1Only.loc[idx_mci,'DXCHANGE']=2
idx_ad = D1Only['DXCHANGE']==5
D1Only.loc[idx_ad,'DXCHANGE']=3
idx_ad = D1Only['DXCHANGE']==6
D1Only.loc[idx_ad,'DXCHANGE']=3
idx_cn = D1Only['DXCHANGE']==7
D1Only.loc[idx_cn,'DXCHANGE']=1
idx_mci=D1Only['DXCHANGE']==8
D1Only.loc[idx_mci,'DXCHANGE']=2
idx_cn = D1Only['DXCHANGE']==9
D1Only.loc[idx_cn,'DXCHANGE']=1
D1Only=D1Only.rename(columns={'DXCHANGE':'Diagnosis'})
h = list(D1Only)

D3=pd.read_csv(tadpoleD3File)

# Create Diagnosis variable based on DX
idx=D3['DX']=='NL'
D3.loc[idx,'Diagnosis']=1
idx = D3['DX']=='MCI'
D3.loc[idx,'Diagnosis']=2
idx = D3['DX']=='Dementia'
D3.loc[idx,'Diagnosis']=3
idx = D3['DX']=='NL to MCI'
D3.loc[idx,'Diagnosis']=2
idx=D3['DX']=='NL to Dementia'
D3.loc[idx,'Diagnosis']=3
idx = D3['DX']=='MCI to Dementia'
D3.loc[idx,'Diagnosis']=3
idx = D3['DX']=='MCI to NL'
D3.loc[idx,'Diagnosis']=1
idx = D3['DX']=='Dementia to NL'
D3.loc[idx,'Diagnosis']=1
idx = D3['DX']=='Dementia to MCI'
D3.loc[idx,'Diagnosis']=2

# Select features
D1Only=D1Only[['RID', 'Diagnosis', 'AGE', 'ADAS13', 'Ventricles', 'ICV_bl']].copy()

# Force values to numeric
h = list(D1Only)
for i in range(5,len(h)):
    print([i])
    if D1Only[h[i]].dtype != 'float64':
        D1Only[h[i]]=pd.to_numeric(D1Only[h[i]], errors='coerce')

# Sort the dataframe based on age for each subject
urid = np.unique(D1Only['RID'].values)
D1Only_sorted=pd.DataFrame(columns=h)
for i in range(len(urid)):
    print([i])
    agei=D1Only.loc[D1Only['RID']==urid[i],'AGE']
    idx_sortedi=np.argsort(agei)
    D1=D1Only.loc[idx_sortedi.index[idx_sortedi]]
    ld = [D1Only_sorted,D1]
    D1Only_sorted = pd.concat(ld)

D1Only_sorted=D1Only_sorted.drop(['AGE'],axis=1)

# Save dataset
D1Only_sorted.to_csv(str_exp+'IntermediateData/BenchmarkSVMFeaturesTADPOLE.csv',index=False)

#Make list of RIDs in D2 to be predicted
# idx_d2=D2==1
D3_RID = D3.RID
SD3=pd.Series(np.unique(D3_RID.values))
SD3.to_csv(str_exp + 'IntermediateData/ToPredict_D3.csv', index=False)

# SVM for TADPOLE
print('Train SVM for Diagnosis and SVR for ADAS and Ventricles')
#Read Data
str_in=os.path.join(str_exp, 'IntermediateData','BenchmarkSVMFeaturesTADPOLE.csv')

D1Only_sorted = pd.read_csv(str_in)

# Correct ventricle volume for ICV
D1Only_sorted['Ventricles_ICV'] = D1Only_sorted['Ventricles'].values / D1Only_sorted['ICV_bl'].values
D3['Ventricles_ICV'] = D3['Ventricles'].values  / D3['ICV'].values

#Get Future Measurements for training prediction
Y_FutureADAS13_temp = D1Only_sorted['ADAS13'].copy()
Y_FutureADAS13_temp[:]=np.nan
Y_FutureVentricles_ICV_temp= D1Only_sorted['Ventricles_ICV'].copy()
Y_FutureVentricles_ICV_temp[:]=np.nan
Y_FutureDiagnosis_temp = D1Only_sorted['Diagnosis'].copy()
Y_FutureDiagnosis_temp[:]=np.nan
RID = D1Only_sorted['RID'].copy()
uRIDs = np.unique(RID)
for i in range(len(uRIDs)):
    idx = RID == uRIDs[i]
    idx_copy = np.copy(idx)
    idx_copy[np.where(idx)[-1][-1]]=False
    Y_FutureADAS13_temp[idx_copy]= D1Only_sorted.loc[idx, 'ADAS13'].values[1:]
    Y_FutureVentricles_ICV_temp[idx_copy]= D1Only_sorted.loc[idx, 'Ventricles_ICV'].values[1:]
    Y_FutureDiagnosis_temp[idx_copy]= D1Only_sorted.loc[idx, 'Diagnosis'].values[1:]
Dtrain = D1Only_sorted.drop(['RID', 'Diagnosis'], axis=1).copy()



#Fill nans in feature matrix as mean of all subjects for that marker. At the end, normalise to (0,1)
Dtrainmat = Dtrain.as_matrix()
D3Mat = D3[['ADAS13', 'Ventricles', 'ICV', 'Ventricles_ICV']].values

print(Dtrain)
print(D3Mat)


h = list(Dtrain)
m = []
s = []
for i in range(Dtrainmat.shape[1]):
    m.append(np.nanmean(Dtrainmat[:,i]))
    s.append(np.nanstd(Dtrainmat[:,i]))
    Dtrainmat[np.isnan(Dtrainmat[:,i]),i]=m[i]
    Dtrainmat[:,i]=(Dtrainmat[:,i] - m[i])/s[i]

    # d3mean = np.nanmean(D3Mat[:, i])
    # d3Std = np.nanstd(D3Mat[:, i])
    d3Mean = m[i]
    d3Std = s[i]

    D3Mat[np.isnan(D3Mat[:,i]),i] = d3Mean
    D3Mat[:, i] = (D3Mat[:, i] - d3Mean) / d3Std


#Remove NaNs in Diagnosis
idx_last_Diagnosis = np.isnan(Y_FutureDiagnosis_temp)
RID_Diagnosis = RID.copy()
Dtrainmat_Diagnosis=Dtrainmat.copy()
Dtrainmat_Diagnosis = Dtrainmat_Diagnosis[np.logical_not(idx_last_Diagnosis),:]
RID_Diagnosis = RID_Diagnosis[np.logical_not(idx_last_Diagnosis)]
Y_FutureDiagnosis = Y_FutureDiagnosis_temp[np.logical_not(idx_last_Diagnosis)].copy()

#Remove NaNs in ADAS
idx_last_ADAS13= np.isnan(Y_FutureADAS13_temp)
RID_ADAS13 = RID.copy()
Dtrainmat_ADAS13=Dtrainmat.copy()
Dtrainmat_ADAS13 = Dtrainmat_ADAS13[np.logical_not(idx_last_ADAS13),:]
RID_ADAS13 = RID_ADAS13[np.logical_not(idx_last_ADAS13)]
Y_FutureADAS13 = Y_FutureADAS13_temp[np.logical_not(idx_last_ADAS13)].copy()

#Normalise ADAS
m_FutureADAS13=np.nanmean(Y_FutureADAS13)
s_FutureADAS13=np.nanstd(Y_FutureADAS13)
Y_FutureADAS13_norm=(Y_FutureADAS13 - m_FutureADAS13)/s_FutureADAS13

#Remove NaNs in Ventricles
idx_last_Ventricles_ICV = np.isnan(Y_FutureVentricles_ICV_temp)
RID_Ventricles_ICV = RID.copy()
Dtrainmat_Ventricles_ICV=Dtrainmat.copy()
Dtrainmat_Ventricles_ICV = Dtrainmat_Ventricles_ICV[np.logical_not(idx_last_Ventricles_ICV ),:]
RID_Ventricles_ICV = RID_Ventricles_ICV [np.logical_not(idx_last_Ventricles_ICV)]
Y_FutureVentricles_ICV = Y_FutureVentricles_ICV_temp[np.logical_not(idx_last_Ventricles_ICV)].copy()

#Normalise Ventricle values
m_FutureVentricles_ICV=np.nanmean(Y_FutureVentricles_ICV)
s_FutureVentricles_ICV=np.nanstd(Y_FutureVentricles_ICV)
Y_FutureVentricles_ICV_norm=(Y_FutureVentricles_ICV - m_FutureVentricles_ICV)/s_FutureVentricles_ICV

#Train SVM for diagnosis
import sklearn.svm as svm
clf = svm.SVC(kernel='linear',probability=True)
clf.fit(Dtrainmat_Diagnosis,Y_FutureDiagnosis)

#Train SVR for ADAS
reg_ADAS13 = svm.SVR(kernel='linear')
reg_ADAS13.fit(Dtrainmat_ADAS13,Y_FutureADAS13_norm)

#Train SVR for Ventricles
reg_Ventricles_ICV = svm.SVR(kernel='linear')
reg_Ventricles_ICV.fit(Dtrainmat_Ventricles_ICV,Y_FutureVentricles_ICV_norm)


print('Create test set and do predictions')
## Create TestSet
SD3 = pd.read_csv(os.path.join(str_exp, 'IntermediateData','ToPredict_D2.csv'),header=None)
SD3=SD3.values

# Test SVM for Diagnosis
p=clf.predict_proba(D3Mat)

# Some defaults for confidence intervals
CI50_Ventricles_ICV=0.05
CI50_ADAS13 = 1

# Test SVR for ADAS
y_ADAS13_norm = reg_ADAS13.predict(D3Mat)
y_ADAS13 = y_ADAS13_norm * s_FutureADAS13 + m_FutureADAS13
y_ADAS13_lower = y_ADAS13 - CI50_ADAS13
y_ADAS13_lower[y_ADAS13_lower<0]=0
y_ADAS13_upper = y_ADAS13 + CI50_ADAS13

# Test SVR for Ventricles
y_Ventricles_ICV_norm = reg_Ventricles_ICV.predict(D3Mat)
y_Ventricles_ICV = y_Ventricles_ICV_norm * s_FutureVentricles_ICV + m_FutureVentricles_ICV
y_Ventricles_ICV_lower = y_Ventricles_ICV - CI50_Ventricles_ICV
y_Ventricles_ICV_lower[y_Ventricles_ICV_lower<0]=0
y_Ventricles_ICV_upper = y_Ventricles_ICV + CI50_Ventricles_ICV

print('D3 min', np.min(D3Mat,axis=0))
print('D3 max', np.max(D3Mat,axis=0))
print('Dtrain min', np.min(Dtrain,axis=0))
print('Dtrain max', np.max(Dtrain,axis=0))


#Write ouput format to files
o=np.column_stack((SD3, SD3, SD3, p, y_ADAS13, y_ADAS13_lower, y_ADAS13_upper, y_Ventricles_ICV, y_Ventricles_ICV_lower, y_Ventricles_ICV_upper))
count=0
years=[str(a) for a in range(2018,2023)]
months=[str(a).zfill(2) for a in range(1,13)]
ym=[y + '-' + mo for y in years for mo in months]
nr_pred=len(ym)
o1 = np.zeros((o.shape[0]*nr_pred, o.shape[1]))
ym1 = [a for b in range(0, len(SD3)) for a in ym]
for i in range(len(o)):
    o1[count:count+nr_pred]=o[i]
    o1[count:count+nr_pred,1]=range(1,nr_pred+1)
    count=count+nr_pred
    

output=pd.DataFrame(o1, columns=['RID','Forecast Month','Forecast Date','CN relative probability','MCI relative probability','AD relative probability','ADAS13','ADAS13 50% CI lower','ADAS13 50% CI upper','Ventricles_ICV','Ventricles_ICV 50% CI lower','Ventricles_ICV 50% CI upper'])
output['Forecast Month'] = output['Forecast Month'].astype(int)
output['Forecast Date'] = ym1

str_out_final = 'TADPOLE_Submission_BenchmarkSVM-ID-5.csv'
output.to_csv(str_out_final,header=True,index=False)

print('Evaluate predictions')
d4Df=pd.read_csv('./TADPOLE_D4_corr.csv')

# convert to datetime format
d4Df['CognitiveAssessmentDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['CognitiveAssessmentDate']]
d4Df['ScanDate'] = [datetime.strptime(x, '%Y-%m-%d') for x in d4Df['ScanDate']]
mapping = {'CN': 0, 'MCI': 1, 'AD': 2}
d4Df.replace({'Diagnosis': mapping}, inplace=True)

import evalOneSubmission as eos
mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA = eos.evalOneSub(d4Df,output)

print('Diagnosis:')
print('mAUC = ' + "%0.3f" % mAUC)
print('BAC = ' + "%0.3f" % bca)
print('ADAS:')
print('MAE = ' + "%0.3f" % adasMAE) 
print('WES = ' + "%0.3f" % adasWES)
print('CPA = ' + "%0.3f" % adasCPA)
print('VENTS:')
print('MAE = ' + "%0.3e" % ventsMAE)
print('WES = ' + "%0.3e" % ventsWES)
print('CPA = ' + "%0.3f" % ventsCPA)

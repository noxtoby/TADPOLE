#Benchmark_SVM_Leaderboard.py
#
#Leaderboard submission using linear support vector machine on ADAS13 and VentVol (+ APOE as covariate).
#
#Adapted by Esther Bron, based on script by Vikram Venkatraghavan
#============
#Date:
#12 Nov 2017

print('Load data and select features')
#str_exp='C:/Users/Esther/Documents/TADPOLE/scripts/tadpole-bigr/'
str_exp = './'

# Read in TADPOLE File
import os
os.chdir(str_exp)

tadpoleD1D2File = str_exp + 'TADPOLE_D1_D2.csv'

import pandas as pd
import numpy as np
Dtadpole=pd.read_csv(tadpoleD1D2File)

# Create Diagnosis variable based on DXCHANGE
idx_mci=Dtadpole['DXCHANGE']==4
Dtadpole.loc[idx_mci,'DXCHANGE']=2
idx_ad = Dtadpole['DXCHANGE']==5
Dtadpole.loc[idx_ad,'DXCHANGE']=3
idx_ad = Dtadpole['DXCHANGE']==6
Dtadpole.loc[idx_ad,'DXCHANGE']=3
idx_cn = Dtadpole['DXCHANGE']==7
Dtadpole.loc[idx_cn,'DXCHANGE']=1
idx_mci=Dtadpole['DXCHANGE']==8
Dtadpole.loc[idx_mci,'DXCHANGE']=2
idx_cn = Dtadpole['DXCHANGE']==9
Dtadpole.loc[idx_cn,'DXCHANGE']=1
Dtadpole=Dtadpole.rename(columns={'DXCHANGE':'Diagnosis'})
h = list(Dtadpole)

# Select Leaderboard subjects
tadpoleLB1LB2File = str_exp + 'TADPOLE_LB1_LB2.csv'
LB_Table = pd.read_csv(tadpoleLB1LB2File)
LB=LB_Table['LB1']+LB_Table['LB2']
idx_lb=LB.values>=1
Dtadpole = Dtadpole[idx_lb]

# Select features
Dtadpole=Dtadpole[['RID','Diagnosis','AGE', 'ADAS13','Ventricles','ICV_bl']].copy()

# Force values to numeric
h = list(Dtadpole)
for i in range(5,len(h)):
    print([i])
    if Dtadpole[h[i]].dtype != 'float64':
        Dtadpole[h[i]]=pd.to_numeric(Dtadpole[h[i]], errors='coerce')

# Sort the dataframe based on age for each subject
urid = np.unique(Dtadpole['RID'].values)
Dtadpole_sorted=pd.DataFrame(columns=h)
for i in range(len(urid)):
    print([i])
    agei=Dtadpole.loc[Dtadpole['RID']==urid[i],'AGE']
    idx_sortedi=np.argsort(agei)
    D1=Dtadpole.loc[idx_sortedi.index[idx_sortedi]]
    ld = [Dtadpole_sorted,D1]
    Dtadpole_sorted = pd.concat(ld)
Dtadpole_sorted=Dtadpole_sorted.drop(['AGE'],axis=1)

# Save dataset
Dtadpole_sorted.to_csv(str_exp+'IntermediateData/LeaderboardBenchmarkSVMFeaturesTADPOLE.csv',index=False)

# Save LB2 RIDs
idx_lb2=LB_Table['LB2']==1
LB2_RID = LB_Table.loc[idx_lb2,'RID']
SLB2=pd.Series(np.unique(LB2_RID.values))
SLB2.to_csv(str_exp+'/IntermediateData/ToPredict.csv',index=False)

# SVM for TADPOLE
print('Train SVM for Diagnosis and SVR for ADAS and Ventricles')
#Read Data
str_in=os.path.join(str_exp, 'IntermediateData','LeaderboardBenchmarkSVMFeaturesTADPOLE.csv')

D = pd.read_csv(str_in)

# Correct ventricle volume for ICV
D['Ventricles_ICV'] = D['Ventricles'].values / D['ICV_bl'].values

#Get Future Measurements for training prediction
Y_FutureADAS13_temp = D['ADAS13'].copy()
Y_FutureADAS13_temp[:]=np.nan
Y_FutureVentricles_ICV_temp= D['Ventricles_ICV'].copy()
Y_FutureVentricles_ICV_temp[:]=np.nan
Y_FutureDiagnosis_temp = D['Diagnosis'].copy()
Y_FutureDiagnosis_temp[:]=np.nan
RID = D['RID'].copy()
uRIDs = np.unique(RID)
for i in range(len(uRIDs)):
    idx = RID == uRIDs[i]
    idx_copy = np.copy(idx)
    idx_copy[np.where(idx)[-1][-1]]=False
    Y_FutureADAS13_temp[idx_copy]= D.loc[idx,'ADAS13'].values[1:]
    Y_FutureVentricles_ICV_temp[idx_copy]= D.loc[idx,'Ventricles_ICV'].values[1:]
    Y_FutureDiagnosis_temp[idx_copy]= D.loc[idx,'Diagnosis'].values[1:]
Dtrain = D.drop(['RID','Diagnosis'],axis=1).copy() 

#Fill nans in feature matrix
Dtrainmat = Dtrain.as_matrix()
h = list(Dtrain)
m = []
s = []
for i in range(Dtrainmat.shape[1]):
    m.append(np.nanmean(Dtrainmat[:,i]))
    s.append(np.nanstd(Dtrainmat[:,i]))
    Dtrainmat[np.isnan(Dtrainmat[:,i]),i]=m[i]
    Dtrainmat[:,i]=(Dtrainmat[:,i] - m[i])/s[i]

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
S = pd.read_csv(os.path.join(str_exp, 'IntermediateData','ToPredict.csv'),header=None)
S=S.values

Dtestmat=np.zeros((len(S),Dtrainmat.shape[1]))
for i in range(len(S)):
    idx_S=RID.values==S[i]
    Dtestmat[i,:]=Dtrainmat[np.where(idx_S)[0][-1],:]

# Test SVM for Diagnosis
p=clf.predict_proba(Dtestmat)

# Some defaults for confidence intervals
CI50_Ventricles_ICV=0.05;
CI50_ADAS13 = 1;

# Test SVR for ADAS
y_ADAS13_norm = reg_ADAS13.predict(Dtestmat)
y_ADAS13 = y_ADAS13_norm * s_FutureADAS13 + m_FutureADAS13
y_ADAS13_lower = y_ADAS13 - CI50_ADAS13
y_ADAS13_lower[y_ADAS13_lower<0]=0
y_ADAS13_upper = y_ADAS13 + CI50_ADAS13

# Test SVR for Ventricles
y_Ventricles_ICV_norm = reg_Ventricles_ICV.predict(Dtestmat)
y_Ventricles_ICV = y_Ventricles_ICV_norm * s_FutureVentricles_ICV + m_FutureVentricles_ICV
y_Ventricles_ICV_lower = y_Ventricles_ICV - CI50_Ventricles_ICV
y_Ventricles_ICV_lower[y_Ventricles_ICV_lower<0]=0
y_Ventricles_ICV_upper = y_Ventricles_ICV + CI50_Ventricles_ICV

#Write ouput format to files
o=np.column_stack((S,S,S,p,y_ADAS13,y_ADAS13_lower,y_ADAS13_upper,y_Ventricles_ICV, y_Ventricles_ICV_lower,y_Ventricles_ICV_upper))
count=0
years=[str(a) for a in range(2010,2018)]
months=[str(a).zfill(2) for a in range(1,13)]
ym=[y + '-' + mo for y in years for mo in months ]
ym=ym[4:-8]
nr_pred=len(ym)
o1 = np.zeros((o.shape[0]*nr_pred,o.shape[1]))
ym1 = [a for b in range(0, len(S)) for a in ym ]
for i in range(len(o)):
    o1[count:count+nr_pred]=o[i]
    o1[count:count+nr_pred,1]=range(1,nr_pred+1)
    count=count+nr_pred
    

output=pd.DataFrame(o1, columns=['RID','Forecast Month','Forecast Date','CN relative probability','MCI relative probability','AD relative probability','ADAS13','ADAS13 50% CI lower','ADAS13 50% CI upper','Ventricles_ICV','Ventricles_ICV 50% CI lower','Ventricles_ICV 50% CI upper'])
output['Forecast Month'] = output['Forecast Month'].astype(int)
output['Forecast Date'] = ym1

output.to_csv('TADPOLE_Submission_Leaderboard_BenchmarkSVM.csv',header=True,index=False)


print('Evaluate predictions')
R=pd.read_csv('./TADPOLE_LB4.csv')
import evalOneSubmission as eos
mAUC, bca, adasMAE, ventsMAE, adasWES, ventsWES, adasCPA, ventsCPA = eos.evalOneSub(R,output)

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

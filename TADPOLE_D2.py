#!/usr/bin/env python
# encoding: utf-8
"""
TADPOLE_D2.py

A script to generate the D2 dataset for TADPOLE Challenge:
The Alzheimer's Disease Prediction Of Longitudinal Evolution Challenge
http://tadpole.grand-challenge.org

Called by TADPOLE_D1.py

Created by Neil P. Oxtoby in June 2017.
Copyright (c) 2017 Neil P. Oxtoby.  All rights reserved.
http://neiloxtoby.com
"""

import os
import numpy as np
from datetime import datetime
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
  description=r'''
 A script to generate the D2 dataset for TADPOLE Challenge:
The Alzheimer's Disease Prediction Of Longitudinal Evolution Challenge
http://tadpole.grand-challenge.org

Called by TADPOLE_D1.py

 The script requires the following spreadsheets to be in the current folder:
    REGISTRY.csv
    ROSTER.csv
    ARM.csv
    DXSUM_PDXCONV_ADNIALL.csv
    ADNIMERGE.csv
 ''', formatter_class=RawTextHelpFormatter
)

parser.add_argument('--spreadsheetFolder', dest='spreadsheetFolder', default='.',
                   help='folder of output spreadsheets')

np.random.seed(1)

args = parser.parse_args()

def generateDXCHANGE(ADNI_DXSUM_table):
    "Generate DXCHANGE for ADNI1 within DXSUM table: As defined on page 46 of ADNI_data_training_slides_part2.pdf"
    # Identify ADNI1 Phase and make temporary data frame
    idx_ADNI1 = np.where(ADNI_DXSUM_table.Phase.values=='ADNI1')[0]
    DXSUM_table_ADNI1_temp = ADNI_DXSUM_table.iloc[idx_ADNI1]
    # Initialise DXCHANGE as NaN
    DXCHANGE_ADNI1 = np.array([np.nan for k in range(0,DXSUM_table_ADNI1_temp.shape[0])])
    # Extract relevant DX variables as arrays
    DXCONV = DXSUM_table_ADNI1_temp.DXCONV.values
    DXCURREN = DXSUM_table_ADNI1_temp.DXCURREN.values
    DXCONTYP = DXSUM_table_ADNI1_temp.DXCONTYP.values
    DXREV = DXSUM_table_ADNI1_temp.DXREV.values
    # DXCHANGE definitions
    DXCHANGE_1 = np.logical_and(DXCONV==0,DXCURREN==1)
    DXCHANGE_2 = np.logical_and(DXCONV==0,DXCURREN==2)
    DXCHANGE_3 = np.logical_and(DXCONV==0,DXCURREN==3)
    DXCHANGE_4 = np.logical_and(DXCONV==1,DXCONTYP==1)
    DXCHANGE_5 = np.logical_and(DXCONV==1,DXCONTYP==3)
    DXCHANGE_6 = np.logical_and(DXCONV==1,DXCONTYP==2)
    DXCHANGE_7 = np.logical_and(DXCONV==2,DXREV==1)
    DXCHANGE_8 = np.logical_and(DXCONV==2,DXREV==2)
    DXCHANGE_9 = np.logical_and(DXCONV==2,DXREV==3)
    # Assign appropriate DXCHANGE values
    DXCHANGE_ADNI1[DXCHANGE_1] = np.array([1 for k in range(0,sum(DXCHANGE_1))])
    DXCHANGE_ADNI1[DXCHANGE_2] = np.array([2 for k in range(0,sum(DXCHANGE_2))])
    DXCHANGE_ADNI1[DXCHANGE_3] = np.array([3 for k in range(0,sum(DXCHANGE_3))])
    DXCHANGE_ADNI1[DXCHANGE_4] = np.array([4 for k in range(0,sum(DXCHANGE_4))])
    DXCHANGE_ADNI1[DXCHANGE_5] = np.array([5 for k in range(0,sum(DXCHANGE_5))])
    DXCHANGE_ADNI1[DXCHANGE_6] = np.array([6 for k in range(0,sum(DXCHANGE_6))])
    DXCHANGE_ADNI1[DXCHANGE_7] = np.array([7 for k in range(0,sum(DXCHANGE_7))])
    DXCHANGE_ADNI1[DXCHANGE_8] = np.array([8 for k in range(0,sum(DXCHANGE_8))])
    DXCHANGE_ADNI1[DXCHANGE_9] = np.array([9 for k in range(0,sum(DXCHANGE_9))])
    # Insert values into original DXSUM table
    ADNI_DXSUM_table.loc[idx_ADNI1,'DXCHANGE'] = DXCHANGE_ADNI1
    return ADNI_DXSUM_table

def mergeDX_ARM(DXSUM,ARM):
    "Merge (outer join) DXSUM and ARM using Phase and RID: As defined on page 49 of ADNI_data_training_slides_part2.pdf"
    # Variables to keep
    DXSUM_columns = ['RID', 'Phase', 'VISCODE', 'VISCODE2', 'DXCHANGE']
    ARM_columns = ['RID', 'Phase', 'ARM', 'ENROLLED']
    # Perform the join
    KEYS = ['RID','Phase']
    DXARM = DXSUM[DXSUM_columns].merge(ARM[ARM_columns], how='inner', on=KEYS)
    return DXARM

def assignBaselineDX(DXARM):
    # Page 53 - Use baseline DXCHANGE and ARM to assign baselineDX variable.
    # Temporary data frame: baseline visit, enrolled==[1,2,3]
    idx_bl_enrolled = np.where(np.logical_and(DXARM.VISCODE2.values=='bl',ismember(DXARM.ENROLLED.values,[1,2,3])))[0]
    DXARM_bl = DXARM.iloc[idx_bl_enrolled]
    DXARM_bl = DXARM_bl[['RID','DXCHANGE','ARM']]
    
    # Define baselineDX as per ADNI training slides
    # Initialise as NaN
    baselineDX = np.array([np.nan for k in range(0,DXARM_bl.shape[0])])
    # Extract relevant variables as arrays
    DXCHANGE = DXARM_bl.DXCHANGE.values
    DXCHANGE_179 = ismember(DXCHANGE,[1,7,9])
    DXCHANGE_248 = ismember(DXCHANGE,[2,4,8])
    DXCHANGE_356 = ismember(DXCHANGE,[3,5,6])
    
    DXARM_bl_ARM = DXARM_bl.ARM.values
    DXARM_bl_11 = DXARM_bl_ARM==11
    DXARM_bl_10 = DXARM_bl_ARM==10
    
    baselineDX_1 = np.logical_and(DXCHANGE_179==True,DXARM_bl_11==False)
    baselineDX_2 = np.logical_and(DXCHANGE_179==True,DXARM_bl_11==True)
    baselineDX_3 = np.logical_and(DXCHANGE_248==True,DXARM_bl_10==True)
    baselineDX_4 = np.logical_and(DXCHANGE_248==True,DXARM_bl_10==False)
    baselineDX_5 = DXCHANGE_356==True
    # Assign values by index
    baselineDX[baselineDX_1] = np.array([1 for k in range(0,sum(baselineDX_1))])
    baselineDX[baselineDX_2] = np.array([2 for k in range(0,sum(baselineDX_2))])
    baselineDX[baselineDX_3] = np.array([3 for k in range(0,sum(baselineDX_3))])
    baselineDX[baselineDX_4] = np.array([4 for k in range(0,sum(baselineDX_4))])
    baselineDX[baselineDX_5] = np.array([5 for k in range(0,sum(baselineDX_5))])
    
    # Insert values into table
    DXARM_bl.loc[idx_bl_enrolled,'baselineDX'] = baselineDX
    # Remove unwanted columns
    DXARM_bl = DXARM_bl[['RID','baselineDX']]
    # Add baselineDX to DXARM: join DXARM with DXARM_bl
    # Variables to keep (must include the keys)
    DXARM_columns = ['RID','Phase','VISCODE','VISCODE2','DXCHANGE','ARM','ENROLLED']
    DXARM_bl_columns = ['RID','baselineDX']
    # Perform the join
    KEYS = ['RID']
    DXARM = DXARM[DXARM_columns].merge(DXARM_bl[DXARM_bl_columns], how='left', on=KEYS)
    
    return DXARM


def ismember(A,B):
    "ismember(A,B): Recursive form of np.logical_or to test if A is in B"
    # First comparison
    C = A==B[0]
    if len(B)>1:
        for k in range(1,len(B)):
            C = np.logical_or(C,A==B[k])
    return C

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def activeAtMostRecentVisit(REGISTRY_table):
    """
    Identifies most recent visit per participant, per Phase
    """
    #*** Identify most recent active visit for each participant, in each ADNI Phase
    ActiveVisits_ADNIGO2 = (REGISTRY_table['PTSTATUS'] == 1).values
    VisitConducted_ADNI1 = (REGISTRY_table['RGCONDCT'] == 1).values
    ADNI1  = np.logical_and((REGISTRY_table['Phase'] == 'ADNI1').values, (REGISTRY_table['RGCONDCT'] == 1).values)
    ADNIGO = np.logical_and((REGISTRY_table['Phase'] == 'ADNIGO').values,(REGISTRY_table['RGSTATUS'] == 1).values)
    ADNI2  = np.logical_and((REGISTRY_table['Phase'] == 'ADNI2').values, (REGISTRY_table['RGSTATUS'] == 1).values)
    #* Identify most recent visit using largest Month (from VISCODE2)
    month = REGISTRY_table['VISCODE2'].str.replace('scmri','0').str.replace('m','').str.replace('bl','0').str.replace('sc','0')
    Month = np.array([int(m) if type(m)==str and m!='f' and m!='uns1' else None for m in month])
    MonthIsNone = np.array([m is None for m in Month]) # Used to avoid errors in the for-loop below
    RID = REGISTRY_table.RID.values
    PTSTATUS = REGISTRY_table.PTSTATUS
    RID_u = np.unique(RID)
    MostRecentVisit_ADNI1  = np.zeros((REGISTRY_table.shape[0],1))
    MostRecentVisit_ADNIGO = np.zeros((REGISTRY_table.shape[0],1))
    MostRecentVisit_ADNI2  = np.zeros((REGISTRY_table.shape[0],1))
    InactiveAtAnyVisit     = np.zeros((REGISTRY_table.shape[0],1))
    for ki in range(0,len(RID_u)):
        # All visits for this participant
        rowz = RID==RID_u[ki]
        #* Separate by ADNI Phase
        rowz_ADNI1  = rowz & ADNI1
        rowz_ADNIGO = rowz & ADNIGO
        rowz_ADNI2  = rowz & ADNI2
        visitz_ADNI1     = Month[rowz_ADNI1]
        ptstatusz_ADNI1  = PTSTATUS[rowz_ADNI1]
        if not all(MonthIsNone[rowz_ADNI1]):
            mostRecentVisit_ADNI1 = visitz_ADNI1==max(visitz_ADNI1)
            rowz_ADNI1 = np.where(rowz_ADNI1)[0]
            MostRecentVisit_ADNI1[rowz_ADNI1[mostRecentVisit_ADNI1]] = 1
        visitz_ADNIGO    = Month[rowz_ADNIGO]
        ptstatusz_ADNIGO = PTSTATUS[rowz_ADNIGO]
        if not all(MonthIsNone[rowz_ADNIGO]):
            mostRecentVisit_ADNIGO = visitz_ADNIGO==max(visitz_ADNIGO)
            rowz_ADNIGO = np.where(rowz_ADNIGO)[0]
            MostRecentVisit_ADNIGO[rowz_ADNIGO[mostRecentVisit_ADNIGO]] = 1
        visitz_ADNI2     = Month[rowz_ADNI2]
        ptstatusz_ADNI2  = PTSTATUS[rowz_ADNI2]
        if not all(MonthIsNone[rowz_ADNI2]):
            mostRecentVisit_ADNI2 = visitz_ADNI2==max(visitz_ADNI2)
            rowz_ADNI2 = np.where(rowz_ADNI2)[0]
            MostRecentVisit_ADNI2[rowz_ADNI2[mostRecentVisit_ADNI2]] = 1
    
        ptstatusz  = PTSTATUS[rowz]
        if any(ptstatusz_ADNI1==2) or any(ptstatusz_ADNIGO==2) or any(ptstatusz_ADNI2==2):
            InactiveAtAnyVisit[rowz] = 1

    #* Identify those who are active at their final visit
    ActiveAtMostRecentVisit_ADNI1  = np.logical_and( MostRecentVisit_ADNI1.flatten() ,VisitConducted_ADNI1 ) 
    ActiveAtMostRecentVisit_ADNI1  = np.logical_and(ActiveAtMostRecentVisit_ADNI1, np.logical_not(InactiveAtAnyVisit.flatten()==1) )

    ActiveAtMostRecentVisit_ADNIGO = np.logical_and( MostRecentVisit_ADNIGO.flatten(),ActiveVisits_ADNIGO2 ) , np.logical_not(InactiveAtAnyVisit.flatten()==1) )
    ActiveAtMostRecentVisit_ADNI2  = np.logical_and( np.logical_and( MostRecentVisit_ADNI2.flatten() ,ActiveVisits_ADNIGO2 ) , np.logical_not(InactiveAtAnyVisit.flatten()==1) )

    return ( ActiveAtMostRecentVisit_ADNI1, ActiveAtMostRecentVisit_ADNIGO, ActiveAtMostRecentVisit_ADNI2 ) 

#********************************************************************#
if __name__ == '__main__':
    # runDate = datetime.now().strftime("%Y%m%d")
    dataSaveLocation = os.getcwd()
    dataLocation = os.getcwd()

    #*** Active, passed screening, etc.
    REGISTRY_file = os.path.join(args_spreadsheetFolder,'REGISTRY.csv')
    #*** specifics on EMCI/LMCI/etc
    ARM_file = os.path.join(args_spreadsheetFolder,'ARM.csv')
    DXSUM_file = os.path.join(args_spreadsheetFolder,'DXSUM_PDXCONV_ADNIALL.csv')

    #*** ADNI tables
    REGISTRY_table = pd.read_csv(REGISTRY_file)
    ARM_table = pd.read_csv(ARM_file)
    DXSUM_table = pd.read_csv(DXSUM_file)

    #*** ADNI preliminaries from training slides part 2 PDF document
    DXSUM_table = generateDXCHANGE(DXSUM_table)
    DXARM_table = mergeDX_ARM(DXSUM_table,ARM_table)
    DXARM_table = assignBaselineDX(DXARM_table)
    DXARMREG_table = pd.merge(DXARM_table[['RID','Phase','VISCODE','VISCODE2','DXCHANGE','ARM','ENROLLED','baselineDX']],REGISTRY_table[['RID','Phase','VISCODE','EXAMDATE','PTSTATUS','RGCONDCT','RGSTATUS','VISTYPE']],'left',on=['RID','Phase','VISCODE'])

    #*** Identify most recent visit per participant, per Phase
(ActiveAtMostRecentVisit_ADNI1,ActiveAtMostRecentVisit_ADNIGO,ActiveAtMostRecentVisit_ADNI2) = activeAtMostRecentVisit(REGISTRY_table)
RID_ActiveAtMostRecentVisit_ADNI1  = REGISTRY_table.RID[ActiveAtMostRecentVisit_ADNI1]
RID_ActiveAtMostRecentVisit_ADNIGO = REGISTRY_table.RID[ActiveAtMostRecentVisit_ADNIGO]
RID_ActiveAtMostRecentVisit_ADNI2  = REGISTRY_table.RID[ActiveAtMostRecentVisit_ADNI2]
print('--- Active status at final visit (ADNI1: RGCONDUCT==1; ADNIGO/2: PTSTATUS==1, and never inactive)')
print('--- Found {0} ADNI1 participants\n---       {1} ADNIGO participants\n---       {2} ADNI2 participants\n'.format(len(RID_ActiveAtMostRecentVisit_ADNI1),len(RID_ActiveAtMostRecentVisit_ADNIGO),len(RID_ActiveAtMostRecentVisit_ADNI2)))

    #*** Report numbers by diagnosis
    BaselineDX_ADNI1  = DXARMREG_table[['RID','baselineDX']][np.logical_and(ismember(DXARMREG_table.RID,RID_ActiveAtMostRecentVisit_ADNI1.values) , DXARMREG_table.Phase=='ADNI1')]
    BaselineDX_ADNIGO = DXARMREG_table[['RID','baselineDX']][np.logical_and(ismember(DXARMREG_table.RID,RID_ActiveAtMostRecentVisit_ADNIGO.values), DXARMREG_table.Phase=='ADNIGO')]
    BaselineDX_ADNI2  = DXARMREG_table[['RID','baselineDX']][np.logical_and(ismember(DXARMREG_table.RID,RID_ActiveAtMostRecentVisit_ADNI2.values) , DXARMREG_table.Phase=='ADNI2')]
    # Unique RIDs
    BaselineDX_ADNI1_u  = pd.DataFrame.drop_duplicates(BaselineDX_ADNI1)
    BaselineDX_ADNIGO_u = pd.DataFrame.drop_duplicates(BaselineDX_ADNIGO)
    BaselineDX_ADNI2_u  = pd.DataFrame.drop_duplicates(BaselineDX_ADNI2)
    
    print('\n\n - - - Identifying active participants in each Phase of ADNI - - - \n')
    print(' - - - ADNI1  ({0}) - - - \n'.format(len(BaselineDX_ADNI1_u)))
    print('Baseline DX:\n CN   = {0}\n SMC  = {1}\n EMCI = {2}\n LMCI = {3}\n AD   = {4}\n'.format(sum(BaselineDX_ADNI1_u.baselineDX==1),sum(BaselineDX_ADNI1_u.baselineDX==2),sum(BaselineDX_ADNI1_u.baselineDX==3),sum(BaselineDX_ADNI1_u.baselineDX==4),sum(BaselineDX_ADNI1_u.baselineDX==5)))
    print(' - - - ADNIGO ({0}) - - - \n'.format(len(BaselineDX_ADNIGO_u)))
    print('Baseline DX:\n CN   = {0}\n SMC  = {1}\n EMCI = {2}\n LMCI = {3}\n AD   = {4}\n'.format(sum(BaselineDX_ADNIGO_u.baselineDX==1),sum(BaselineDX_ADNIGO_u.baselineDX==2),sum(BaselineDX_ADNIGO_u.baselineDX==3),sum(BaselineDX_ADNIGO_u.baselineDX==4),sum(BaselineDX_ADNIGO_u.baselineDX==5)))
    print(' - - - ADNI2  ({0}) - - - \n'.format(len(BaselineDX_ADNI2_u)))
    print('Baseline DX:\n CN   = {0}\n SMC  = {1}\n EMCI = {2}\n LMCI = {3}\n AD   = {4}\n'.format(sum(BaselineDX_ADNI2_u.baselineDX==1),sum(BaselineDX_ADNI2_u.baselineDX==2),sum(BaselineDX_ADNI2_u.baselineDX==3),sum(BaselineDX_ADNI2_u.baselineDX==4),sum(BaselineDX_ADNI2_u.baselineDX==5)))
    
    
    
    ### Below needs to be updated for identifying D2 and D3 rows.
    
    ### Here's my MATLAB code:
    # %% Identify D2: all historical ADNIMERGE rows for "prospective rollovers" from ADNI2 into ADNI3
    # D2_RID = BaselineDX_ADNI2_u.RID;
    # table_D2_columns = table_ADNIMERGE(:,{'RID','VISCODE'});
    # table_D2_columns.D2 = 1*ismember(table_ADNIMERGE.RID,D2_RID);
    #
    # %% Identify D3: final visit
    # table_D2_D3_columns = table_D2_columns;
    # table_D2_D3_columns.M = str2double(strrep(strrep(table_D2_D3_columns.VISCODE,'bl','0'),'m',''));
    # % [table_D3_columns_sorted,I] = sortrows(table_D3_columns,{'RID','M'});
    #   %* Identify most recent visit
    #   RID = str2double(table_D2_D3_columns.RID);
    #   RID_u = unique(RID);
    #   MostRecentVisit = zeros(size(table_D2_D3_columns,1),1);
    #   for ki=1:length(RID_u)
    #     rowz = RID==RID_u(ki);
    #     %* Most recent visit
    #     visitz = table_D2_D3_columns.M(rowz);
    #     mostRecentVisit = visitz==max(visitz);
    #     rowz = find(rowz);
    #     MostRecentVisit(rowz(mostRecentVisit)) = 1;
    #   end
    #   table_D2_D3_columns.D3 = 1*(MostRecentVisit==1 & table_D2_D3_columns.D2);
    #   table_D2_D3_columns.M = [];
    #
    #   writetable(table_D2_D3_columns,fullfile(dataSaveLocation,sprintf('TADPOLE_D2_D3_columns_MATLAB_%s.csv',runDate)))
    #
    
    #*** Select ADNI2 participants
    REGISTRY_ADNI2_bool = (REGISTRY_table['Phase']=='ADNI2') #& (REGISTRY_table['RGSTATUS'] == 1)
    REGISTRY_table_ADNI2 = REGISTRY_table.iloc[REGISTRY_ADNI2_bool.values]
    
    #*** Merge tables to find potential ADNI3 rollovers
    #* Join DXARM to REGISTRY
    DXARMREG_table = REGISTRY_table_ADNI2.merge(DXARM_table,'left',['RID','Phase','VISCODE'])
    #* Remove missing values (shouldn't be any)
    # DXCHANGE_notmissing = ~np.isnan(DXARMREG_table['DXCHANGE']).values
    # print(DXARMREG_table[['Phase', 'ID', 'RID', 'VISCODE', 'USERDATE', 'PTSTATUS', 'RGSTATUS',
    #                       'EXAMDATE', 'DXCHANGE']][DXARMREG_table.RID == 107])
    # DXARMREG_table = DXARMREG_table.iloc[DXCHANGE_notmissing]
    #* ADNI2 and active
    uniqueRIDs = DXARMREG_table.RID.unique()
    nrUnqRIDs = uniqueRIDs.shape[0]
    # lastVisitMask = np.zeros(DXARMREG_table.shape[0], bool)
    hasAtLeastOnePtstatusEq1 = np.zeros(DXARMREG_table.shape[0], bool)

    # print(REGISTRY_table_ADNI2[['Phase', 'ID', 'RID', 'VISCODE', 'USERDATE', 'PTSTATUS', 'RGSTATUS',
    #                       'EXAMDATE']][REGISTRY_table_ADNI2.RID == 107])
    # print(DXARMREG_table[['Phase', 'ID', 'RID', 'VISCODE', 'USERDATE', 'PTSTATUS', 'RGSTATUS',
    #                       'EXAMDATE']][DXARMREG_table.RID == 107])
    # print(adsa)

    # notRollovers = np.array([ 107,  160,  479,  922,  1116, 1318, 2026, 2210, 4010, 4022, 4406, 4729, 4827,
    #   4906, 5162, 5235])

    hasNoPtstatusEq2 = np.zeros(DXARMREG_table.shape[0], bool)
    for r in range(nrUnqRIDs):
      currPartMask = DXARMREG_table['RID'] == uniqueRIDs[r]
      hasAtLeastOnePtstatusEq1[currPartMask] = (DXARMREG_table.PTSTATUS[currPartMask] == 1).any()
      hasNoPtstatusEq2[currPartMask] = not ((DXARMREG_table.PTSTATUS[currPartMask] == 2).any())
      # indexInDXARMREG_table = np.where(currPartMask)[0][-1]
      # lastVisitMask[indexInDXARMREG_table] = 1
      # if uniqueRIDs[r] in notRollovers:
      #   print('check not Rollovers', uniqueRIDs[r], (DXARMREG_table.PTSTATUS[currPartMask] == 1).any(), not ((DXARMREG_table.PTSTATUS[currPartMask] == 2).any()))
      #   print('DXARMREG_table.PTSTATUS[currPartMask]', DXARMREG_table.PTSTATUS[currPartMask])

    table_ADNI2_active = DXARMREG_table.iloc[((DXARMREG_table.Phase=='ADNI2') & hasAtLeastOnePtstatusEq1 & hasNoPtstatusEq2).values]
    # print('hasAtLeastOnePtstatusEq1', np.sum(hasAtLeastOnePtstatusEq1))
    # print('hasNoPtstatusEq2', np.sum(hasNoPtstatusEq2))
    # print('table_ADNI2_active', table_ADNI2_active)
    # print(adsa)
    D2_RID = table_ADNI2_active.RID.unique()
    # print('table_ADNI2_active.columns', table_ADNI2_active.columns)

    # print('notRollover flags', np.in1d(notRollovers, D2_RID))
    # print('# in D2', D2_RID.shape[0])

    #*** TADPOLE D2: historical data for D2_RID
    D1_file = '%s/ADNIMERGE.csv' %  args_spreadsheetFolder
    D1_table = pd.read_csv(D1_file)
    D2_indicator = ismember(D1_table.RID.values,D2_RID)
    D2_indicator_numeric = 1*D2_indicator
    D2_ = D1_table[['RID','VISCODE']]
    D2 = D2_.assign(D2=D2_indicator_numeric)

    D2_file = '%s/TADPOLE_D2_column.csv' % args_spreadsheetFolder # D2_file = 'TADPOLE_D2_column_{0}.csv'.format(runDate)
    D2.to_csv(os.path.join(dataSaveLocation,D2_file),index=False)

    performCheck = True
    if performCheck:
      print('----- missing from neil, existing in raz --------')
      neilD2D3matlab = pd.read_csv(os.path.join(os.getcwd(),'TADPOLE_D2_D3_columns_MATLAB_20170707.csv'))
      d2RidUnqNeil = neilD2D3matlab.RID[neilD2D3matlab['D2'] == 1].unique()
      d2RidUnqRaz = D2['RID'][D2['D2'] == 1].unique()


      print('neilUnqRIDs', d2RidUnqNeil)
      print('raz UnqRIDs', d2RidUnqRaz)
      print('raz shape', d2RidUnqRaz.shape[0])
      print('neil shape', d2RidUnqNeil.shape[0])
      for r in range(d2RidUnqRaz.shape[0]):
        pass
        if np.sum(d2RidUnqRaz[r] == neilD2D3matlab['RID']) == 0:
          print('RID not found in neil\n', table_ADNI2_active[['Phase', 'ID', 'RID', 'VISCODE','VISCODE2_x','VISCODE2_y',
                                                     'USERDATE',
                                                     'PTSTATUS', 'RGSTATUS',
                            'EXAMDATE']][table_ADNI2_active.RID == d2RidUnqRaz[r]])

      print('----- missing from raz, existing in neil --------')
      print('raz shape', d2RidUnqRaz.shape[0])
      print('neil shape', d2RidUnqNeil.shape[0])
      for r in range(d2RidUnqNeil.shape[0]):
        pass
        if np.sum(d2RidUnqRaz == d2RidUnqNeil[r]) == 0:
          print('RID not found in raz\n', neilD2D3matlab[
            ['RID', 'VISCODE', 'D2', 'D3']][neilD2D3matlab.RID == d2RidUnqNeil[r]])
          print('', DXARMREG_table[['Phase', 'ID', 'RID', 'VISCODE','VISCODE2_x','VISCODE2_y',
                                                     'USERDATE',
                                                     'PTSTATUS', 'RGSTATUS',
                            'EXAMDATE']][DXARMREG_table.RID == d2RidUnqNeil[r]])


      # print('np.in1d(d2RidUnqRaz, d2RidUnqNeil)', np.in1d(d2RidUnqRaz, d2RidUnqNeil))
      ridRazNotInNeil = d2RidUnqRaz[~np.in1d(d2RidUnqRaz, d2RidUnqNeil)]
      neilNotInRaz = d2RidUnqNeil[~np.in1d(d2RidUnqNeil, d2RidUnqRaz)]
      print('raz shape', d2RidUnqRaz.shape[0])
      print('neil shape', d2RidUnqNeil.shape[0])

      print('d2RidUnqRaz.dtype',d2RidUnqRaz.dtype)
      print('d2RidUnqNeil.dtype', d2RidUnqNeil.dtype)
      print('ridRazNotInNeil', ridRazNotInNeil)
      print('neilNotInRaz', neilNotInRaz)

    

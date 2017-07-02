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

#********************************************************************#
if __name__ == '__main__':
    # runDate = datetime.now().strftime("%Y%m%d")
    dataSaveLocation = os.getcwd()
    dataLocation = os.getcwd()
    
    #*** Active, passed screening, etc.
    REGISTRY_file = '%s/REGISTRY.csv' % args.spreadsheetFolder
    ROSTER_file   = '%s/ROSTER.csv' % args.spreadsheetFolder
    #*** specifics on EMCI/LMCI/etc
    ARM_file = '%s/ARM.csv' % args.spreadsheetFolder
    DXSUM_file = '%s/DXSUM_PDXCONV_ADNIALL.csv' % args.spreadsheetFolder
    
    #*** ADNI tables
    REGISTRY_table = pd.read_csv(REGISTRY_file)
    ARM_table = pd.read_csv(ARM_file)
    DXSUM_table = pd.read_csv(DXSUM_file)
    
    #*** ADNI preliminaries from training slides part 2 PDF document
    DXSUM_table = generateDXCHANGE(DXSUM_table)
    DXARM_table = mergeDX_ARM(DXSUM_table,ARM_table)
    DXARM_table = assignBaselineDX(DXARM_table)
    
    #*** Select ADNI2 participants
    REGISTRY_ADNI2_bool = (REGISTRY_table['Phase']=='ADNI2') & (REGISTRY_table['RGSTATUS']==1)
    REGISTRY_table_ADNI2 = REGISTRY_table.iloc[REGISTRY_ADNI2_bool.values]
    
    #*** Merge tables to find potential ADNI3 rollovers
    #* Join DXARM to REGISTRY
    DXARMREG_table = DXARM_table.merge(REGISTRY_table_ADNI2,'left',['RID','Phase','VISCODE'])
    #* Remove missing values (shouldn't be any)
    DXCHANGE_notmissing = ~np.isnan(DXARMREG_table['DXCHANGE']).values
    DXARMREG_table = DXARMREG_table.iloc[DXCHANGE_notmissing]
    #* ADNI2 and active
    table_ADNI2_active = DXARMREG_table.iloc[((DXARMREG_table.Phase=='ADNI2') & (DXARMREG_table.PTSTATUS==1)).values]
    D2_RID = table_ADNI2_active.RID.unique()
    
    #*** TADPOLE D2: historical data for D2_RID
    D1_file = '%s/ADNIMERGE.csv' %  args.spreadsheetFolder
    D1_table = pd.read_csv(D1_file)
    D2_indicator = ismember(D1_table.RID.values,D2_RID)
    D2_indicator_numeric = 1*D2_indicator
    D2_ = D1_table[['RID','VISCODE']]
    D2 = D2_.assign(D2=D2_indicator_numeric)
    D2_file = '%s/TADPOLE_D2_column.csv' % args.spreadsheetFolder # D2_file = 'TADPOLE_D2_column_{0}.csv'.format(runDate)
    D2.to_csv(os.path.join(dataSaveLocation,D2_file),index=False)
    

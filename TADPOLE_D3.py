#!/usr/bin/env python
# encoding: utf-8
"""
TADPOLE_D3.py

A script to generate the D3 dataset for TADPOLE Challenge:
The Alzheimer's Disease Prediction Of Longitudinal Evolution Challenge
http://tadpole.grand-challenge.org

Called by TADPOLE_D1.py
Pre-requisite: must have already run TADPOLE_D2.py

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
  description=r'''A script to generate the D3 dataset for TADPOLE Challenge:
The Alzheimer's Disease Prediction Of Longitudinal Evolution Challenge
http://tadpole.grand-challenge.org

Called by TADPOLE_D1.py
Pre-requisite: must have already run TADPOLE_D2.py
 ''', formatter_class=RawTextHelpFormatter
)

parser.add_argument('--spreadsheetFolder', dest='spreadsheetFolder', default='.',
                   help='folder of output spreadsheets')

np.random.seed(1)

args = parser.parse_args()

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#********************************************************************#
if __name__ == '__main__':
    dataSaveLocation = os.getcwd()
    
    #*** TADPOLE D2: historical data for D2_RID
    D1_file = 'TADPOLE_D1_D2.csv' 
    D1_table = pd.read_csv(D1_file)
    D2_indicator = D1_table.D2
    D2_indicator_numeric = 1*D2_indicator
    D2_ = D1_table[['RID','VISCODE']]
    D2 = D2_.assign(D2=D2_indicator_numeric)
    
    #*** TADPOLE D3: D2 final visit per individual; selected columns relevant to clinical trials selection
    
    #* Identify UCSFFSL columns (STxxx) for both versions of FreeSurfer: 4.3 and 5.1
    UCSFFSX4p3_csv = '%s/UCSFFSX_11_02_15.csv' % args.spreadsheetFolder
    UCSFFSX5p1_csv = '%s/UCSFFSX51_08_01_16.csv' % args.spreadsheetFolder
    UCSFFSX1  = pd.read_csv(UCSFFSX4p3_csv) # ADNI1: 1.5T
    UCSFFSX51 = pd.read_csv(UCSFFSX5p1_csv) # ADNIGO/2: 3T
    UCSFFSX4p3_columns = list(UCSFFSX1.columns.values)
    UCSFFSX5p1_columns = list(UCSFFSX51.columns.values)
    # Remove key columns as we're interested in the other columns
    UCSFFSX4p3_columns.remove('RID')
    UCSFFSX4p3_columns.remove('VISCODE')
    UCSFFSX4p3_columns.remove('update_stamp')
    UCSFFSX5p1_columns.remove('COLPROT')
    UCSFFSX5p1_columns.remove('RID')
    UCSFFSX5p1_columns.remove('VISCODE')
    UCSFFSX5p1_columns.remove('VISCODE2')
    UCSFFSX5p1_columns.remove('update_stamp')
    # Add 5.1 columns missing from 4.3
    UCSFFSX_columns = UCSFFSX4p3_columns + [c for c in UCSFFSX5p1_columns if c not in UCSFFSX4p3_columns]
    # Append table names to column names
    UCSFFSX_columns = [c + '_UCSFFSX_11_02_15_UCSFFSX51_08_01_16' for c in UCSFFSX_columns]
    # Selected columns
    D3_columns = ['RID','VISCODE','EXAMDATE','DX','AGE','PTGENDER','PTEDUCAT','PTETHCAT','PTRACCAT','PTMARRY','COLPROT','ADAS13','MMSE','Ventricles','Hippocampus','WholeBrain','Entorhinal','Fusiform','MidTemp','ICV']
    D3_columns = D3_columns + UCSFFSX_columns
    
    #* Extract selected individuals and columns from D1 & D2, then select most recent visit
    D3_table = D1_table.loc[D2_indicator==1]
    ################################
    columnsThatAreNotInD1D2 = ['IMAGETYPE_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','LHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','RHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST28SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST87SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST131HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST132HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST133HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST134HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST135HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST136HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST137HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST138HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST139HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST140HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST141HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST142HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST143HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST144HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST145HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST146HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST147SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST148SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST149SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST150SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST151SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST152SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST153SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST154SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST155SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16']
    D3_columns_subset = D3_columns
    for k in range(0,len(columnsThatAreNotInD1D2)):
        s = columnsThatAreNotInD1D2[k]
        D3_columns_subset.remove(s)
    ################################
    M = D3_table.M.values
    D3_table = D3_table[D3_columns_subset]
    
    #* Identify most recent visit
    RID = D3_table.RID.values
    mostRecentVisit = np.zeros((len(RID),1))
    RID_u = np.unique(RID)
    for k in range(0,len(RID_u)):
        rowz = np.where(RID_u[k]==RID)[0]
        mrv = rowz[M[rowz]==max(M[rowz])][-1]
        mostRecentVisit[mrv] = True
    
    D3_table = D3_table.iloc[mostRecentVisit.flatten()==True]
    D3_table = D3_table.fillna('-4') # ADNI's default missing value code
    D3_file = 'TADPOLE_D3.csv' # D3_file = 'TADPOLE_D3_{0}.csv'.format(runDate)
    D3_table.to_csv(os.path.join(dataSaveLocation,D3_file),index=False,na_rep='-4')

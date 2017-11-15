#!/usr/bin/env python
# encoding: utf-8
"""
TADPOLE_VisitAge.py

Load datasets for TADPOLE Challenge 2017, and adjust AGE to VISITAGE.
  AGE = age at baseline
  VISITAGE = current age at visit

Loads TADPOLE_D1_D2.csv => Saves TADPOLE_D1_D2_VisitAge.csv
Loads TADPOLE_D3.csv    => Saves TADPOLE_D3_VisitAge.csv

Instructions (equivalently for the corresponding MATLAB script):
  1. Save this file to the same folder as 
     TADPOLE_D1_D2.csv and TADPOLE_D3.csv
  2. Run this script using python

Output:
  TADPOLE_D1_D2_VisitAge.csv
  TADPOLE_D3_VisitAge.csv

Alternatively, copy the relevant lines of code into your own script.

Tested in python version 2.7.13 and 3.5.2
on a MacBook Pro running OS X Yosemite 10.10.5

Neil Oxtoby, UCL, November 2017
http://neiloxtoby.com
"""

import os
import pandas as pd
import numpy as np

dataSaveLocation = os.getcwd()

#****** D1/D2 ******#
dataFile = os.path.join(dataSaveLocation,'TADPOLE_D1_D2.csv')
#* Read in the table
dataTable_D1D2 = pd.read_csv(dataFile)

#****** D3 ******#
dataFile = os.path.join(dataSaveLocation,'TADPOLE_D3.csv')
#* Read in the table
dataTable_D3 = pd.read_csv(dataFile)

#* Optionally sort the rows by RID and EXAMDATE
#dataTable_D1D2.sort_values(['RID','EXAMDATE'])
#dataTable_D3.sort_values(['RID','EXAMDATE'])

#****** Adjust AGE at baseline to VISITAGE ******#
dataTable_D1D2['VISITAGE'] = dataTable_D1D2['AGE'] + dataTable_D1D2['Years_bl']
#* Left Outer Join D3 to D1D2 on {RID,VISCODE}, keeping only VISITAGE from D1D2
dataTable_D3 = dataTable_D3.merge(dataTable_D1D2[['RID','VISCODE','VISITAGE']],how='outer',on=['RID','VISCODE'])

#* Reorder columns to put VISITAGE next to AGE
a = np.where(dataTable_D1D2.columns == 'AGE')[0][0]
cols = [col for col in dataTable_D1D2.columns[0:(a+1)]] + ['VISITAGE']  + [col for col in dataTable_D1D2.columns[(a+1):] if col != 'VISITAGE']
dataTable_D1D2 = dataTable_D1D2[cols]

a = np.where(dataTable_D3.columns == 'AGE')[0][0]
cols = [col for col in dataTable_D3.columns[0:(a+1)]] + ['VISITAGE']  + [col for col in dataTable_D3.columns[(a+1):] if col != 'VISITAGE']
dataTable_D3 = dataTable_D3[cols]

#****** Write data to CSV ******#
dataTable_D1D2.to_csv(os.path.join(dataSaveLocation,'TADPOLE_D1_D2_VisitAge.csv'),index=False,na_rep='')
dataTable_D3.to_csv(os.path.join(dataSaveLocation,'TADPOLE_D3_VisitAge.csv'),index=False,na_rep='')

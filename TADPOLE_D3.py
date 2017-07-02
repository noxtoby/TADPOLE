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
    
    #* Identify UCSFFSL columns: STxxx
    UCSFFSL4p3_csv = '%s/UCSFFSL_02_01_16.csv' % args.spreadsheetFolder
    UCSFFSL5p1_csv = '%s/UCSFFSL51ALL_08_01_16.csv' % args.spreadsheetFolder
    UCSFFSL1  = pd.read_csv(UCSFFSL4p3_csv) # ADNI1: 1.5T
    UCSFFSL51 = pd.read_csv(UCSFFSL5p1_csv) # ADNIGO/2: 3T
    UCSFFSL4p3_columns = UCSFFSL1.columns
    FSL4p3_columns = []
    UCSFFSL5p1_columns = UCSFFSL51.columns
    FSL5p1_columns = []
    
    ############ Need to do this also for UCSFFSX tables (cross-sectional FreeSurfer)
    for k in range(0,len(UCSFFSL4p3_columns)):
        col = UCSFFSL4p3_columns[k]
        if col[0:2]=='ST':
            if representsInt(col[2]):
                FSL4p3_columns.append(col)
    for k in range(0,len(UCSFFSL5p1_columns)):
        col = UCSFFSL5p1_columns[k]
        if col[0:2]=='ST':
            if representsInt(col[2]):
                FSL5p1_columns.append(col)

    # #### Raz: added Freesurfer Cross-sectional, 01 July 2017 ##########
    # UCSFFSX4p3_csv = '%s/UCSFFSX_11_02_15.csv' % args.spreadsheetFolder
    # UCSFFSX5p1_csv = '%s/UCSFFSX51_08_01_16.csv' % args.spreadsheetFolder
    # UCSFFSX1 = pd.read_csv(UCSFFSX4p3_csv)  # ADNI1: 1.5T
    # UCSFFSX51 = pd.read_csv(UCSFFSX5p1_csv)  # ADNIGO/2: 3T
    # UCSFFSX4p3_columns = UCSFFSX1.columns
    # FSX4p3_columns = []
    # UCSFFSX5p1_columns = UCSFFSX51.columns
    # FSX5p1_columns = []
    #
    # for k in range(0, len(UCSFFSX4p3_columns)):
    #   col = UCSFFSX4p3_columns[k]
    #   if col[0:2] == 'ST':
    #     if representsInt(col[2]):
    #       FSX4p3_columns.append(col)
    # for k in range(0, len(UCSFFSX5p1_columns)):
    #   col = UCSFFSX5p1_columns[k]
    #   if col[0:2] == 'ST':
    #     if representsInt(col[2]):
    #       FSX5p1_columns.append(col)

    UCSFFSL_columns = FSL4p3_columns + FSL5p1_columns
    UCSFFSL_columns_u = set(UCSFFSL_columns)
    
    UCSFFSL_columns_manual = ['LONISID','LONIUID','IMAGEUID','OVERALLQC','TEMPQC','FRONTQC','PARQC','INSULAQC','OCCQC','BGQC','CWMQC','VENTQC','ST100SV','ST101SV','ST102CV','ST102SA','ST102TA','ST102TS','ST103CV','ST103SA','ST103TA','ST103TS','ST104CV','ST104SA','ST104TA','ST104TS','ST105CV','ST105SA','ST105TA','ST105TS','ST106CV','ST106SA','ST106TA','ST106TS','ST107CV','ST107SA','ST107TA','ST107TS','ST108CV','ST108SA','ST108TA','ST108TS','ST109CV','ST109SA','ST109TA','ST109TS','ST10CV','ST110CV','ST110SA','ST110TA','ST110TS','ST111CV','ST111SA','ST111TA','ST111TS','ST112SV','ST113CV','ST113SA','ST113TA','ST113TS','ST114CV','ST114SA','ST114TA','ST114TS','ST115CV','ST115SA','ST115TA','ST115TS','ST116CV','ST116SA','ST116TA','ST116TS','ST117CV','ST117SA','ST117TA','ST117TS','ST118CV','ST118SA','ST118TA','ST118TS','ST119CV','ST119SA','ST119TA','ST119TS','ST11SV','ST120SV','ST121CV','ST121SA','ST121TA','ST121TS','ST122SV','ST123CV','ST123SA','ST123TA','ST123TS','ST124SV','ST125SV','ST126SV','ST127SV','ST128SV','ST129CV','ST129SA','ST129TA','ST129TS','ST12SV','ST130CV','ST130SA','ST130TA','ST130TS','ST13CV','ST13SA','ST13TA','ST13TS','ST14CV','ST14SA','ST14TA','ST14TS','ST15CV','ST15SA','ST15TA','ST15TS','ST16SV','ST17SV','ST18SV','ST19SV','ST1SV','ST20SV','ST21SV','ST22CV','ST22SA','ST22TA','ST22TS','ST23CV','ST23SA','ST23TA','ST23TS','ST24CV','ST24SA','ST24TA','ST24TS','ST25CV','ST25SA','ST25TA','ST25TS','ST26CV','ST26SA','ST26TA','ST26TS','ST27SA','ST28CV','ST29SV','ST2SV','ST30SV','ST31CV','ST31SA','ST31TA','ST31TS','ST32CV','ST32SA','ST32TA','ST32TS','ST33SV','ST34CV','ST34SA','ST34TA','ST34TS','ST35CV','ST35SA','ST35TA','ST35TS','ST36CV','ST36SA','ST36TA','ST36TS','ST37SV','ST38CV','ST38SA','ST38TA','ST38TS','ST39CV','ST39SA','ST39TA','ST39TS','ST3SV','ST40CV','ST40SA','ST40TA','ST40TS','ST41SV','ST42SV','ST43CV','ST43SA','ST43TA','ST43TS','ST44CV','ST44SA','ST44TA','ST44TS','ST45CV','ST45SA','ST45TA','ST45TS','ST46CV','ST46SA','ST46TA','ST46TS','ST47CV','ST47SA','ST47TA','ST47TS','ST48CV','ST48SA','ST48TA','ST48TS','ST49CV','ST49SA','ST49TA','ST49TS','ST4SV','ST50CV','ST50SA','ST50TA','ST50TS','ST51CV','ST51SA','ST51TA','ST51TS','ST52CV','ST52SA','ST52TA','ST52TS','ST53SV','ST54CV','ST54SA','ST54TA','ST54TS','ST55CV','ST55SA','ST55TA','ST55TS','ST56CV','ST56SA','ST56TA','ST56TS','ST57CV','ST57SA','ST57TA','ST57TS','ST58CV','ST58SA','ST58TA','ST58TS','ST59CV','ST59SA','ST59TA','ST59TS','ST5SV','ST60CV','ST60SA','ST60TA','ST60TS','ST61SV','ST62CV','ST62SA','ST62TA','ST62TS','ST63SV','ST64CV','ST64SA','ST64TA','ST64TS','ST65SV','ST66SV','ST67SV','ST68SV','ST69SV','ST6SV','ST70SV','ST71SV','ST72CV','ST72SA','ST72TA','ST72TS','ST73CV','ST73SA','ST73TA','ST73TS','ST74CV','ST74SA','ST74TA','ST74TS','ST75SV','ST76SV','ST77SV','ST78SV','ST79SV','ST7SV','ST80SV','ST81CV','ST81SA','ST81TA','ST81TS','ST82CV','ST82SA','ST82TA','ST82TS','ST83CV','ST83SA','ST83TA','ST83TS','ST84CV','ST84SA','ST84TA','ST84TS','ST85CV','ST85SA','ST85TA','ST85TS','ST86SA','ST87CV','ST88SV','ST89SV','ST8SV','ST90CV','ST90SA','ST90TA','ST90TS','ST91CV','ST91SA','ST91TA','ST91TS','ST92SV','ST93CV','ST93SA','ST93TA','ST93TS','ST94CV','ST94SA','ST94TA','ST94TS','ST95CV','ST95SA','ST95TA','ST95TS','ST96SV','ST97CV','ST97SA','ST97TA','ST97TS','ST98CV','ST98SA','ST98TA','ST98TS','ST99CV','ST99SA','ST99TA','ST99TS','ST9SV']

    UCSFFSX_columns_manual = ['EXAMDATE','VERSION','LONISID','FLDSTRENG','LONIUID','IMAGEUID','RUNDATE','STATUS','OVERALLQC','TEMPQC','FRONTQC','PARQC','INSULAQC','OCCQC','BGQC','CWMQC','VENTQC','ST100SV','ST101SV','ST102CV','ST102SA','ST102TA','ST102TS','ST103CV','ST103SA','ST103TA','ST103TS','ST104CV','ST104SA','ST104TA','ST104TS','ST105CV','ST105SA','ST105TA','ST105TS','ST106CV','ST106SA','ST106TA','ST106TS','ST107CV','ST107SA','ST107TA','ST107TS','ST108CV','ST108SA','ST108TA','ST108TS','ST109CV','ST109SA','ST109TA','ST109TS','ST10CV','ST110CV','ST110SA','ST110TA','ST110TS','ST111CV','ST111SA','ST111TA','ST111TS','ST112SV','ST113CV','ST113SA','ST113TA','ST113TS','ST114CV','ST114SA','ST114TA','ST114TS','ST115CV','ST115SA','ST115TA','ST115TS','ST116CV','ST116SA','ST116TA','ST116TS','ST117CV','ST117SA','ST117TA','ST117TS','ST118CV','ST118SA','ST118TA','ST118TS','ST119CV','ST119SA','ST119TA','ST119TS','ST11SV','ST120SV','ST121CV','ST121SA','ST121TA','ST121TS','ST122SV','ST123CV','ST123SA','ST123TA','ST123TS','ST124SV','ST125SV','ST126SV','ST127SV','ST128SV','ST129CV','ST129SA','ST129TA','ST129TS','ST12SV','ST130CV','ST130SA','ST130TA','ST130TS','ST13CV','ST13SA','ST13TA','ST13TS','ST14CV','ST14SA','ST14TA','ST14TS','ST15CV','ST15SA','ST15TA','ST15TS','ST16SV','ST17SV','ST18SV','ST19SV','ST1SV','ST20SV','ST21SV','ST22CV','ST22SA','ST22TA','ST22TS','ST23CV','ST23SA','ST23TA','ST23TS','ST24CV','ST24SA','ST24TA','ST24TS','ST25CV','ST25SA','ST25TA','ST25TS','ST26CV','ST26SA','ST26TA','ST26TS','ST27SA','ST28CV','ST29SV','ST2SV','ST30SV','ST31CV','ST31SA','ST31TA','ST31TS','ST32CV','ST32SA','ST32TA','ST32TS','ST33SV','ST34CV','ST34SA','ST34TA','ST34TS','ST35CV','ST35SA','ST35TA','ST35TS','ST36CV','ST36SA','ST36TA','ST36TS','ST37SV','ST38CV','ST38SA','ST38TA','ST38TS','ST39CV','ST39SA','ST39TA','ST39TS','ST3SV','ST40CV','ST40SA','ST40TA','ST40TS','ST41SV','ST42SV','ST43CV','ST43SA','ST43TA','ST43TS','ST44CV','ST44SA','ST44TA','ST44TS','ST45CV','ST45SA','ST45TA','ST45TS','ST46CV','ST46SA','ST46TA','ST46TS','ST47CV','ST47SA','ST47TA','ST47TS','ST48CV','ST48SA','ST48TA','ST48TS','ST49CV','ST49SA','ST49TA','ST49TS','ST4SV','ST50CV','ST50SA','ST50TA','ST50TS','ST51CV','ST51SA','ST51TA','ST51TS','ST52CV','ST52SA','ST52TA','ST52TS','ST53SV','ST54CV','ST54SA','ST54TA','ST54TS','ST55CV','ST55SA','ST55TA','ST55TS','ST56CV','ST56SA','ST56TA','ST56TS','ST57CV','ST57SA','ST57TA','ST57TS','ST58CV','ST58SA','ST58TA','ST58TS','ST59CV','ST59SA','ST59TA','ST59TS','ST5SV','ST60CV','ST60SA','ST60TA','ST60TS','ST61SV','ST62CV','ST62SA','ST62TA','ST62TS','ST63SV','ST64CV','ST64SA','ST64TA','ST64TS','ST65SV','ST66SV','ST67SV','ST68SV','ST69SV','ST6SV','ST70SV','ST71SV','ST72CV','ST72SA','ST72TA','ST72TS','ST73CV','ST73SA','ST73TA','ST73TS','ST74CV','ST74SA','ST74TA','ST74TS','ST75SV','ST76SV','ST77SV','ST78SV','ST79SV','ST7SV','ST80SV','ST81CV','ST81SA','ST81TA','ST81TS','ST82CV','ST82SA','ST82TA','ST82TS','ST83CV','ST83SA','ST83TA','ST83TS','ST84CV','ST84SA','ST84TA','ST84TS','ST85CV','ST85SA','ST85TA','ST85TS','ST86SA','ST87CV','ST88SV','ST89SV','ST8SV','ST90CV','ST90SA','ST90TA','ST90TS','ST91CV','ST91SA','ST91TA','ST91TS','ST92SV','ST93CV','ST93SA','ST93TA','ST93TS','ST94CV','ST94SA','ST94TA','ST94TS','ST95CV','ST95SA','ST95TA','ST95TS','ST96SV','ST97CV','ST97SA','ST97TA','ST97TS','ST98CV','ST98SA','ST98TA','ST98TS','ST99CV','ST99SA','ST99TA',
                              'ST99TS','ST9SV']

    UCSFFSL_columns = [c + '_UCSFFSL_02_01_16_UCSFFSL51ALL_08_01_16' for c in UCSFFSL_columns_manual]
    UCSFFSX_columns = [c + '_UCSFFSX_11_02_15_UCSFFSX51_08_01_16' for c in UCSFFSX_columns_manual]

    D3_columns = ['RID','VISCODE','EXAMDATE','DX','AGE','PTGENDER','PTEDUCAT','PTETHCAT','PTRACCAT','PTMARRY','COLPROT','ADAS13','MMSE','Ventricles','Hippocampus','WholeBrain','Entorhinal','Fusiform','MidTemp','ICV']
    D3_columns = D3_columns + UCSFFSL_columns + UCSFFSX_columns
    
    #* Extract selected individuals and columns from D1 & D2, then select most recent visit
    D3_table = D1_table.loc[D2_indicator==1]
    M = D3_table.M.values
    D3_table = D3_table[D3_columns]
    
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

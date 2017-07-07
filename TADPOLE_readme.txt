=== TADPOLE Challenge data ===
See https://tadpole.grand-challenge.org/ for more details regarding the challenge.

For enquiries on this dataset or the challenge please email tadpole@cs.ucl.ac.uk


=== Steps required to generate the TADPOLE data sets ===
= Requires MATLAB and Python =
1. Place all required ADNI spreadsheets (CSV files, see below) together into one folder
2. Place all of the TADPOLE scripts (described below) into the same folder
3. MATLAB: run TADPOLE_D2.m
4. python: run TADPOLE_D1_D2.py
5. MATLAB: run TADPOLE_D3.m


=== Scripts used to generate TADPOLE datasets ===
TADPOLE_D2.m
- MATLAB script to generate prediction data set D2, and identifies the final visit used to generate prediction data set D3.
TADPOLE_D1_D2.py
- python script used to construct TADPOLE_D1_D2.csv and TADPOLE_D1_D2_Dict.csv
TADPOLE_D3.m
- MATLAB script to generate prediction data set D3, using the outputs from TADPOLE_D2.m and TADPOLE_D1_D2.py.


=== Spreadsheets ===
TADPOLE_D1_D2.csv
- Historical ADNI data from selected tables. Columns D1 and D2 (=1) indicate the corresponding TADPOLE datasets.

TADPOLE_D1_D2_Dict.csv
- Combined data dictionaries for the selected tables. 

TADPOLE_D3.csv
- TADPOLE data set D3


=== ADNI spreadsheets required ===
ADNIMERGE.csv
ADNIMERGE_DICT.csv
ARM.csv
REGISTRY.csv
DXSUM_PDXCONV_ADNIALL.csv
UCSFFSL_02_01_16.csv
UCSFFSL_DICT_11_01_13.csv
UCSFFSL51ALL_08_01_16.csv
UCSFFSL51ALL_DICT_05_04_16.csv
UCSFFSX_11_02_15.csv
UCSFFSX_DICT_08_01_14.csv
UCSFFSX51_08_01_16.csv
UCSFFSX51_DICT_08_01_14.csv
BAIPETNMRC_09_12_16.csv
BAIPETNMRC_DICT_09_12_16.csv
UCBERKELEYAV45_10_17_16.csv
UCBERKELEYAV45_DICT_06_15_16.csv
UCBERKELEYAV1451_10_17_16.csv
UCBERKELEYAV1451_DICT_10_17_16.csv
DTIROI_04_30_14.csv
DTIROI_DICT_04_30_14.csv
UPENNBIOMK9_04_19_17.csv
UPENNBIOMK9_DICT_04_19_17.csv

--------- Data description ----------

------------- Data sets -------------

We have prepared three “standard” data sets for training and forecasting. The archive containing all the data and associated files is HERE.  In the archive, the file D1-D2.csv contains both data sets D1 and D2 - membership is indicated by columns in the spreadsheet; D3.csv contains D3.  Here is a description of the data sets themselves:

--------------- D1. TADPOLE Standard training set. -----------------

The Standard training set (D1) was created from the ADNIMERGE spreadsheet, to which we added additional MRI, PET (FDG, AV45 and AV1451), DTI and CSF biomarkers.
 
The MRI biomarkers we added consist of FreeSurfer longitudinally processed ROIs from UCSFFSL tables. The exact spreadsheets used were UCSFFSL_02_01_16.csv and UCSFFSL51ALL_08_01_16.csv. Duplicate rows were removed by retaining the row with the most recent RUNDATE and IMAGEUID.
 
We also included the following types of PET ROI-based biomarkers: FDG, AV45 and AV1451. The spreadsheets used were: BAIPETNMRC_09_12_16.csv, UCBERKELEYAV45_10_17_16.csv and UCBERKELEYAV1451_10_17_16.csv.
 
TADPOLE flowchart
The DTI biomarkers added represent ROI summary measures (e.g. mean diffusivity MD, axial diffusivity AD) taken from the spreadsheet DTIROI_04_30_14.csv.
 
We also included three CSF biomarkers: Amyloid-beta, Tau and P-Tau. These values were taken from the Elecsys analysis, which can be found in the UPENNBIOMK9_04_19_17.csv spreadsheet.
 
We matched the subjects between ADNIMERGE and these spreadsheets using the subject ID and visit code. Duplicate rows were removed, with the most recent preferred (). For each modality we also included the ID of the image that was used to derive these summary measures.

-------------- D2. TADPOLE Standard prediction set. ----------------

All currently available longitudinal data for prospective ADNI3 participants (rollovers from ADNI2). That is, active participants with ADNI2 visits. These participants were identified using the script TADPOLE_D2.m.

----------- D3. TADPOLE Cross-sectional prediction set. ------------
 
For each participant in D2, the final visit only and a limited number of data columns to mimic screening data for a clinical trial: demographics, cognitive test scores, and structural MRI (derived brain volumes). These participants were identified using the script TADPOLE_D2.m, and the spreadsheet TADPOLE_D3.cv was assembled using the script TADPOLE_D3.m.
 
The forecasts will be evaluated on future data:

------------ D4. TADPOLE Test set. ------------------------
 
The test set will contain ADNI3 data from rollover individuals, acquired after the challenge submission deadline, and used for evaluating the forecasts according to the challenge metrics.



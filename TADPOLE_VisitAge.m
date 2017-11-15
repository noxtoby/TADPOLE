% TADPOLE_VisitAge.m
%
% Load datasets for TADPOLE Challenge 2017, and adjust AGE to VISITAGE.
%   AGE = age at baseline
%   VISITAGE = current age at visit
%
% Loads TADPOLE_D1_D2.csv => Saves TADPOLE_D1_D2_VisitAge.csv
% Loads TADPOLE_D3.csv    => Saves TADPOLE_D3_VisitAge.csv
%
% Instructions (equivalently for the corresponding python script):
%   1. Save this file to the same folder as 
%      TADPOLE_D1_D2.csv and TADPOLE_D3.csv
%   2. Run this script using MATLAB
%
% Output:
%   TADPOLE_D1_D2_VisitAge.csv
%   TADPOLE_D3_VisitAge.csv
%
% Alternatively, copy the relevant lines of code into your own script.
%
% Tested in MATLAB version 8.6.0.267246 (R2015b) 
% on a MacBook Pro running OS X Yosemite 10.10.5
%
% Neil Oxtoby, UCL, November 2017

missingDataNumeric = '';
dataSaveLocation = pwd;

%****** D1/D2 ******%
dataFile = fullfile(dataSaveLocation,'TADPOLE_D1_D2.csv');
%* Read in the table
dataTable_D1D2 = readtable(dataFile,'TreatAsEmpty',missingDataNumeric);
dataTable_D1D2.Properties.Description = 'TADPOLE D1/D2 table created for TADPOLE Challenge 2017.';

%****** D3 ******%
dataFile = fullfile(pwd,'TADPOLE_D3.csv');
%* Read in the table
dataTable_D3 = readtable(dataFile,'TreatAsEmpty',missingDataNumeric);
dataTable_D3.Properties.Description = 'TADPOLE D3 table created for TADPOLE Challenge 2017.';

%****** Adjust AGE at baseline to VISITAGE ******%
dataTable_D1D2.VISITAGE = dataTable_D1D2.AGE + dataTable_D1D2.Years_bl;
%* Left Outer Join D3 to D1D2 on {RID,VISCODE}, keeping only VISITAGE from D1D2
dataTable_D3 = outerjoin(dataTable_D3,dataTable_D1D2,'Keys',{'RID','VISCODE'},'RightVariables','VISITAGE','Type','Left');

%* Optionally sort the rows by RID and EXAMDATE
%dataTable_D1D2 = sortrows(dataTable_D1D2,{'RID','EXAMDATE'});
%dataTable_D3 = sortrows(dataTable_D3,{'RID','EXAMDATE'});

%* Reorder columns to put VISITAGE next to AGE
a = find(strcmpi(dataTable_D1D2.Properties.VariableNames,'AGE'));
cols = [dataTable_D1D2.Properties.VariableNames(1:a), {'VISITAGE'}, dataTable_D1D2.Properties.VariableNames((a+1):(end-1))];
dataTable_D1D2 = dataTable_D1D2(:,cols);

a = find(strcmpi(dataTable_D3.Properties.VariableNames,'AGE'));
cols = [dataTable_D3.Properties.VariableNames(1:a), {'VISITAGE'}, dataTable_D3.Properties.VariableNames((a+1):(end-1))];
dataTable_D3 = dataTable_D3(:,cols);

%****** Write data to CSV ******%
writetable(dataTable_D1D2,fullfile(dataSaveLocation,'TADPOLE_D1_D2_VisitAge.csv'))
writetable(dataTable_D3,fullfile(dataSaveLocation,'TADPOLE_D3_VisitAge.csv'))

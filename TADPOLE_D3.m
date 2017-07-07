% TADPOLE_D3.m Identifying test subjects for TADPOLE challenge 2017
%
% Must run TADPOLE_D2.m first
%
% Neil Oxtoby, UCL, March 2017

%* Preliminaries
writeTables = true;
runDate = datestr(date,'yyyymmdd');
fprintf('If you ran TADPOLE_D2.m on a day other than today, you need to manually change runDate_D2_D3 accordingly.\n')
runDate_D2_D3 = runDate; % '20170707';

%* ADNI spreadsheet locations 
fprintf('Assumes that you''ve put all the ADNI CSVs, along with this script, into the present working directory.\n')
dataLocation = pwd; 
dataSaveLocation = pwd; 

%* Read ADNI tables
TADPOLE_D1_D2_csv = fullfile(dataLocation,'TADPOLE_D1_D2.csv');
table_D1_D2 = readtable(TADPOLE_D1_D2_csv,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
TADPOLE_D2_D3_csv = fullfile(dataLocation,'TADPOLE_D1_D2.csv');
table_D3_column = readtable(fullfile(dataSaveLocation,sprintf('TADPOLE_D2_D3_columns_MATLAB_%s.csv',runDate_D2_D3)));
D3 = table_D3_column.D3;

%* Identify UCSFFSL columns (STxxx) for both versions of FreeSurfer: 4.3 and 5.1
UCSFFSX4p3_csv = fullfile(dataLocation,'UCSFFSX_11_02_15.csv');
UCSFFSX5p1_csv = fullfile(dataLocation,'UCSFFSX51_08_01_16.csv');
UCSFFSX1 = readtable(UCSFFSX4p3_csv); % ADNI1: 1.5T
UCSFFSX51 = readtable(UCSFFSX5p1_csv); % ADNIGO/2: 3T

UCSFFSX4p3_columns = UCSFFSX1.Properties.VariableNames;
UCSFFSX5p1_columns = UCSFFSX51.Properties.VariableNames;
% Remove key columns - we're interested in the other columns
UCSFFSX4p3_columns(ismember(UCSFFSX4p3_columns,{'RID','VISCODE','update_stamp'})) = [];
UCSFFSX5p1_columns(ismember(UCSFFSX5p1_columns,{'COLPROT','RID','VISCODE','VISCODE2','update_stamp'})) = [];

% Add 5.1 columns missing from 4.3
extraColumns = ~ismember(UCSFFSX5p1_columns,UCSFFSX4p3_columns);
UCSFFSX_columns = horzcat(UCSFFSX4p3_columns,UCSFFSX5p1_columns(extraColumns));
% Append table names to column names
UCSFFSX_columns = strcat(UCSFFSX_columns,'_UCSFFSX_11_02_15_UCSFFSX51_08_01_16');

%* Selected columns for D3
D3_columns = {'RID','VISCODE','EXAMDATE','DX','AGE','PTGENDER','PTEDUCAT','PTETHCAT','PTRACCAT','PTMARRY','COLPROT','ADAS13','MMSE','Ventricles','Hippocampus','WholeBrain','Entorhinal','Fusiform','MidTemp','ICV'};
D3_columns = horzcat(D3_columns,UCSFFSX_columns);

%* Extract selected participants and columns from D1 & D2, then select most
%  recent visit (actually done by TADPOLE_D2.m and saved to
%  TADPOLE_D2_D3_columns_MATLAB_{runDate}.csv)
table_D3 = table_D1_D2(D3==1,:);

% ################################
%* FreeSurfer 5.1 has additional columns to 4.3
%  This code removes those columns, as done for TADPOLE_D1_D2
columnsThatAreNotInD1D2 = {'IMAGETYPE_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','LHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','RHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST28SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST87SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST131HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST132HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST133HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST134HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST135HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST136HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST137HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST138HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST139HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST140HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST141HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST142HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST143HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST144HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST145HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST146HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST147SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST148SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST149SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST150SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST151SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST152SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST153SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST154SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST155SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16'};
D3_columns_subset = D3_columns;
for k =1:length(columnsThatAreNotInD1D2)
  s = columnsThatAreNotInD1D2{k};
  s = ismember(D3_columns_subset,s);
  D3_columns_subset(s) = [];
end
% ################################
table_D3 = table_D3(:,D3_columns_subset);

if writeTables
  writetable(table_D3 ,fullfile(dataSaveLocation,'TADPOLE_D3.csv'))
end

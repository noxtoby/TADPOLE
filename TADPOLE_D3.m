% TADPOLE_D3.m Identifying test subjects for TADPOLE challenge 2017
%
% Must run TADPOLE_D2.m first
%
% Neil Oxtoby, UCL, March 2017

writeTables = true;
runDate = datestr(date,'yyyymmdd');

dataLocation = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TADPOLE_D1_D2_D3';
dataSaveLocation = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TADPOLE_D1_D2_D3/20170704_Checks';


%* Read ADNI tables
%ADNIMERGE = fullfile(dataLocation,'ADNIMERGE.csv');
%table_ADNIMERGE = readtable(ADNIMERGE,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
D1_D2 = fullfile(pwd,'TADPOLE_D1_D2.csv');
table_D1_D2 = readtable(D1_D2,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

runDate_D3 = '20170706';
table_D3_columns = readtable(fullfile(dataSaveLocation,sprintf('TADPOLE_D2_D3_columns_MATLAB_%s.csv',runDate_D3)));
D3 = table_D3_columns.D3;

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

%* Extract selected individuals and columns from D1 & D2, then select most
%recent visit (already done by TADPOLE_D2.m)
table_D3 = table_D1_D2(D3==1,:);
%* FreeSurfer 5.1 has additional columns to 4.3
%  This code removes those columns, as Raz did in the original D1_D2.
% => Need to fix TADPOLE_D1.py
columnsThatAreNotInD1D2 = {'IMAGETYPE_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','LHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','RHIPQC_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST28SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST87SA_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST131HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST132HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST133HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST134HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST135HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST136HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST137HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST138HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST139HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST140HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST141HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST142HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST143HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST144HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST145HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST146HS_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST147SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST148SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST149SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST150SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST151SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST152SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST153SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST154SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16','ST155SV_UCSFFSX_11_02_15_UCSFFSX51_08_01_16'};
D3_columns_subset = D3_columns;
for k =1:length(columnsThatAreNotInD1D2)
  s = columnsThatAreNotInD1D2{k};
  s = ismember(D3_columns_subset,s);
  D3_columns_subset(s) = [];
end
% ################################
M = table_D3.M;
table_D3 = table_D3(:,D3_columns_subset);

if writeTables
  writetable(table_D3 ,fullfile(dataSaveLocation,sprintf('TADPOLE_D3_MATLAB_%s.csv',runDate)))
end


%% Template submission spreadsheet
targets = {'DX','ADAS13','Ventricles'}; %{'pCN','pMCI','pAD','ADAS13','ADAS13_CI50pc','Ventricles_ICV','Ventricles_ICV_CI50pc'};
table_template_submission_baseline = table_D3(:,[{'RID','EXAMDATE'},targets,{'ICV'}]);
table_template_submission_baseline.VentVol_ICV = table_template_submission_baseline.Ventricles ./ table_template_submission_baseline.ICV;
table_template_submission_baseline.ICV = []; table_template_submission_baseline.Ventricles = [];
table_template_submission_baseline.ForecastDate = repmat({'2017-11'},size(table_template_submission_baseline,1),1);
table_template_submission_baseline = sortrows(table_template_submission_baseline,{'RID'});

% ForecastDates_year1 = {'2017-12-15','2018-01-15','2018-02-15','2018-03-15','2018-04-15','2018-05-15','2018-06-15','2018-07-15','2018-08-15','2018-09-15','2018-10-15','2018-11-15'};
% ForecastDates_year2 = {'2018-12-15','2019-01-15','2019-02-15','2019-03-15','2019-04-15','2019-05-15','2018-06-15','2019-07-15','2019-08-15','2019-09-15','2019-10-15','2019-11-15'};
% ForecastDates_year3 = {'2019-12-15','2020-01-15','2020-02-15','2020-03-15','2020-04-15','2020-05-15','2018-06-15','2020-07-15','2020-08-15','2020-09-15','2020-10-15','2020-11-15'};
% ForecastDates_year4 = {'2020-12-15','2021-01-15','2021-02-15','2021-03-15','2021-04-15','2021-05-15','2018-06-15','2021-07-15','2021-08-15','2021-09-15','2021-10-15','2021-11-15'};
% ForecastDates_year5 = {'2021-12-15','2022-01-15','2022-02-15','2022-03-15','2022-04-15','2022-05-15','2018-06-15','2022-07-15','2022-08-15','2022-09-15','2022-10-15','2022-11-15'};
ForecastDates_year1 = {'2018-01','2018-02','2018-03','2018-04','2018-05','2018-06','2018-07','2018-08','2018-09','2018-10','2018-11','2018-12'};
ForecastDates_year2 = {'2019-01','2019-02','2019-03','2019-04','2019-05','2019-06','2019-07','2019-08','2019-09','2019-10','2019-11','2019-12'};
ForecastDates_year3 = {'2020-01','2020-02','2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12'};
ForecastDates_year4 = {'2021-01','2021-02','2021-03','2021-04','2021-05','2021-06','2021-07','2021-08','2021-09','2021-10','2021-11','2021-12'};
ForecastDates_year5 = {'2022-01','2022-02','2022-03','2022-04','2022-05','2022-06','2022-07','2022-08','2022-09','2022-10','2022-11','2022-12'};

ForecastMonths_year1 = 1:12;
ForecastMonths_year2 = ForecastMonths_year1 + 12;
ForecastMonths_year3 = ForecastMonths_year2 + 12;
ForecastMonths_year4 = ForecastMonths_year3 + 12;
ForecastMonths_year5 = ForecastMonths_year4 + 12;

ForecastDate = vertcat(ForecastDates_year1(:),ForecastDates_year2(:),ForecastDates_year3(:),ForecastDates_year4(:),ForecastDates_year5(:));
ForecastMonth = vertcat(ForecastMonths_year1(:),ForecastMonths_year2(:),ForecastMonths_year3(:),ForecastMonths_year4(:),ForecastMonths_year5(:));
NForecasts = length(ForecastDate);
RID = table_template_submission_baseline.RID;
NParticipants = length(RID);

RID_long = repmat(RID,1,NForecasts).'; RID_long = RID_long(:);

table_template_submission = table(RID_long,repmat(ForecastMonth,NParticipants,1),repmat(ForecastDate,NParticipants,1));
  table_template_submission.Properties.VariableNames = {'RID','Forecast_Month','Forecast_Date'};
targets = {'CN_relative_likelihood','MCI_relative_likelihood','AD_relative_likelihood','ADAS13','ADAS13_50pc_lower','ADAS13_50pc_upper','Ventricles_ICV','Ventricles_ICV_50pc_lower','Ventricles_ICV_50pc_upper'};
for k=1:length(targets)
  table_template_submission.(targets{k}) = cell(size(table_template_submission,1),1);
end

if writeTables
  writetable(table_template_submission_baseline,fullfile(pwd,sprintf('TADPOLE_ForecastBaseline_%s.csv',runDate)));
  writetable(table_template_submission,fullfile(pwd,sprintf('TADPOLE_ForecastTemplateSubmission_%s.csv',runDate)));
end

function TADPOLE_D1(dataLocation,dataSaveLocation,writeTables)
% TADPOLE_D1.m 
% Cleaned-up version of ADPMC2017_adniMergePlus_Neil.m
%
% Creates D1 standard data set for comparison with Raz's python version 
%
% TADPOLE Challenge 2017 
% (The AD Prediction Of Longitudinal Evolution Challenge)
%
% Neil Oxtoby, UCL, May 2017

%*** To-Do ***%
%* July: Need to add UCSFFSX tables

dataLocation_default = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TADPOLE_D1_D2_D3';
switch nargin
  case 0
    dataLocation = dataLocation_default;
  case 1
    dataSaveLocation = dataLocation;
  case 2
    writeTables = false;
  case 3
  otherwise
    error('TADPOLE_d1.m:nargin','Wrong number of input arguments.')
end

%% ADNI tables of interest
UCSFFSL1_csv   = 'UCSFFSL_02_01_16.csv';
UCSFFSL51_csv  = 'UCSFFSL51ALL_08_01_16.csv';
UCSFFSX1_csv   = 'UCSFFSX_11_02_15.csv';
UCSFFSX51_csv  = 'UCSFFSX51_08_01_16.csv';
BAIPETNMRC_csv = 'BAIPETNMRC_09_12_16.csv';
UCBERKELEYAV45_csv = 'UCBERKELEYAV45_10_17_16.csv';
UCBERKELEYAV1451_csv = 'UCBERKELEYAV1451_10_17_16.csv';
DTIROI_csv = 'DTIROI_04_30_14.csv';
UPENNBIOMK9_csv = 'UPENNBIOMK9_04_19_17.csv';

%% Keys for ADNI tables of interest
keyColumns = {'RID','VISCODE2'}; %'EXAMDATE'
keyColumnsMerge = {'RID','VISCODE'};
%* When dealing with duplicates, take the most recent, as in adnimerger.R
%  (except for QC because I will only keep 'Pass')
sortColumns_UCSFFSL = {'RID','EXAMDATE','RUNDATE','IMAGEUID'};
sortOrder_UCSFFSL = [1,2,-3,-4];
sortColumns = {'RID','EXAMDATE','RUNDATE'};
sortOrder = [1,2,-3];
%* Start with ADNIMERGE
adniMerge = readtable(fullfile(dataLocation,'ADNIMERGE.csv'));
  %* Sort by ID and visit
  %adniMerge.RIDNUM = str2double(adniMerge.RID); adniMerge = sortrows(adniMerge,{'RIDNUM','VISCODE'}); adniMerge.RIDNUM = [];
adniMerge_key = adniMerge(:,keyColumnsMerge);

%% FreeSurfer tables
%* Longitudinal
UCSFFSL1 = readtable(fullfile(dataLocation,UCSFFSL1_csv));   % ADNI1
UCSFFSL51 = readtable(fullfile(dataLocation,UCSFFSL51_csv)); % ADNIGO/2
%* Cross-sectional
UCSFFSX1 = readtable(fullfile(dataLocation,UCSFFSX1_csv));   % ADNI1
UCSFFSX51 = readtable(fullfile(dataLocation,UCSFFSX51_csv)); % ADNIGO/2
  %* Make image IDs numeric
  UCSFFSL1.IMAGEUID = str2double(UCSFFSL1.IMAGEUID); 
  UCSFFSL51.IMAGEUID = str2double(UCSFFSL51.IMAGEUID); 
  UCSFFSX1.IMAGEUID = str2double(UCSFFSX1.IMAGEUID); 
  UCSFFSX51.IMAGEUID = str2double(UCSFFSX51.IMAGEUID); 
  %* Remove failures
  UCSFFSL1 = UCSFFSL1(not(strcmpi(UCSFFSL1.VISCODE,'f')),:);
  UCSFFSL51 = UCSFFSL51(not(strcmpi(UCSFFSL51.VISCODE,'nv')),:);
  UCSFFSX1 = UCSFFSX1(not(strcmpi(UCSFFSX1.VISCODE,'f')),:);
  UCSFFSX51 = UCSFFSX51(not(strcmpi(UCSFFSX51.VISCODE,'nv')),:);
  %* OVERALLQC == 'Pass'
  UCSFFSL1 = UCSFFSL1(strcmpi(UCSFFSL1.OVERALLQC,'Pass'),:);
  UCSFFSL51 = UCSFFSL51(strcmpi(UCSFFSL51.OVERALLQC,'Pass'),:);
  [~,I] = sortrows(UCSFFSL1(:,sortColumns_UCSFFSL),sortOrder_UCSFFSL);  UCSFFSL1 = UCSFFSL1(I,:);
  [~,I] = sortrows(UCSFFSL51(:,sortColumns_UCSFFSL),sortOrder_UCSFFSL); UCSFFSL51 = UCSFFSL51(I,:);
  UCSFFSX1 = UCSFFSX1(strcmpi(UCSFFSX1.OVERALLQC,'Pass'),:);
  UCSFFSX51 = UCSFFSX51(strcmpi(UCSFFSX51.OVERALLQC,'Pass'),:);
  [~,I] = sortrows(UCSFFSX1(:,sortColumns_UCSFFSL),sortOrder_UCSFFSL);  UCSFFSX1 = UCSFFSX1(I,:);
  [~,I] = sortrows(UCSFFSX51(:,sortColumns_UCSFFSL),sortOrder_UCSFFSL); UCSFFSX51 = UCSFFSX51(I,:);
  %* FSL: remove manually-identified rows that should not be there (non-ADNI1)
  UCSFFSL1_nonADNI1Rows = ismember(UCSFFSL1.RID,{'1066','867'}) & ismember(UCSFFSL1.VISCODE2,{'bl','m12'}) & (datetime(UCSFFSL1.EXAMDATE) > datetime(2010,01,01));
  UCSFFSL1 = UCSFFSL1(not(UCSFFSL1_nonADNI1Rows),:);
  %* Remove duplicate rows by RID-VISCODE, selecting by default latest RUNDATE (see sortrows() above)
  [~,I] = unique(UCSFFSL1(:,keyColumns));  UCSFFSL1_ = UCSFFSL1(I,:); 
  [~,I] = unique(UCSFFSL51(:,keyColumns)); UCSFFSL51_ = UCSFFSL51(I,:);
  [~,I] = unique(UCSFFSX1(:,keyColumnsMerge));  UCSFFSX1_ = UCSFFSX1(I,:);
  [~,I] = unique(UCSFFSX51(:,keyColumnsMerge)); UCSFFSX51_ = UCSFFSX51(I,:);
  %* Convert screening to baseline where no bl exists
  %* ADNI1: where both exist, prefer sc and remove bl if date is after 2010
    %*** Longitudinal ***%
    VISCODE_string = 'VISCODE2';
    UCSFFSL1_ = convertScreeningToBaseline_ADNI1(UCSFFSL1_,VISCODE_string);
    UCSFFSL51_ = convertScreeningToBaseline_ADNIGO2(UCSFFSL51_,VISCODE_string);
    %*** Cross-sectional ***%
    VISCODE_string = 'VISCODE';
    UCSFFSX1_ = convertScreeningToBaseline_ADNI1(UCSFFSX1_,VISCODE_string);
    UCSFFSX51_ = convertScreeningToBaseline_ADNIGO2(UCSFFSX51_,VISCODE_string);
    
  %* Combine ADNI1 and ADNIGO/2 using union (same columns) and outerjoin (extras)
    %* Extra columns
    UCSFFSL_ADNI1_sameColumns = UCSFFSL1_.Properties.VariableNames(ismember(UCSFFSL1_.Properties.VariableNames,UCSFFSL51_.Properties.VariableNames));
    UCSFFSL_ADNI2_sameColumns = UCSFFSL51_.Properties.VariableNames(ismember(UCSFFSL51_.Properties.VariableNames,UCSFFSL1_.Properties.VariableNames));
    UCSFFSL_ADNI1_extraColumns = UCSFFSL1_.Properties.VariableNames(~ismember(UCSFFSL1_.Properties.VariableNames,UCSFFSL51_.Properties.VariableNames));
    UCSFFSL_ADNI2_extraColumns = UCSFFSL51_.Properties.VariableNames(~ismember(UCSFFSL51_.Properties.VariableNames,UCSFFSL1_.Properties.VariableNames));
    UCSFFSL = union(UCSFFSL1_(:,UCSFFSL_ADNI1_sameColumns),UCSFFSL51_(:,UCSFFSL_ADNI2_sameColumns));
    UCSFFSL = outerjoin(UCSFFSL,UCSFFSL1_(:,[keyColumns,UCSFFSL_ADNI1_extraColumns]),'Keys',keyColumns,'Type','left','MergeKeys',true);
    UCSFFSL = outerjoin(UCSFFSL,UCSFFSL51_(:,[keyColumns,UCSFFSL_ADNI2_extraColumns]),'Keys',keyColumns,'Type','left','MergeKeys',true);
    
    UCSFFSX_ADNI1_sameColumns = UCSFFSX1_.Properties.VariableNames(ismember(UCSFFSX1_.Properties.VariableNames,UCSFFSX51_.Properties.VariableNames));
    UCSFFSX_ADNI2_sameColumns = UCSFFSX51_.Properties.VariableNames(ismember(UCSFFSX51_.Properties.VariableNames,UCSFFSX1_.Properties.VariableNames));
    UCSFFSX_ADNI1_extraColumns = UCSFFSX1_.Properties.VariableNames(~ismember(UCSFFSX1_.Properties.VariableNames,UCSFFSX51_.Properties.VariableNames));
    UCSFFSX_ADNI2_extraColumns = UCSFFSX51_.Properties.VariableNames(~ismember(UCSFFSX51_.Properties.VariableNames,UCSFFSX1_.Properties.VariableNames));
    UCSFFSX = union(UCSFFSX1_(:,UCSFFSX_ADNI1_sameColumns),UCSFFSX51_(:,UCSFFSX_ADNI2_sameColumns));
    UCSFFSX = outerjoin(UCSFFSX,UCSFFSX1_(:,[keyColumnsMerge,UCSFFSX_ADNI1_extraColumns]),'Keys',keyColumnsMerge,'Type','left','MergeKeys',true);
    UCSFFSX = outerjoin(UCSFFSX,UCSFFSX51_(:,[keyColumnsMerge,UCSFFSX_ADNI2_extraColumns]),'Keys',keyColumnsMerge,'Type','left','MergeKeys',true);

  %* Keys
  UCSFFSL_key = UCSFFSL(:,keyColumns); UCSFFSL_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';
  UCSFFSX_key = UCSFFSX(:,keyColumnsMerge); 
  %UCSFFSL51_key = UCSFFSL51(:,keyColumns); UCSFFSL51_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';

%% PET tables
BAIPETNMRC = readtable(fullfile(dataLocation,BAIPETNMRC_csv)); 
UCBERKELEYAV45 = readtable(fullfile(dataLocation,UCBERKELEYAV45_csv));
UCBERKELEYAV1451 = readtable(fullfile(dataLocation,UCBERKELEYAV1451_csv));
  
BAIPETNMRC_key = BAIPETNMRC(:,keyColumns); BAIPETNMRC_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';
UCBERKELEYAV45_key = UCBERKELEYAV45(:,keyColumns); UCBERKELEYAV45_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';
UCBERKELEYAV1451_key = UCBERKELEYAV1451(:,keyColumns); UCBERKELEYAV1451_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';

  %* PET QC
  PETQC = readtable(fullfile(Imaging,'PETQC.csv'));
  PETQC_Passed = strcmpi(PETQC.PASS,'1');
  PETQC_key = PETQC(PETQC_Passed ,keyColumns); PETQC_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';
  %* BAIPETNMRC: keep PETQC.PASS=='1'
  rowsToKeep = ismember(BAIPETNMRC_key,PETQC_key);
  BAIPETNMRC = BAIPETNMRC(rowsToKeep,:);
  %* BAIPETNMRC: keep only most recent scan per visit
  [~,I] = sortrows(BAIPETNMRC(:,sortColumns),sortOrder); BAIPETNMRC = BAIPETNMRC(I,:);
  [~,I] = unique(BAIPETNMRC(:,keyColumns)); BAIPETNMRC = BAIPETNMRC(I,:);
  BAIPETNMRC_key = BAIPETNMRC(:,keyColumns); BAIPETNMRC_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';

%% DTI table
DTIROI = readtable(fullfile(dataLocation,DTIROI_csv));
DTIROI(strcmpi(DTIROI.RID,'4354'),{'RID','VISCODE2','EXAMDATE','RUNDATE','FA_CST_L'})
  %* Convert screening visits to bl
  DTIROI = convertScreeningToBaseline_DTI(DTIROI);
  %* Debugging
  %DTIROI(strcmpi(DTIROI.RID,'4354'),{'RID','VISCODE2','EXAMDATE','RUNDATE','FA_CST_L'})
  
  %* Sort and then remove duplicates
  [~,I] = sortrows(DTIROI(:,sortColumns),sortOrder); DTIROI = DTIROI(I,:);
  %* Debugging
  %DTIROI(strcmpi(DTIROI.RID,'4354'),{'RID','VISCODE2','EXAMDATE','RUNDATE','FA_CST_L'})
  
  [~,I] = unique(DTIROI(:,keyColumns)); DTIROI = DTIROI(I,:);
  %* Debugging
  %DTIROI(strcmpi(DTIROI.RID,'4354'),{'RID','VISCODE2','EXAMDATE','RUNDATE','FA_CST_L'})
  
DTIROI_key = DTIROI(:,keyColumns); DTIROI_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';

%% CSF Elecsys
UPENNBIOMK9 = readtable(fullfile(dataLocation,UPENNBIOMK9_csv));
  [~,I] = sortrows(UPENNBIOMK9(:,sortColumns),sortOrder); UPENNBIOMK9 = UPENNBIOMK9(I,:); 
  [~,I] = unique(UPENNBIOMK9(:,keyColumns)); UPENNBIOMK9 = UPENNBIOMK9(I,:);
  %* Replace recalculated values
  ABETA = UPENNBIOMK9.ABETA;
  ABETA_replace = strcmpi(ABETA,'>1700');
  ABETA_recalculated = (strrep(strrep(UPENNBIOMK9.COMMENT,'Recalculated ABETA result = ',''),' pg/mL',''));
  ABETA(ABETA_replace) = ABETA_recalculated(ABETA_replace);
  UPENNBIOMK9.ABETA = (ABETA);
UPENNBIOMK9_key = UPENNBIOMK9(:,keyColumns); UPENNBIOMK9_key.Properties.VariableNames{'VISCODE2'} = 'VISCODE';

%% Keep only visits in ADNI MERGE
UCSFFSL = UCSFFSL(ismember(UCSFFSL_key,adniMerge_key),:);
UCSFFSX = UCSFFSX(ismember(UCSFFSX_key,adniMerge_key),:);
BAIPETNMRC = BAIPETNMRC(ismember(BAIPETNMRC_key,adniMerge_key),:);
UCBERKELEYAV45 = UCBERKELEYAV45(ismember(UCBERKELEYAV45_key,adniMerge_key),:);
UCBERKELEYAV1451 = UCBERKELEYAV1451(ismember(UCBERKELEYAV1451_key,adniMerge_key),:);
DTIROI = DTIROI(ismember(DTIROI_key,adniMerge_key),:);
UPENNBIOMK9 = UPENNBIOMK9(ismember(UPENNBIOMK9_key,adniMerge_key),:);

%% *** ADNI MERGE plus
adniMerge.Properties.VariableNames{'VISCODE'} = 'VISCODE_MERGE';
adniMerge.Properties.VariableNames{'RID'} = 'RID_MERGE';
outerJoinBool = true;
if outerJoinBool
  fprintf('size(adniMerge)     = [%i, %i]\n',size(adniMerge))
  adniMergePlus = outerjoin(adniMerge    ,UCSFFSL         ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with UCSFFSL\n',size(adniMergePlus))
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
  adniMergePlus = outerjoin(adniMerge    ,UCSFFSX         ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with UCSFFSL\n',size(adniMergePlus))
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
    
  adniMergePlus = outerjoin(adniMergePlus,BAIPETNMRC      ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with BAIPETNMRC\n',size(adniMergePlus))
    %adniMergePlus.VISCODE2 = []; adniMergePlus.VISCODE = []; adniMergePlus.RID = [];
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
    
  adniMergePlus = outerjoin(adniMergePlus,UCBERKELEYAV45  ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with UCBERKELEYAV45\n',size(adniMergePlus))
    %adniMergePlus.VISCODE2 = []; adniMergePlus.VISCODE = []; adniMergePlus.RID = [];
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
    
  if any(size(UCBERKELEYAV1451)==0)
    fprintf('Not joining UCBERKELEYAV1451 - contains zero data matching to ADNI MERGE.\n')
  else
    adniMergePlus = outerjoin(adniMergePlus,UCBERKELEYAV1451,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
    fprintf('size(adniMergePlus) = [%i, %i] after joining with UCBERKELEYAV1451\n',size(adniMergePlus))
    %adniMergePlus.VISCODE2 = []; adniMergePlus.VISCODE = []; adniMergePlus.RID = [];
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
  end
  
  adniMergePlus = outerjoin(adniMergePlus,DTIROI          ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with DTIROI\n',size(adniMergePlus))
    %adniMergePlus.VISCODE2 = []; adniMergePlus.VISCODE = []; adniMergePlus.RID = [];
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';
    
  adniMergePlus = outerjoin(adniMergePlus,UPENNBIOMK9     ,'Type','left','LeftKeys',{'RID_MERGE','VISCODE_MERGE'},'RightKeys',{'RID','VISCODE2'},'MergeKeys',true);
  fprintf('size(adniMergePlus) = [%i, %i] after joining with UPENNBIOMK9\n',size(adniMergePlus))
    %adniMergePlus.VISCODE2 = []; adniMergePlus.VISCODE = []; adniMergePlus.RID = [];
    adniMergePlus.Properties.VariableNames{'VISCODE_MERGE_VISCODE2'} = 'VISCODE_MERGE';
    adniMergePlus.Properties.VariableNames{'RID_MERGE_RID'} = 'RID_MERGE';

else
%   adniMergePlus = join(adniMerge    ,UCSFFSL1         ,'LeftKeys',{'RID','VISCODE'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,UCSFFSL51       ,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,BAIPETNMRC      ,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,UCBERKELEYAV45  ,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,UCBERKELEYAV1451,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,DTIROI          ,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
%   adniMergePlus = join(adniMergePlus,UPENNBIOMK9     ,'LeftKeys',{'RID_adniMerge','VISCODE_adniMerge'},'RightKeys',{'RID','VISCODE2'});
end

%%
adniMergePlusRaz_file = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TrainingTest/Raz/adniMergePlus/adniMergePlus.csv';
adniMergePlusRaz = readtable(adniMergePlusRaz_file,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);


%%
if writeTables
  writetable(adniMergePlus,fullfile(dataSaveLocation,'adniMergePlusNeil.csv'))
  %writetable(adniMergePlusRaz,[dataSaveLocation,'/adniMergePlusRaz.csv'])
end

%%
Raz = adniMergePlusRaz(:,{'RID','VISCODE'});
Neil = adniMergePlus(:,{'RID_MERGE','VISCODE_MERGE'});
Neil.RID = str2double(Neil.RID_MERGE); Neil.RID_MERGE = [];
Neil.VISCODE = Neil.VISCODE_MERGE; Neil.VISCODE_MERGE = [];

Raz_and_Neil = ismember(Raz,Neil);
Neil_and_Raz = ismember(Neil,Raz);

ampRaz = sortrows(adniMergePlusRaz(Raz_and_Neil,:),{'RID','VISCODE'});
ampNeil = adniMergePlus; ampNeil.RID = str2double(ampNeil.RID_MERGE);
ampNeil = sortrows(ampNeil(Neil_and_Raz,:),{'RID','VISCODE_MERGE'});

%%
markersToCheck_Raz =  {'RID',      'AGE' ...
  ,'ST101SV_UCSFFSL_02_01_16_UCSFFSL51ALL_08_01_16',...
  'TMPINFR03_BAIPETNMRC_09_12_16','ANGULR01_BAIPETNMRC_09_12_16'...
  ,'TEMPORAL_UCBERKELEYAV45_10_17_16','CTX_LH_CUNEUS_UCBERKELEYAV1451_10_17_16'...
  ,'FA_CST_L_DTIROI_04_30_14','ABETA_UPENNBIOMK9_04_19_17'};
markersToCheck_Neil = {'RID_MERGE','AGE','ST101SV','TMPINFR03','ANGULR01','TEMPORAL','CTX_LH_CUNEUS_UCBERKELEYAV1451','FA_CST_L','ABETA'};
for km = 1:length(markersToCheck_Neil)
  n = ampNeil.(markersToCheck_Neil{km});
  r = ampRaz.(markersToCheck_Raz{km});
  if iscell(n)
    t = @str2double;
  else
    t = @(x)x;
  end
  if iscell(r)
    u = @str2double;
  else
    u = @(x)x;
  end

  figure
  plot(u(r),t(n),'r+')
  %legend('Raz','Neil')
  title(strrep(markersToCheck_Neil{km},'_','\_'))
  
  d = abs(u(r)-t(n));
  df = find(~isnan(d));
  dd = d(df);
  if not(all(dd<eps))
    f = find(dd>eps); %find(u(r)~=t(n));
    ff = df(f);
    hold all
    plot(u(r(ff)),t(n(ff)),'bo')
    fprintf('Mismatched subjects (%s):\n',markersToCheck_Neil{km})
    writetable([ampNeil(ff,{'RID_MERGE','VISCODE_MERGE',markersToCheck_Neil{km}}),ampRaz(ff,{'RID','VISCODE',markersToCheck_Raz{km}})],['temp_',markersToCheck_Neil{km},'.csv'])
    tt = [u(r),t(n)];
    diff(tt,1,2);
    [min(diff(tt,1,2)),max(diff(tt,1,2))]
  end
end



end

function UCSFFS_ = convertScreeningToBaseline_ADNI1(UCSFFS,VISCODE_str)
% Removes screening rows, or converts them to baseline, as appropriate
  RID = UCSFFS.RID;
  RIDu = unique(RID);
  sc_rows_to_remove = false(size(RID));
  VISCODEs = UCSFFS.(VISCODE_str);
  for ki=1:length(RIDu)
    RIDk = RIDu{ki};
    rowz = strcmpi(RID,RIDk);
    sc = strcmpi(VISCODEs(rowz),'sc');
    bl = strcmpi(VISCODEs(rowz),'bl');
    rowz = find(rowz);
    if all(bl==0) && sum(sc)==1
      %* Use sc as bl
      VISCODEs{rowz(sc)} = 'bl';
    elseif sum(bl)>=1 && sum(sc)==1
      %* Check date, then keep sc
      nonADNI1_date = datetime(UCSFFS.EXAMDATE(rowz)) > datetime(2010,01,01);
      if nonADNI1_date
        fprintf('RID = %i - post-ADNI1 date found\n',RIDk)
      else
        fprintf('RID = %i - sum(sc) = %i (keeping) , sum(bl) = %i (removing)\n',RIDk,sum(sc),sum(bl))
      end
      sc_rows_to_remove(rowz(bl)) = 1;
    end
  end
  UCSFFS.(VISCODE_str) = VISCODEs;
  UCSFFS_ = UCSFFS(not(sc_rows_to_remove),:);
end

function UCSFFS_ = convertScreeningToBaseline_ADNIGO2(UCSFFS,VISCODE_str)
% Removes screening rows, or converts them to baseline, as appropriate
  RID = UCSFFS.RID;
  RIDu = unique(RID);
  sc_rows_to_remove = false(size(RID));
  VISCODEs = UCSFFS.(VISCODE_str);
  for ki=1:length(RIDu)
    RIDk = RIDu{ki};
    rowz = strcmpi(RID,RIDk);
    sc = strcmpi(VISCODEs(rowz),'scmri');
    bl = strcmpi(VISCODEs(rowz),'bl');
    rowz = find(rowz);
    if all(bl==0) && sum(sc)==1
      VISCODEs{rowz(sc)} = 'bl';
    else
      %fprintf('k = %i - sum(sc) = %i / sum(bl) = %i\n',ki,sum(sc),sum(bl))
      sc_rows_to_remove(rowz(sc)) = 1;
    end
  end
  UCSFFS.(VISCODE_str) = VISCODEs;
  UCSFFS_ = UCSFFS(not(sc_rows_to_remove),:);
end



function DTI_ = convertScreeningToBaseline_DTI(DTI)
  RID = DTI.RID;
  RIDu = unique(RID);
  sc_rows_to_remove = false(size(RID));
  dupes_rowsToRemove = false(size(sc_rows_to_remove));
  for ki=1:length(RIDu)
    RIDk = RIDu{ki};
    rowz = strcmpi(RID,RIDk);
    sc = ismember(DTI.VISCODE2(rowz),{'sc','scmri'});
    bl = strcmpi(DTI.VISCODE2(rowz),'bl');
    rowz = find(rowz);
    if all(bl==0) && sum(sc)==1
      DTI.VISCODE2{rowz(sc)} = 'bl';
    else
      sc_rows_to_remove(rowz(sc)) = 1;
    end
  end
  DTI_ = DTI(not(sc_rows_to_remove),:);
end
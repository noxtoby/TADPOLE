%* Identifying possible test subjects for our
%* ADNI-EuroPOND Alzheimer's Disease Progression Modelling Challenge 2017
%* Neil Oxtoby, UCL, March 2017

%* From the ADNI training slides (part 2, page 61), on how to identify
%  ADNI2 subjects:
%
% 1. New subjects: 925 had screening, 655 had baseline
% From REGISTRY/DXSUM/ARM
% By PHASE='ADNI2', VISCODE = 'v01' or 'v03' (screening or baseline, respectively)
%    RGSTATUS=1 and DXCHANGE is not missing
%
% 2. Continuing subjects
%  258 ADNI1 continuers
%  115 ADNIGO continuers
% As above, but VISCODE=v06 (Initial Visit - continuing Pt)

writeTables = false;
runDate = datestr(date,'yyyymmdd');

dataLocation = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/ADNITables';
dataSaveLocation = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TrainingTest';

Imaging = [dataLocation,'/Imaging'];
MAYOADIRL_MRI_MCH = [Imaging, '/MAYOADIRL_MRI_MCH_09_15_16.csv']; % one row per MR finding

Enrollment = [dataLocation,'/Enrollment'];
REGISTRY = [Enrollment,'/REGISTRY.csv'];
ROSTER = [Enrollment,'/ROSTER.csv'];
ADNI2_VISITID = [Enrollment,'/ADNI2_VISITID.csv'];
ARM = [Enrollment,'/ARM.csv']; % can get specifics on EMCI/LMCI/etc

Diagnosis = [dataLocation,'/Diagnosis'];
DXSUM = [Diagnosis,'/DXSUM_PDXCONV_ADNIALL.csv']; % can get specifics on EMCI/LMCI/etc

table_REGISTRY = readtable(REGISTRY);
% table_ROSTER = readtable(ROSTER);
table_ARM = readtable(ARM);
table_DXSUM = readtable(DXSUM);
  table_DXSUM.DXCHANGE = str2double(table_DXSUM.DXCHANGE);

%* Select ADNI2 / ADNI3 participants
ADNI2 = strcmpi(table_REGISTRY.Phase,'ADNI2') & strcmpi(table_REGISTRY.RGSTATUS,'1');
ADNI2_new_sc = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v01'});
ADNI2_new_bl = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v03'});
ADNI2_continuing = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v06'});

ADNI3 = strcmpi(table_REGISTRY.Phase,'ADNI3') & strcmpi(table_REGISTRY.RGSTATUS,'1');

table_REGISTRY_ADNI23 = table_REGISTRY(ADNI2 | ADNI3,:);

table_REGISTRY_ADNI2 =  table_REGISTRY(ADNI2,:);

%* Leaderboard data
ADNI1 = strcmpi(table_REGISTRY.Phase,'ADNI1');
table_REGISTRY_ADNI1 =  table_REGISTRY(ADNI1,:);

%% 
%table_DXSUM = table_DXSUM(strcmpi(table_DXSUM.Phase,'ADNI2'),:);
%table_ARM = table_ARM(strcmpi(table_ARM.Phase,'ADNI2'),:);

%* Page 46-48 - Generate DXCHANGE for ADNI1
table_DXSUM_ADNI1_temp = table_DXSUM(strcmpi(table_DXSUM.Phase,'ADNI1'),:);
  table_DXSUM_ADNI1_temp.DXCONV = str2double(table_DXSUM_ADNI1_temp.DXCONV);
  table_DXSUM_ADNI1_temp.DXCURREN = str2double(table_DXSUM_ADNI1_temp.DXCURREN);
  table_DXSUM_ADNI1_temp.DXCONTYP = str2double(table_DXSUM_ADNI1_temp.DXCONTYP);
  table_DXSUM_ADNI1_temp.DXREV = str2double(table_DXSUM_ADNI1_temp.DXREV);
DXCHANGE_ADNI1 = nan(size(table_DXSUM_ADNI1_temp.DXCONV));
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==0 & table_DXSUM_ADNI1_temp.DXCURREN==1) = 1;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==0 & table_DXSUM_ADNI1_temp.DXCURREN==2) = 2;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==0 & table_DXSUM_ADNI1_temp.DXCURREN==3) = 3;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==1 & table_DXSUM_ADNI1_temp.DXCONTYP==1) = 4;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==1 & table_DXSUM_ADNI1_temp.DXCONTYP==3) = 5;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==1 & table_DXSUM_ADNI1_temp.DXCONTYP==2) = 6;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==2 & table_DXSUM_ADNI1_temp.DXREV==1) = 7;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==2 & table_DXSUM_ADNI1_temp.DXREV==2) = 8;
DXCHANGE_ADNI1(table_DXSUM_ADNI1_temp.DXCONV==2 & table_DXSUM_ADNI1_temp.DXREV==3) = 9;
table_DXSUM.DXCHANGE(strcmpi(table_DXSUM.Phase,'ADNI1')) = DXCHANGE_ADNI1;

%* Joins
%* Page 49 - merge DXSUM and ARM using Phase and RID
% Keep key variables:
% DXSUM: RID, PHASE, VISCODE, VISCODE2, DXCHANGE
%   ARM: RID, PHASE, ARM, ENROLLED
table_DXARM = join(table_DXSUM,table_ARM,'Keys',{'RID','Phase'},...
  'LeftVariables',{'RID','Phase','VISCODE','VISCODE2','DXCHANGE'},...
  'RightVariables',{'ARM','ENROLLED'});
%* Page 53 - Use baseline DXCHANGE and ARM to assign baselineDX variable.
baselineVISCODE2 = 'bl';
table_DXARM_bl = table_DXARM(strcmpi(table_DXARM.VISCODE2,baselineVISCODE2) & ismember(table_DXARM.ENROLLED,{'1','2','3'}),{'RID','DXCHANGE','ARM'});
      baselineDX = nan(size(table_DXARM_bl,1),1);
      baselineNormal = ismember(table_DXARM_bl.DXCHANGE,[1,7,9]) & not(strcmpi(table_DXARM_bl.ARM,'11'));
      baselineSMC = ismember(table_DXARM_bl.DXCHANGE,[1,7,9]) & strcmpi(table_DXARM_bl.ARM,'11');
      baselineEMCI = ismember(table_DXARM_bl.DXCHANGE,[2,4,8]) & strcmpi(table_DXARM_bl.ARM,'10');
      baselineLMCI = ismember(table_DXARM_bl.DXCHANGE,[2,4,8]) & not(strcmpi(table_DXARM_bl.ARM,'10'));
      baselineAD = ismember(table_DXARM_bl.DXCHANGE,[3,5,6]);
      %sum(baselineNormal) + sum(baselineSMC) + sum(baselineEMCI) + sum(baselineLMCI) + sum(baselineAD)
      baselineDX(baselineNormal) = 1;
      baselineDX(baselineSMC) = 2;
      baselineDX(baselineEMCI) = 3;
      baselineDX(baselineLMCI) = 4;
      baselineDX(baselineAD) = 5;
        baselineDX_text = cell(size(baselineDX));
        [baselineDX_text{baselineNormal}] = deal('CN');
        [baselineDX_text{baselineSMC}] = deal('SMC');
        [baselineDX_text{baselineEMCI}] = deal('EMCI');
        [baselineDX_text{baselineLMCI}] = deal('LMCI');
        [baselineDX_text{baselineAD}] = deal('AD');
      
      table_DXARM_bl.baselineDX = baselineDX_text;
      table_DXARM_bl.baselineDXnum = baselineDX; 
      %table_DXARM_bl.ARM = [];  table_DXARM_bl.DXCHANGE=[];
table_DXARM = outerjoin(table_DXARM,table_DXARM_bl,'Keys',{'RID'},'Type','Left',...
  'LeftVariables',{'RID','Phase','VISCODE','VISCODE2','DXCHANGE','ARM','ENROLLED'},...
  'RightVariables',{'baselineDX','baselineDXnum'},'MergeKeys',true);

%* Join to REGISTRY
table_DXARMREG_ADNI2 = outerjoin(table_DXARM,table_REGISTRY_ADNI2,'Keys',{'RID','Phase','VISCODE'},...
  'RightVariables',{'VISCODE2','EXAMDATE','PTSTATUS','RGCONDCT','RGSTATUS','VISTYPE'},...
  'LeftVariables',{'RID','Phase','VISCODE','DXCHANGE','ARM','ENROLLED','baselineDX','baselineDXnum'},'Type','Left');
%   'LeftVariables',{'RID','Phase','VISCODE','DXCHANGE','ARM','ENROLLED','baselineDX'},'Type','Left');

DXCHANGE_notmissing = not(isnan(table_DXARMREG_ADNI2.DXCHANGE));
%[sum(DXCHANGE_notmissing),length(DXCHANGE_notmissing)]
table_DXARMREG_ADNI2_notMissing = table_DXARMREG_ADNI2(DXCHANGE_notmissing,:);

table_DXARMREG_ADNI1 = outerjoin(table_DXARM,table_REGISTRY_ADNI1,'Keys',{'RID','Phase','VISCODE'},...
  'RightVariables',{'VISCODE2','EXAMDATE','PTSTATUS','RGCONDCT','RGSTATUS','VISTYPE'},...
  'LeftVariables',{'RID','Phase','VISCODE','DXCHANGE','ARM','ENROLLED','baselineDX','baselineDXnum'},'Type','Left');
DXCHANGE_notmissing1 = not(isnan(table_DXARMREG_ADNI1.DXCHANGE));
table_DXARMREG_ADNI1_notMissing = table_DXARMREG_ADNI1(DXCHANGE_notmissing1,:);

%% ADNI2 and active
table_ADNI2 = table_DXARMREG_ADNI2_notMissing(strcmpi(table_DXARMREG_ADNI2_notMissing.Phase,'ADNI2'),:);
table_ADNI2_active = table_ADNI2(strcmpi(table_ADNI2.PTSTATUS,'1'),:);
  table_ADNI2_active.RID = str2double(table_ADNI2_active.RID);
  table_ADNI2_active.m = str2double(strrep(strrep(table_ADNI2_active.VISCODE2,'m',''),'bl','0'));
  table_ADNI2_active = sortrows(table_ADNI2_active,{'baselineDXnum','RID','m'});
  table_ADNI2_active.baselineDXnum = [];
  table_ADNI2_active.m = [];
RID_table_ADNI2_active = unique(table_ADNI2_active.RID);

%* Identify most recent visit
VISCODE2NUM = str2double(strrep(strrep(table_ADNI2_active.VISCODE2,'m',''),'bl','0'));
RIDNUM = table_ADNI2_active.RID; %str2double(table_ADNI23_active.RID);
RIDNUM_u = unique(RIDNUM);
table_ADNI2_active__mostRecentVisit = zeros(size(table_ADNI2_active,1),1);
for ki=1:length(RIDNUM_u)
  rowz = RIDNUM==RIDNUM_u(ki);
  visitz = VISCODE2NUM(rowz);
  mostRecentVisit = visitz==max(visitz);
  rowz = find(rowz);
  table_ADNI2_active__mostRecentVisit(rowz(mostRecentVisit)) = 1;
end

table_ADNI2_active_mostRecentVisit = table_ADNI2_active(table_ADNI2_active__mostRecentVisit==1,:);
% clear table_ADNI23_active__mostRecentVisit

if isnumeric(table_ADNI2_active_mostRecentVisit.baselineDX)
  ADNI2_active_baselineNormal_N = sum(table_ADNI2_active_mostRecentVisit.baselineDX==1);
  ADNI2_active_baselineSMC_N = sum(table_ADNI2_active_mostRecentVisit.baselineDX==2);
  ADNI2_active_baselineEMCI_N = sum(table_ADNI2_active_mostRecentVisit.baselineDX==3);
  ADNI2_active_baselineLMCI_N = sum(table_ADNI2_active_mostRecentVisit.baselineDX==4);
  ADNI2_active_baselineAD_N = sum(table_ADNI2_active_mostRecentVisit.baselineDX==5);
else
  ADNI2_active_baselineNormal_N = sum(strcmpi(table_ADNI2_active_mostRecentVisit.baselineDX,'CN'));
  ADNI2_active_baselineSMC_N = sum(strcmpi(table_ADNI2_active_mostRecentVisit.baselineDX,'SMC'));
  ADNI2_active_baselineEMCI_N = sum(strcmpi(table_ADNI2_active_mostRecentVisit.baselineDX,'EMCI'));
  ADNI2_active_baselineLMCI_N = sum(strcmpi(table_ADNI2_active_mostRecentVisit.baselineDX,'LMCI'));
  ADNI2_active_baselineAD_N = sum(strcmpi(table_ADNI2_active_mostRecentVisit.baselineDX,'AD'));
end

fprintf('\n\n The most recent visit of %i active ADNI2 participants is stored in \n   table_ADNI2_active_mostRecentVisit\n',size(table_ADNI2_active_mostRecentVisit,1))
fprintf('Baseline DX:\n NL   = %i\n SMC  = %i\n EMCI = %i\n LMCI = %i\n AD   = %i\n',ADNI2_active_baselineNormal_N,ADNI2_active_baselineSMC_N,ADNI2_active_baselineEMCI_N,ADNI2_active_baselineLMCI_N,ADNI2_active_baselineAD_N)

%* Sanity check that these total size(table_ADNI2_active_mostRecentVisit,1)
%  ADNI23_active_baselineNormal_N + ADNI23_active_baselineSMC_N + ADNI23_active_baselineEMCI_N + ADNI23_active_baselineLMCI_N + ADNI23_active_baselineAD_N;

%* Now search for all available visits for each of these subjects (regardless of 'Phase')
fprintf('Finding all available visits for prospective ADNI3 subjects.\n')

table_DXARMREGISTRY_notMissing_allvisits = table_DXARMREG_ADNI2_notMissing; %table_DXARMREGISTRY_notMissing(~strcmpi(table_DXARMREGISTRY_notMissing.PTSTATUS,''),:);
  table_DXARMREGISTRY_notMissing_allvisits.RID = str2double(table_DXARMREGISTRY_notMissing_allvisits.RID);
  table_DXARMREGISTRY_notMissing_allvisits.M = str2double(strrep(strrep(table_DXARMREGISTRY_notMissing_allvisits.VISCODE2,'m',''),'bl','0'));
table_D2_old = table_ADNI2_active_mostRecentVisit(:,{'RID'});
table_D2_old = table_DXARMREGISTRY_notMissing_allvisits(ismember(table_DXARMREGISTRY_notMissing_allvisits.RID,table_D2_old.RID),:);
table_D2_old = sortrows(table_D2_old,{'baselineDXnum','RID','M'});
  table_D2_old.baselineDXnum = [];
  table_D2_old = table_D2_old(not(isnan(table_D2_old.M)),:);
  
if writeTables
%   writetable(table_D2_old,fullfile(dataSaveLocation,sprintf('D2_v1_%s.csv',runDate)))
end

%* Extract final rows
mostRecentVisits = false(size(table_D2_old.RID));
RID = table_D2_old.RID; M = table_D2_old.M;
RID_u = unique(RID);
for k=1:length(RID_u)
  rowz = find(RID_u(k)==RID);
  mrv = rowz(M(rowz)==max(M(rowz)));
  mostRecentVisits(mrv) = true;
end

table_D3_old = table_D2_old(mostRecentVisits,:);
if writeTables
%   writetable(table_D3_old,fullfile(dataSaveLocation,'D3_columns.csv')) %writetable(table_ADNI23_active_mostRecentVisit,[dataLocation,'/ADNI2_active_mostRecentVisit.csv'])
%  %   % writetable(table_ADNI23_active_mostRecentVisit,[dataSaveLocation,'/D3_v1.csv']) %writetable(table_ADNI23_active_mostRecentVisit,[dataLocation,'/ADNI2_active_mostRecentVisit.csv'])
end

% adniMerge_file = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/ADNITables/ADNIMERGE.csv';
% table_adniMerge = readtable(adniMerge_file,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

%% Start with ADNI-Merge-Plus
adniMergePlus_file = '/Users/noxtoby/inSync Share/SharedWithDanny/TADPOLE-Data/adniMergePlus.csv'; %'/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TrainingTest/Raz/adniMergePlus/adniMergePlus.csv';
  %adniMergePlus_file = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/TrainingTest/adniMergePlusNeil.csv';

table_adniMergePlus = readtable(adniMergePlus_file,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
  % table_adniMergePlus.Properties.VariableNames{'RID_MERGE'} = 'RID';
  % table_adniMergePlus.Properties.VariableNames{'VISCODE_MERGE'} = 'VISCODE';

%* D2, starting from adniMergePlus
D2_indicator = ismember(table_adniMergePlus.RID,RID_table_ADNI2_active); %D2_indicator = ismember(table_adniMergePlus(:,{'RID','VISCODE'}),table_D2_temp);
table_D2_column = table(table_adniMergePlus.RID,table_adniMergePlus.VISCODE,1*D2_indicator,'VariableNames',{'RID','VISCODE','D2'});
if writeTables
  writetable(table_D2_column,fullfile(dataSaveLocation,sprintf('D2_column_%s.csv',runDate)))
end

%* Note FreeSurfer codes:
%{
FS51codes = FreeSurferROI_ucsffsl51all();
FreeSurfer51_ROIs = FS51codes(:,1); % 23:end
Descriptions = FS51codes(:,2);
table_FS51 = table(FreeSurfer51_ROIs,Descriptions);
writetable(table_FS51,[dataSaveLocation,'/freeSurfer5p1Decoder.csv'])
FS44codes = FreeSurferROI_ucsffsl();
FreeSurfer44_ROIs = FS44codes(:,1); % 29:end
Descriptions = FS44codes(:,2);
table_FS44 = table(FreeSurfer44_ROIs,Descriptions);
writetable(table_FS44,[dataSaveLocation,'/freeSurfer4p4Decoder.csv'])
%}

%* Now for D3: final visit from D2, plus selected columns relevant to
%clinical trials selection
ADNIImagingDataLocation = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/ADNITables/Imaging';
UCSFFSL4p3_csv = fullfile(ADNIImagingDataLocation,'UCSFFSL_02_01_16.csv');
UCSFFSL5p1_csv = fullfile(ADNIImagingDataLocation,'UCSFFSL51ALL_08_01_16.csv');
UCSFFSL1 = readtable(UCSFFSL4p3_csv); % ADNI1: 1.5T
UCSFFSL51 = readtable(UCSFFSL5p1_csv); % ADNIGO/2: 3T
UCSFFSL4p3_columns = UCSFFSL1.Properties.VariableNames;
  FSL4p3_columns = {};
  for k=1:length(UCSFFSL4p3_columns)
    col = UCSFFSL4p3_columns{k};
    if strcmpi(col(1:2),'ST') 
      if ~isempty(str2num(col(3)))
        FSL4p3_columns = [FSL4p3_columns,{col}];
      end
    end
  end
UCSFFSL5p1_columns = sort(UCSFFSL51.Properties.VariableNames);
  FSL5p1_columns = {};
  for k=1:length(UCSFFSL5p1_columns)
    col = UCSFFSL5p1_columns{k};
    if strcmpi(col(1:2),'ST') 
      if ~isempty(str2num(col(3)))
        %col
        FSL5p1_columns = [FSL5p1_columns,{col}];
      end
    end
  end
UCSFFSL_columns = vertcat(FSL4p3_columns(:),FSL5p1_columns(:));
UCSFFSL_columns_manual = {'LONISID','LONIUID','IMAGEUID'...
  ,'OVERALLQC','TEMPQC','FRONTQC','PARQC','INSULAQC','OCCQC','BGQC','CWMQC','VENTQC'...
  ,'ST100SV','ST101SV','ST102CV','ST102SA','ST102TA','ST102TS','ST103CV','ST103SA','ST103TA','ST103TS','ST104CV','ST104SA','ST104TA','ST104TS','ST105CV','ST105SA','ST105TA','ST105TS','ST106CV','ST106SA','ST106TA','ST106TS','ST107CV','ST107SA','ST107TA','ST107TS','ST108CV','ST108SA','ST108TA','ST108TS','ST109CV','ST109SA','ST109TA','ST109TS','ST10CV','ST110CV','ST110SA','ST110TA','ST110TS','ST111CV','ST111SA','ST111TA','ST111TS','ST112SV','ST113CV','ST113SA','ST113TA','ST113TS','ST114CV','ST114SA','ST114TA','ST114TS','ST115CV','ST115SA','ST115TA','ST115TS','ST116CV','ST116SA','ST116TA','ST116TS','ST117CV','ST117SA','ST117TA','ST117TS','ST118CV','ST118SA','ST118TA','ST118TS','ST119CV','ST119SA','ST119TA','ST119TS','ST11SV','ST120SV','ST121CV','ST121SA','ST121TA','ST121TS','ST122SV','ST123CV','ST123SA','ST123TA','ST123TS','ST124SV','ST125SV','ST126SV','ST127SV','ST128SV','ST129CV','ST129SA','ST129TA','ST129TS','ST12SV','ST130CV','ST130SA','ST130TA','ST130TS','ST13CV','ST13SA','ST13TA','ST13TS','ST14CV','ST14SA','ST14TA','ST14TS','ST15CV','ST15SA','ST15TA','ST15TS','ST16SV','ST17SV','ST18SV','ST19SV','ST1SV','ST20SV','ST21SV','ST22CV','ST22SA','ST22TA','ST22TS','ST23CV','ST23SA','ST23TA','ST23TS','ST24CV','ST24SA','ST24TA','ST24TS','ST25CV','ST25SA','ST25TA','ST25TS','ST26CV','ST26SA','ST26TA','ST26TS','ST27SA','ST28CV','ST29SV','ST2SV','ST30SV','ST31CV','ST31SA','ST31TA','ST31TS','ST32CV','ST32SA','ST32TA','ST32TS','ST33SV','ST34CV','ST34SA','ST34TA','ST34TS','ST35CV','ST35SA','ST35TA','ST35TS','ST36CV','ST36SA','ST36TA','ST36TS','ST37SV','ST38CV','ST38SA','ST38TA','ST38TS','ST39CV','ST39SA','ST39TA','ST39TS','ST3SV','ST40CV','ST40SA','ST40TA','ST40TS','ST41SV','ST42SV','ST43CV','ST43SA','ST43TA','ST43TS','ST44CV','ST44SA','ST44TA','ST44TS','ST45CV','ST45SA','ST45TA','ST45TS','ST46CV','ST46SA','ST46TA','ST46TS','ST47CV','ST47SA','ST47TA','ST47TS','ST48CV','ST48SA','ST48TA','ST48TS','ST49CV','ST49SA','ST49TA','ST49TS','ST4SV','ST50CV','ST50SA','ST50TA','ST50TS','ST51CV','ST51SA','ST51TA','ST51TS','ST52CV','ST52SA','ST52TA','ST52TS','ST53SV','ST54CV','ST54SA','ST54TA','ST54TS','ST55CV','ST55SA','ST55TA','ST55TS','ST56CV','ST56SA','ST56TA','ST56TS','ST57CV','ST57SA','ST57TA','ST57TS','ST58CV','ST58SA','ST58TA','ST58TS','ST59CV','ST59SA','ST59TA','ST59TS','ST5SV','ST60CV','ST60SA','ST60TA','ST60TS','ST61SV','ST62CV','ST62SA','ST62TA','ST62TS','ST63SV','ST64CV','ST64SA','ST64TA','ST64TS','ST65SV','ST66SV','ST67SV','ST68SV','ST69SV','ST6SV','ST70SV','ST71SV','ST72CV','ST72SA','ST72TA','ST72TS','ST73CV','ST73SA','ST73TA','ST73TS','ST74CV','ST74SA','ST74TA','ST74TS','ST75SV','ST76SV','ST77SV','ST78SV','ST79SV','ST7SV','ST80SV','ST81CV','ST81SA','ST81TA','ST81TS','ST82CV','ST82SA','ST82TA','ST82TS','ST83CV','ST83SA','ST83TA','ST83TS','ST84CV','ST84SA','ST84TA','ST84TS','ST85CV','ST85SA','ST85TA','ST85TS','ST86SA','ST87CV','ST88SV','ST89SV','ST8SV','ST90CV','ST90SA','ST90TA','ST90TS','ST91CV','ST91SA','ST91TA','ST91TS','ST92SV','ST93CV','ST93SA','ST93TA','ST93TS','ST94CV','ST94SA','ST94TA','ST94TS','ST95CV','ST95SA','ST95TA','ST95TS','ST96SV','ST97CV','ST97SA','ST97TA','ST97TS','ST98CV','ST98SA','ST98TA','ST98TS','ST99CV','ST99SA','ST99TA','ST99TS','ST9SV'};

UCSFFSL_columns = strcat(UCSFFSL_columns_manual,'_UCSFFSL_02_01_16_UCSFFSL51ALL_08_01_16');

% table_adniMergePlus.Properties.VariableNames(122:468).';

D3_columns = {...
  'RID','VISCODE','EXAMDATE'...,'baselineDX'
  ,'DX','AGE','PTGENDER','PTEDUCAT','PTETHCAT','PTRACCAT','PTMARRY','COLPROT'...
  ... 'CDRSB'
  ,'ADAS13','MMSE'...
  ,'Ventricles','Hippocampus','WholeBrain','Entorhinal','Fusiform','MidTemp','ICV'...
  ...
  };
D3_columns = vertcat(D3_columns(:),UCSFFSL_columns(:));


table_D3_data = table_adniMergePlus(D2_indicator,D3_columns);
M = table_adniMergePlus{D2_indicator,'M'};
%* Identify most recent visit
mostRecentVisit = false(size(table_D3_data.RID));
RID = table_D3_data.RID; 
RID_u = unique(RID);
for k=1:length(RID_u)
  rowz = find(RID_u(k)==RID);
  mrv = rowz(M(rowz)==max(M(rowz)));
  mostRecentVisit(mrv) = true;
end
table_D3_data = table_D3_data(mostRecentVisit,:);
if writeTables
  writetable(table_D3_data,fullfile(dataSaveLocation,sprintf('D3_%s.csv',runDate)))
end

%%
%* Template submission spreadsheet
targets = {'DX','ADAS13','Ventricles'}; %{'pCN','pMCI','pAD','ADAS13','ADAS13_CI50pc','Ventricles_ICV','Ventricles_ICV_CI50pc'};
table_template_submission_baseline = table_D3_data(:,[{'RID','EXAMDATE'},targets,{'ICV'}]);
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
  writetable(table_template_submission_baseline,sprintf('ForecastBaseline_%s.csv',runDate));
  writetable(table_template_submission,sprintf('ForecastTemplateSubmission_%s.csv',runDate));
end


%% Leaderboard sets: same idea, but using ADNI1 rollovers
% ====== Raz's leaderboard method ======
% Selected all subjects with:
%  * at least two scans in ADNI1
%  * were either CN or MCI on the last clinical assessment
%  * were rollovers in ADNI GO/2
adniMerge_file = '/Users/noxtoby/Documents/Research/UCLPOND/Projects/201612 POND challenge/Data/ADNITables/ADNIMERGE.csv';
table_adniMerge = readtable(adniMerge_file,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
adni1Merge_ORIGPROT = strcmpi(table_adniMerge.ORIGPROT,'ADNI1');
adni1Merge_COLPROT = strcmpi(table_adniMerge.COLPROT,'ADNI1');
adni1Merge_rolledOver = adni1Merge_ORIGPROT & ~adni1Merge_COLPROT;
  %* At least 2 visits
  nVisitsMin = 2;
  VISCODE2NUM = str2double(strrep(strrep(table_adniMerge.VISCODE,'m',''),'bl','0'));
  RIDNUM = str2double(table_adniMerge.RID);
  RIDNUM_u = unique(RIDNUM);
  adni1Merge_moreThanOneVisit = zeros(size(adni1Merge_COLPROT));
  adni1Merge_mostRecentVisit  = zeros(size(adni1Merge_COLPROT));
  for ki=1:length(RIDNUM_u)
    rowz = RIDNUM==RIDNUM_u(ki);
    rowz = rowz & adni1Merge_COLPROT;
    if sum(rowz)>=nVisitsMin
      adni1Merge_moreThanOneVisit(rowz) = 1;
    end
    visitz = VISCODE2NUM(rowz); %* ADNI1 only
    %* Most recent visit
    mostRecentVisit = visitz==max(visitz);
    rowz_f = find(rowz);
    adni1Merge_mostRecentVisit(rowz_f(mostRecentVisit)) = 1;
  end
ADNI1_CNorMCIfinalvisit = ismember(table_adniMerge.DX,{'NL','MCI','NL to MCI','MCI to NL','Dementia to MCI'}) & adni1Merge_mostRecentVisit;
ADNI1_2scans_CNorMCIfinalvisit_rolledOver = adni1Merge_rolledOver & adni1Merge_moreThanOneVisit & ADNI1_CNorMCIfinalvisit;
% The above criteria yielded a set of 132 potential CN subjects and 101 potential MCI subjects
% I selected 2/3 of each group and assigned all ADNI1 visits to LB2
% I assigned all ADNI GO/2 visits for these subjects to LB4
% I assigned all the remaining subjects not included in LB2 or LB4 to LB1.
% 
% I pushed all the changes to the code and also attached the generated data (you can pull the code changes from github). I ran the following checks:
% compared the output of your Matlab-generated dataset with my python-generated one, and everything matches
% manually checked a few entries for X-sectional FS data
% manually checked some entries for the LB datasets
% wrote more comprehensive automatic checks (see below)
% 
% In particular, I also wrote some automatic concistency checks in TADPOLE_D1.py, which compare biomarker values between the TADPOLE dataset and each individual spreadsheet, for several subjects. I wrote some automatic checks also for the D1/D2/LB1-4 columns. Everything looks ok. 
% 
% What I haven't checked though is the D2_column and D3. It would be great if you could sanity check those, and also have another look on D1. Is there anything else we need to do? 
% 
% Finally, I am currently visiting NYC and will be flying back to London on Tuesday evening, so I won't make it for the POND meeting. You can reach me via email if you need help.
% 
% Regards,
% Raz

%% ADNI1, active, at least two time points
table_ADNI1 = table_DXARMREG_ADNI1_notMissing(strcmpi(table_DXARMREG_ADNI1_notMissing.Phase,'ADNI1'),:);
table_ADNI1_ = table_ADNI1;
  table_ADNI1_.RID = str2double(table_ADNI1_.RID);
  table_ADNI1_.m = str2double(strrep(strrep(table_ADNI1_.VISCODE2,'m',''),'bl','0'));
  table_ADNI1_ = sortrows(table_ADNI1_,{'baselineDXnum','RID','m'});
  table_ADNI1_.baselineDXnum = [];
  table_ADNI1_.m = [];
[RID_table_ADNI1,i1,i2] = unique(table_ADNI1_.RID);

%* Require at least 2 visits
nVisitsMin = 2;


%* Identify most recent visit
VISCODE2NUM = str2double(strrep(strrep(table_ADNI1_.VISCODE2,'m',''),'bl','0'));
RIDNUM = table_ADNI1_.RID; %str2double(table_ADNI23_active.RID);
RIDNUM_u = unique(RIDNUM);
table_ADNI1___mostRecentVisit = zeros(size(table_ADNI1_,1),1);
table_ADNI1___hasMultipleTimePoints = zeros(size(table_ADNI1_,1),1);
for ki=1:length(RIDNUM_u)
  rowz = RIDNUM==RIDNUM_u(ki);
  if sum(rowz)>1
    table_ADNI1___hasMultipleTimePoints(rowz) = 1;
  end
  visitz = VISCODE2NUM(rowz);
  mostRecentVisit = visitz==max(visitz);
  rowz = find(rowz);
  table_ADNI1___mostRecentVisit(rowz(mostRecentVisit)) = 1;
end

table_ADNI1__mostRecentVisit = table_ADNI1_(table_ADNI1___mostRecentVisit==1,:);

if isnumeric(table_ADNI1__mostRecentVisit.baselineDX)
  ADNI1_active_baselineNormal_N = sum(table_ADNI1__mostRecentVisit.baselineDX==1);
  ADNI1_active_baselineSMC_N    = sum(table_ADNI1__mostRecentVisit.baselineDX==2);
  ADNI1_active_baselineEMCI_N   = sum(table_ADNI1__mostRecentVisit.baselineDX==3);
  ADNI1_active_baselineLMCI_N   = sum(table_ADNI1__mostRecentVisit.baselineDX==4);
  ADNI1_active_baselineAD_N     = sum(table_ADNI1__mostRecentVisit.baselineDX==5);
else
  ADNI1_active_baselineNormal_N = sum(strcmpi(table_ADNI1__mostRecentVisit.baselineDX,'CN'));
  ADNI1_active_baselineSMC_N    = sum(strcmpi(table_ADNI1__mostRecentVisit.baselineDX,'SMC'));
  ADNI1_active_baselineEMCI_N   = sum(strcmpi(table_ADNI1__mostRecentVisit.baselineDX,'EMCI'));
  ADNI1_active_baselineLMCI_N   = sum(strcmpi(table_ADNI1__mostRecentVisit.baselineDX,'LMCI'));
  ADNI1_active_baselineAD_N     = sum(strcmpi(table_ADNI1__mostRecentVisit.baselineDX,'AD'));
end

fprintf('\n\n The most recent visit of %i ADNI1 participants is stored in \n   table_ADNI1__mostRecentVisit\n',size(table_ADNI1__mostRecentVisit,1))
fprintf('Baseline DX:\n NL   = %i\n SMC  = %i\n EMCI = %i\n LMCI = %i\n AD   = %i\n',ADNI1_active_baselineNormal_N,ADNI1_active_baselineSMC_N,ADNI1_active_baselineEMCI_N,ADNI1_active_baselineLMCI_N,ADNI1_active_baselineAD_N)

%* Sanity check that these total size(table_ADNI1__mostRecentVisit,1)
%  ADNI1_active_baselineNormal_N + ADNI1_active_baselineSMC_N + ADNI1_active_baselineEMCI_N + ADNI1_active_baselineLMCI_N + ADNI1_active_baselineAD_N;

%* Now search for all available visits for each of these subjects (regardless of 'Phase')
fprintf('Finding all available visits for ADNI1 rollover subjects.\n')

table_DXARMREGISTRY_notMissing_allvisits = table_DXARMREG_ADNI1_notMissing;
  table_DXARMREGISTRY_notMissing_allvisits.RID = str2double(table_DXARMREGISTRY_notMissing_allvisits.RID);
  table_DXARMREGISTRY_notMissing_allvisits.M = str2double(strrep(strrep(table_DXARMREGISTRY_notMissing_allvisits.VISCODE2,'m',''),'bl','0'));
table_LB2_old = table_ADNI1__mostRecentVisit(:,{'RID'});
table_LB2_old = table_DXARMREGISTRY_notMissing_allvisits(ismember(table_DXARMREGISTRY_notMissing_allvisits.RID,table_LB2_old.RID),:);
table_LB2_old = sortrows(table_LB2_old,{'baselineDXnum','RID','M'});
  table_LB2_old.baselineDXnum = [];
  table_LB2_old = table_LB2_old(not(isnan(table_LB2_old.M)),:);
  
if writeTables
%   writetable(table_LB2_old,fullfile(dataSaveLocation,sprintf('LB2_v1_%s.csv',runDate)))
end

%* Extract final rows
mostRecentVisits = false(size(table_LB2_old.RID));
RID = table_LB2_old.RID; M = table_LB2_old.M;
RID_u = unique(RID);
for k=1:length(RID_u)
  rowz = find(RID_u(k)==RID);
  mrv = rowz(M(rowz)==max(M(rowz)));
  mostRecentVisits(mrv) = true;
end

table_LB4_old = table_LB2_old(mostRecentVisits,:);

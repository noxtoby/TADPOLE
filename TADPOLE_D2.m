% TADPOLE_D2.m Identifying prediction set D2 for TADPOLE challenge 2017
% Neil Oxtoby, UCL, March 2017

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

writeTables = true;
runDate = datestr(date,'yyyymmdd');

dataLocation = pwd; 
dataSaveLocation = pwd;

%* ADNI tables
MAYOADIRL_MRI_MCH = fullfile(dataLocation, 'MAYOADIRL_MRI_MCH_09_15_16.csv'); % one row per MR finding
REGISTRY = fullfile(dataLocation,'REGISTRY.csv');
ADNI2_VISITID = fullfile(dataLocation,'ADNI2_VISITID.csv');
%* DXARM => contains specifics on EMCI/LMCI/etc
ARM = fullfile(dataLocation,'ARM.csv'); 
DXSUM = fullfile(dataLocation,'DXSUM_PDXCONV_ADNIALL.csv'); 
ADNIMERGE = fullfile(dataLocation,'ADNIMERGE.csv');

%* Read ADNI tables
table_REGISTRY = readtable(REGISTRY);
table_ARM = readtable(ARM);
table_DXSUM = readtable(DXSUM);
  table_DXSUM.DXCHANGE = str2double(table_DXSUM.DXCHANGE); % make numeric
table_ADNIMERGE = readtable(ADNIMERGE,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

%* REGISTRY => select ADNI2 participants
ADNI2 = strcmpi(table_REGISTRY.Phase,'ADNI2') & strcmpi(table_REGISTRY.RGSTATUS,'1');
table_REGISTRY_ADNI2 =  table_REGISTRY(ADNI2,:);
ADNI2_new_sc = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v01'});
ADNI2_new_bl = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v03'});
ADNI2_continuing = ADNI2 & ismember(table_REGISTRY.VISCODE,{'v06'});
%* REGISTRY => identify ADNI1 participants
%*     (Leaderboard data: rollovers from ADNI1 into ADNIGO or ADNI2)
ADNI1 = strcmpi(table_REGISTRY.Phase,'ADNI1');
table_REGISTRY_ADNI1 =  table_REGISTRY(ADNI1,:);
%* REGISTRY => identify ADNIGO participants
ADNIGO = strcmpi(table_REGISTRY.Phase,'ADNIGO');
table_REGISTRY_ADNIGO =  table_REGISTRY(ADNIGO,:);

%* REGISTRY => identify ADNI3 participants
ADNI3 = strcmpi(table_REGISTRY.Phase,'ADNI3') & strcmpi(table_REGISTRY.RGSTATUS,'1');
%fprintf('    Found %i ADNI3 visits.    \n',sum(ADNI3))
table_REGISTRY_ADNI23 = table_REGISTRY(ADNI2 | ADNI3,:);

%% REGISTRY => Active at final visit
  ActiveVisits = strcmpi(table_REGISTRY.PTSTATUS,'1');
  inActiveVisits = strcmpi(table_REGISTRY.PTSTATUS,'2');
  VisitConducted_ADNI1 = strcmpi(table_REGISTRY.RGCONDCT,'1');
  VisitNotConducted_ADNI1 = strcmpi(table_REGISTRY.RGCONDCT,'0');
  %* Identify most recent visit
  %VISCODE2_num = str2double(strrep(strrep(table_REGISTRY.VISCODE2,'m',''),'bl','0'));
  VISCODE2_num = str2double(strrep(strrep(strrep(strrep(table_REGISTRY.VISCODE2,'scmri','0'),'m',''),'bl','0'),'sc','0'));
  RID_num = str2double(table_REGISTRY.RID);
  PTSTATUS = table_REGISTRY.PTSTATUS;
  RID_num_u = unique(RID_num);
  %MostRecentVisit = zeros(size(table_REGISTRY,1),1);
  InactiveAtAnyVisit = zeros(size(table_REGISTRY,1),1);
  MostRecentVisit_ADNI1 = zeros(size(table_REGISTRY,1),1);
  MostRecentVisit_ADNIGO = zeros(size(table_REGISTRY,1),1);
  MostRecentVisit_ADNI2 = zeros(size(table_REGISTRY,1),1);
  for ki=1:length(RID_num_u)
    rowz = RID_num==RID_num_u(ki);
    %* Most recent visit, per study phase
    rowz_ADNI1  = rowz & ADNI1;
    rowz_ADNIGO = rowz & ADNIGO;
    rowz_ADNI2  = rowz & ADNI2;
    
    visitz_ADNI1  = VISCODE2_num(rowz_ADNI1);
    active_ADNI1  = VisitConducted_ADNI1 & rowz_ADNI1;
    inactive_ADNI1  = VisitNotConducted_ADNI1 & rowz_ADNI1;
      mostRecentVisit_ADNI1 = visitz_ADNI1==max(visitz_ADNI1);
      rowz_ADNI1 = find(rowz_ADNI1);
      MostRecentVisit_ADNI1(rowz_ADNI1(mostRecentVisit_ADNI1)) = 1;
      
    visitz_ADNIGO    = VISCODE2_num(rowz_ADNIGO);
    active_ADNIGO = ActiveVisits & rowz_ADNIGO;
    inactive_ADNIGO = inActiveVisits & rowz_ADNIGO;
      mostRecentVisit_ADNIGO = visitz_ADNIGO==max(visitz_ADNIGO);
      rowz_ADNIGO = find(rowz_ADNIGO);
      MostRecentVisit_ADNIGO(rowz_ADNIGO(mostRecentVisit_ADNIGO)) = 1;
    
    visitz_ADNI2     = VISCODE2_num(rowz_ADNI2);
    active_ADNI2  = ActiveVisits & rowz_ADNI2;
    inactive_ADNI2  = inActiveVisits & rowz_ADNI2;
      mostRecentVisit_ADNI2 = visitz_ADNI2==max(visitz_ADNI2);
      rowz_ADNI2 = find(rowz_ADNI2);
      MostRecentVisit_ADNI2(rowz_ADNI2(mostRecentVisit_ADNI2)) = 1;
    
    %* Ensure that no previous ADNIGO/2 PTSTATUS were INACTIVE
    visitz = VISCODE2_num(rowz);
    rowz = find(rowz);
    if any(inactive_ADNIGO | inactive_ADNI2)
      InactiveAtAnyVisit(rowz) = 1;
    end
  end
  %MostRecentVisit = MostRecentVisit==1; % boolean
  
  %* Identify those who are active at their final visit
  ActiveAtMostRecentVisit_ADNI1  = MostRecentVisit_ADNI1  & VisitConducted_ADNI1;
  ActiveAtMostRecentVisit_ADNIGO = MostRecentVisit_ADNIGO & ActiveVisits & ~InactiveAtAnyVisit;
  ActiveAtMostRecentVisit_ADNI2  = MostRecentVisit_ADNI2  & ActiveVisits & ~InactiveAtAnyVisit;
  
  RID_ActiveAtMostRecentVisit_ADNI1  = table_REGISTRY.RID(ActiveAtMostRecentVisit_ADNI1);
  RID_ActiveAtMostRecentVisit_ADNIGO = table_REGISTRY.RID(ActiveAtMostRecentVisit_ADNIGO);
  RID_ActiveAtMostRecentVisit_ADNI2  = table_REGISTRY.RID(ActiveAtMostRecentVisit_ADNI2);
  
  fprintf('--- Active status at final visit (ADNI1: RGCONDUCT==1; ADNIGO/2: PTSTATUS==1, and never inactive)\n--- Found %i ADNI1 participants\n---       %i ADNIGO participants\n---       %i ADNI2 participants\n',length(RID_ActiveAtMostRecentVisit_ADNI1),length(RID_ActiveAtMostRecentVisit_ADNIGO),length(RID_ActiveAtMostRecentVisit_ADNI2))
  
%% Some prescribed preprocessing from the ADNI training slides 
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

%% DXARM + REGISTRY
table_DXARMREG = outerjoin(table_DXARM,table_REGISTRY,'Keys',{'RID','Phase','VISCODE'},...
  'RightVariables',{'VISCODE2','EXAMDATE','PTSTATUS','RGCONDCT','RGSTATUS','VISTYPE'},...
  'LeftVariables',{'RID','Phase','VISCODE','DXCHANGE','ARM','ENROLLED','baselineDX','baselineDXnum'},'Type','Left');

%% Report numbers by diagnosis
BaselineDX_ADNI1  = table_DXARMREG(ismember(table_DXARMREG.RID,RID_ActiveAtMostRecentVisit_ADNI1)  & strcmpi(table_DXARMREG.Phase,'ADNI1'), {'RID','baselineDX'});
BaselineDX_ADNIGO = table_DXARMREG(ismember(table_DXARMREG.RID,RID_ActiveAtMostRecentVisit_ADNIGO) & strcmpi(table_DXARMREG.Phase,'ADNIGO'),{'RID','baselineDX'});
BaselineDX_ADNI2  = table_DXARMREG(ismember(table_DXARMREG.RID,RID_ActiveAtMostRecentVisit_ADNI2)  & strcmpi(table_DXARMREG.Phase,'ADNI2'), {'RID','baselineDX'});

BaselineDX_ADNI1_u  = unique(BaselineDX_ADNI1);
BaselineDX_ADNIGO_u = unique(BaselineDX_ADNIGO);
BaselineDX_ADNI2_u  = unique(BaselineDX_ADNI2);

fprintf('\n\n - - - Identifying active participants in each Phase of ADNI - - - \n')
fprintf(' - - - ADNI1 (%i) - - - \n',height(BaselineDX_ADNI1_u))
fprintf('Baseline DX:\n NL   = %i\n SMC  = %i\n EMCI = %i\n LMCI = %i\n AD   = %i\n'...
  ,sum(strcmpi(BaselineDX_ADNI1_u.baselineDX,'CN'))...
  ,sum(strcmpi(BaselineDX_ADNI1_u.baselineDX,'SMC'))...
  ,sum(strcmpi(BaselineDX_ADNI1_u.baselineDX,'EMCI'))...
  ,sum(strcmpi(BaselineDX_ADNI1_u.baselineDX,'LMCI'))...
  ,sum(strcmpi(BaselineDX_ADNI1_u.baselineDX,'AD')))
fprintf(' - - - ADNIGO (%i) - - - \n',height(BaselineDX_ADNIGO_u))
fprintf('Baseline DX:\n NL   = %i\n SMC  = %i\n EMCI = %i\n LMCI = %i\n AD   = %i\n'...
  ,sum(strcmpi(BaselineDX_ADNIGO_u.baselineDX,'CN'))...
  ,sum(strcmpi(BaselineDX_ADNIGO_u.baselineDX,'SMC'))...
  ,sum(strcmpi(BaselineDX_ADNIGO_u.baselineDX,'EMCI'))...
  ,sum(strcmpi(BaselineDX_ADNIGO_u.baselineDX,'LMCI'))...
  ,sum(strcmpi(BaselineDX_ADNIGO_u.baselineDX,'AD')))
fprintf(' - - - ADNI2 (%i) - - - \n',height(BaselineDX_ADNI2_u))
fprintf('Baseline DX:\n NL   = %i\n SMC  = %i\n EMCI = %i\n LMCI = %i\n AD   = %i\n ''''   = %i\n'...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'CN'))...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'SMC'))...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'EMCI'))...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'LMCI'))...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'AD'))...
  ,sum(strcmpi(BaselineDX_ADNI2_u.baselineDX,'')))


%% Identify D2: all historical ADNIMERGE rows for "prospective rollovers" from ADNI2 into ADNI3
D2_RID = BaselineDX_ADNI2_u.RID;
table_D2_columns = table_ADNIMERGE(:,{'RID','VISCODE'});
table_D2_columns.D2 = 1*ismember(table_ADNIMERGE.RID,D2_RID);

%% Identify D3: final visit
table_D2_D3_columns = table_D2_columns;
table_D2_D3_columns.M = str2double(strrep(strrep(table_D2_D3_columns.VISCODE,'bl','0'),'m',''));
% [table_D3_columns_sorted,I] = sortrows(table_D3_columns,{'RID','M'});
  %* Identify most recent visit
  RID_num = str2double(table_D2_D3_columns.RID);
  RID_num_u = unique(RID_num);
  MostRecentVisit = zeros(size(table_D2_D3_columns,1),1);
  for ki=1:length(RID_num_u)
    rowz = RID_num==RID_num_u(ki);
    %* Most recent visit
    visitz = table_D2_D3_columns.M(rowz);
    mostRecentVisit = visitz==max(visitz);
    rowz = find(rowz);
    MostRecentVisit(rowz(mostRecentVisit)) = 1;
  end
  table_D2_D3_columns.D3 = 1*(MostRecentVisit==1 & table_D2_D3_columns.D2);
  table_D2_D3_columns.M = [];
  
  table_D2_column = table_D2_D3_columns;
  table_D2_column.D3 = [];
  if writeTables
    writetable(table_D2_D3_columns,fullfile(dataSaveLocation,sprintf('TADPOLE_D2_D3_columns_MATLAB_%s.csv',runDate)))
    writetable(table_D2_column,fullfile(dataSaveLocation,'TADPOLE_D2_column.csv'))
  end





% TADPOLE_D3_completeVisit.m Identifying potential test subjects for TADPOLE challenge 2017
%
% The original D3 simply takes the most recent visit for individuals in D2
% (prospective rollovers into ADNI3).
% There was a lot of missing data, for various reasons.
%
% This alternative version of D3 finds the most recent visit *without missing
% data*.
%  Explicitly, this script searches back in time through the D2 data set,
%  identifying visits where the individual has data for each TADPOLE
%  Challenge target variable: DX, ADAS13, and Ventricles.
%
% Output:
%  TADPOLE_D3_completeVisit.csv
%
% This is an alternative D3 which comes under ID9–ID12 on the submissions table
% here:
%  https://tadpole.grand-challenge.org/details/#Submissions
%
% ============
% Date:
%   18 September 2017
% Author: 
%   Neil P. Oxtoby
%   University College London
%
% For more information on TADPOLE Challenge:
%   http://tadpole.grand-shallenge.org 

% To regenerate the alternative D3, place this script in the same location as
% the TADPOLE_D1_D2.csv spreadsheet downloaded from the LONI website.

%%
%* Preliminaries
writeTables = true;
startOfADNI1  = '2005-07-01';
startOfADNIGO = '2010-04-01';
startOfADNI2  = '2011-01-01';
endOfADNI1    = '2011-06-30';
endOfADNIGO   = '2012-10-31';
startOfADNI3  = '2016-10-01';
endOfADNI2    = '2017-10-31';
endOfADNI3    = '2021-10-31';
daysInAYear = 365.25;

%* Spreadsheet location(s)
fprintf('Assumes that you''ve put TADPOLE_D1_D2.csv into the present working directory.\n')
dataLocation = pwd; 
dataSaveLocation = pwd; 

%* Read TADPOLE data
TADPOLE_D1_D2_csv = fullfile(dataLocation,'TADPOLE_D1_D2.csv');
table_D1D2 = readtable(TADPOLE_D1_D2_csv,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

%% Search D2 for candidate D3 rows (most recent visit having complete target data)
timeZero = endOfADNI2;
table_D2 = table_D1D2(table_D1D2.D2==1,:);
table_D2_targetVariablesOnly = table_D2(:,{'RID','VISCODE','EXAMDATE','COLPROT','ORIGPROT','DX','ADAS13','Ventricles'});
table_D2_targetVariablesOnly.t = (datenum(table_D2_targetVariablesOnly.EXAMDATE) - datenum(timeZero))/365.25;

%*** Search back from final visit for available data
%* Sort by time, within subject
[table_D2_targetVariablesOnly,I] = sortrows(table_D2_targetVariablesOnly,{'RID','t'});
table_D2 = table_D2(I,:);
%* Individuals - RosterID
RID = table_D2_targetVariablesOnly.RID;
RID_u = unique(RID);

%* Initialise some arrays 
row_latestVisit = nan(size(RID_u));               % Latest visit
row_latestVisit_completeData = nan(size(RID_u));  % ...complete data (DX,ADAS13,Ventricles)
% Years prior to end of ADNI2
years_backToCompleteDataVisit = nan(size(RID_u));
years_backToLatestVentricles = nan(size(RID_u));
years_backToLatestADAS13 = nan(size(RID_u));
years_backToLatestDX = nan(size(RID_u));

%* Identify not missing values
notMissing_DX = ~strcmpi(table_D2_targetVariablesOnly.DX,'');
notMissing_ADAS13 = ~isnan(table_D2_targetVariablesOnly.ADAS13);
notMissing_Ventricles = ~isnan(table_D2_targetVariablesOnly.Ventricles);
notMissing_targets = notMissing_DX & notMissing_ADAS13 & notMissing_Ventricles;

%* ...most recent not missing

for k=1:length(RID_u)
  % Rows for individual k
  rowz_i = table_D2_targetVariablesOnly.RID==RID_u(k);
  kr = find(rowz_i);
  row_latestVisit(k) = max(kr);
  rows_latestVisitDX = find(notMissing_DX(rowz_i),1,'last');
  rows_latestVisitADAS13 = find(notMissing_ADAS13(rowz_i),1,'last');
  rows_latestVisitVentricles = find(notMissing_Ventricles(rowz_i),1,'last');
  
  %* Complete target data at a single visit
  rowz_i_complete = rowz_i & notMissing_targets;
  if sum(rowz_i_complete)>=1
    kr_complete = find(rowz_i_complete);
    t_i = table_D2_targetVariablesOnly.t(rowz_i_complete); % complete data only
    mostRecentComplete_i = find(t_i == max(t_i),1,'last');
    years_backToCompleteDataVisit(k) = t_i(mostRecentComplete_i);
    mostRecentComplete_k = kr_complete(mostRecentComplete_i);
    row_latestVisit_completeData(k) = mostRecentComplete_k;
    %fprintf('k = %i, DX = %s, colr = %i,%i,%i\n',k,table_D2_targetVariablesOnly.DX{kr_complete(mostRecentComplete_i)},c)
  end
end



%% D3 
%* Rows = most recent single visit with complete data
D3_rows = false(size(table_D2_targetVariablesOnly,1),1);
D3_rows( row_latestVisit_completeData(~isnan(row_latestVisit_completeData)) ) = true;
%* Columns = demographics plus DX, ADAS13, Ventricles, UCSFFSX4p3
D3_cols = {'RID','VISCODE','EXAMDATE','DX','AGE','PTGENDER','PTEDUCAT','PTETHCAT','PTRACCAT','PTMARRY','COLPROT','ADAS13','MMSE','Ventricles','Hippocampus','WholeBrain','Entorhinal','Fusiform','MidTemp','ICV'};
UCSCFFSX_cols = {'EXAMDATE','VERSION','LONISID','FLDSTRENG','LONIUID','IMAGEUID','RUNDATE','STATUS','OVERALLQC','TEMPQC','FRONTQC','PARQC','INSULAQC','OCCQC','BGQC','CWMQC','VENTQC','ST100SV','ST101SV','ST102CV','ST102SA','ST102TA','ST102TS','ST103CV','ST103SA','ST103TA','ST103TS','ST104CV','ST104SA','ST104TA','ST104TS','ST105CV','ST105SA','ST105TA','ST105TS','ST106CV','ST106SA','ST106TA','ST106TS','ST107CV','ST107SA','ST107TA','ST107TS','ST108CV','ST108SA','ST108TA','ST108TS','ST109CV','ST109SA','ST109TA','ST109TS','ST10CV','ST110CV','ST110SA','ST110TA','ST110TS','ST111CV','ST111SA','ST111TA','ST111TS','ST112SV','ST113CV','ST113SA','ST113TA','ST113TS','ST114CV','ST114SA','ST114TA','ST114TS','ST115CV','ST115SA','ST115TA','ST115TS','ST116CV','ST116SA','ST116TA','ST116TS','ST117CV','ST117SA','ST117TA','ST117TS','ST118CV','ST118SA','ST118TA','ST118TS','ST119CV','ST119SA','ST119TA','ST119TS','ST11SV','ST120SV','ST121CV','ST121SA','ST121TA','ST121TS','ST122SV','ST123CV','ST123SA','ST123TA','ST123TS','ST124SV','ST125SV','ST126SV','ST127SV','ST128SV','ST129CV','ST129SA','ST129TA','ST129TS','ST12SV','ST130CV','ST130SA','ST130TA','ST130TS','ST13CV','ST13SA','ST13TA','ST13TS','ST14CV','ST14SA','ST14TA','ST14TS','ST15CV','ST15SA','ST15TA','ST15TS','ST16SV','ST17SV','ST18SV','ST19SV','ST1SV','ST20SV','ST21SV','ST22CV','ST22SA','ST22TA','ST22TS','ST23CV','ST23SA','ST23TA','ST23TS','ST24CV','ST24SA','ST24TA','ST24TS','ST25CV','ST25SA','ST25TA','ST25TS','ST26CV','ST26SA','ST26TA','ST26TS','ST27SA','ST28CV','ST29SV','ST2SV','ST30SV','ST31CV','ST31SA','ST31TA','ST31TS','ST32CV','ST32SA','ST32TA','ST32TS','ST33SV','ST34CV','ST34SA','ST34TA','ST34TS','ST35CV','ST35SA','ST35TA','ST35TS','ST36CV','ST36SA','ST36TA','ST36TS','ST37SV','ST38CV','ST38SA','ST38TA','ST38TS','ST39CV','ST39SA','ST39TA','ST39TS','ST3SV','ST40CV','ST40SA','ST40TA','ST40TS','ST41SV','ST42SV','ST43CV','ST43SA','ST43TA','ST43TS','ST44CV','ST44SA','ST44TA','ST44TS','ST45CV','ST45SA','ST45TA','ST45TS','ST46CV','ST46SA','ST46TA','ST46TS','ST47CV','ST47SA','ST47TA','ST47TS','ST48CV','ST48SA','ST48TA','ST48TS','ST49CV','ST49SA','ST49TA','ST49TS','ST4SV','ST50CV','ST50SA','ST50TA','ST50TS','ST51CV','ST51SA','ST51TA','ST51TS','ST52CV','ST52SA','ST52TA','ST52TS','ST53SV','ST54CV','ST54SA','ST54TA','ST54TS','ST55CV','ST55SA','ST55TA','ST55TS','ST56CV','ST56SA','ST56TA','ST56TS','ST57CV','ST57SA','ST57TA','ST57TS','ST58CV','ST58SA','ST58TA','ST58TS','ST59CV','ST59SA','ST59TA','ST59TS','ST5SV','ST60CV','ST60SA','ST60TA','ST60TS','ST61SV','ST62CV','ST62SA','ST62TA','ST62TS','ST63SV','ST64CV','ST64SA','ST64TA','ST64TS','ST65SV','ST66SV','ST67SV','ST68SV','ST69SV','ST6SV','ST70SV','ST71SV','ST72CV','ST72SA','ST72TA','ST72TS','ST73CV','ST73SA','ST73TA','ST73TS','ST74CV','ST74SA','ST74TA','ST74TS','ST75SV','ST76SV','ST77SV','ST78SV','ST79SV','ST7SV','ST80SV','ST81CV','ST81SA','ST81TA','ST81TS','ST82CV','ST82SA','ST82TA','ST82TS','ST83CV','ST83SA','ST83TA','ST83TS','ST84CV','ST84SA','ST84TA','ST84TS','ST85CV','ST85SA','ST85TA','ST85TS','ST86SA','ST87CV','ST88SV','ST89SV','ST8SV','ST90CV','ST90SA','ST90TA','ST90TS','ST91CV','ST91SA','ST91TA','ST91TS','ST92SV','ST93CV','ST93SA','ST93TA','ST93TS','ST94CV','ST94SA','ST94TA','ST94TS','ST95CV','ST95SA','ST95TA','ST95TS','ST96SV','ST97CV','ST97SA','ST97TA','ST97TS','ST98CV','ST98SA','ST98TA','ST98TS','ST99CV','ST99SA','ST99TA','ST99TS','ST9SV'};
D3_cols = horzcat(D3_cols,strcat(UCSCFFSX_cols,'_UCSFFSX_11_02_15_UCSFFSX51_08_01_16'));
table_D3 = table_D2(D3_rows,D3_cols);

table_D3.years_endOfADNI2 = table_D2_targetVariablesOnly.t(D3_rows);

%% Write table to CSV spreadsheet
if writeTables
  writetable(table_D3 ,fullfile(dataSaveLocation,'TADPOLE_D3_completeVisit.csv'))
end

%% How to limit D3 to being within a maximum time from the end of ADNI2
%{
D3_maxYears_endOfADNI2 = 3.6;
table_D3_ = table_D3(abs(table_D3.years_endOfADNI2)<D3_maxYears_endOfADNI2,:);
fprintf('Window = %g years. N = %i\n',D3_maxYears_endOfADNI2,height(table_D3_))
writetable(table_D3_ ,fullfile(dataSaveLocation,sprintf('TADPOLE_D3_completeVisit_max%gYearsBeforeADNI2End.csv',D3_maxYears_endOfADNI2)))
%}

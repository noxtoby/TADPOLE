% TADPOLE_SimpleForecastExampleFPC02_Leaderboard.m
%
% Leaderboard submission test using linear regression on ADAS13 and VentVol.
%
%============
% Date:
%   10 September 2017
% Authors: 
%   Daniel C. Alexander
%   University College London

% Script is not ready yet!! (as of 31 Oct 2017)

%% Read in the TADPOLE data set and extract a few columns of salient information.
% Script requires that TADPOLE_D1_D2.csv is in the parent directory. Change if
% necessary
dataLocationD1D2 = '../'; % parent directory
dataLocationLB1LB2 = './';% current directory

tadpoleD1D2File = fullfile(dataLocationD1D2,'TADPOLE_D1_D2.csv');
tadpoleLB1LB2File = fullfile(dataLocationLB1LB2,'TADPOLE_LB1_LB2.csv');
outputFile = 'TADPOLE_Submission_Leaderboard_FPC2.csv';
errorFlag = 0;
if ~(exist(tadpoleD1D2File, 'file') == 2)
  error(sprintf(strcat('File %s does not exist. You need to download\n ',  ... 
  'it from ADNI and/or move it in the right directory'), tadpoleD1D2File))
  errorFlag = 1;
end

if errorFlag
  exit;
end

%* Read in the D1_D2 spreadsheet.
TADPOLE_Table_full = readtable(tadpoleD1D2File,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
% Read in the LB1_LB2 spreadsheet
LB_Table_full = readtable(tadpoleLB1LB2File,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);
tadpoleLB4File = fullfile(dataLocationLB1LB2,'TADPOLE_LB4.csv');
LB4_Table = readtable(tadpoleLB4File,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

% First filter out all entries which are not part of LB1 or LB2 
% (because there are in LB4 and we're not allowed to use them)
LB1LB2Ind = (LB_Table_full.LB1 | LB_Table_full.LB2);
TADPOLE_Table = TADPOLE_Table_full(LB1LB2Ind,:);
LB_Table = LB_Table_full(LB1LB2Ind,:);

% This currently outputs a warning about datetime not being in the right
% format, but the read does work.

%* Target variables: check whether numeric and convert if necessary
targetVariables = {'DX','ADAS13','Ventricles'};
variablesToCheck = [{'RID','ICV_bl'},targetVariables]; % also check RosterID and IntraCranialVolume
for kt=1:length(variablesToCheck)
  if not(strcmpi('DX',variablesToCheck{kt}))
    if iscell(TADPOLE_Table.(variablesToCheck{kt}))
      %* Convert strings (cells) to numeric (arrays)
      TADPOLE_Table.(variablesToCheck{kt}) = str2double(TADPOLE_Table.(variablesToCheck{kt}));
    end
  end
end
%* Copy numeric target variables into arrays. Missing data is encoded as -1
% ADAS13 scores 
ADAS13_Col = TADPOLE_Table.ADAS13;
ADAS13_Col(isnan(ADAS13_Col)) = -1;
% Ventricles volumes, normalised by intracranial volume
Ventricles_Col = TADPOLE_Table.Ventricles;
Ventricles_Col(isnan(Ventricles_Col)) = -1;
ICV_Col = TADPOLE_Table.ICV_bl;
ICV_Col(Ventricles_Col==-1) = 1;
Ventricles_ICV_Col = Ventricles_Col./ICV_Col;
%* Create an array containing the clinical status (current diagnosis DX)
%* column from the spreadsheet
DXCHANGE = TADPOLE_Table.DX; % 'NL to MCI', 'MCI to Dementia', etc. = '[previous DX] to [current DX]'
DX = DXCHANGE; % Note: missing data encoded as empty string
  %* Convert DXCHANGE to current DX, i.e., the final
  for kr=1:length(DXCHANGE)
    spaces = strfind(DXCHANGE{kr},' '); % find the spaces in DXCHANGE
    if not(isempty(spaces))
      DX{kr} = DXCHANGE{kr}((spaces(end)+1):end); % extract current DX
    end
  end
CLIN_STAT_Col = DX;

%* Copy the subject ID column from the spreadsheet into an array.
RID_Col = TADPOLE_Table.RID;
RID_Col(isnan(RID_Col)) = -1; % missing data encoded as -1
RID_Col_full = TADPOLE_Table_full.RID;
RID_Col_full(isnan(RID_Col_full)) = -1; % missing data encoded as -1

%* Compute months since Jan 2000 for each exam date
EXAMDATE = cell2mat(TADPOLE_Table.EXAMDATE);
ExamMonth_Col = zeros(length(TADPOLE_Table.EXAMDATE),1);
for i=1:length(TADPOLE_Table.EXAMDATE)
    ExamMonth_Col(i) = (str2num(TADPOLE_Table.EXAMDATE{i}(1:4))-2000)*12 + str2num(TADPOLE_Table.EXAMDATE{i}(6:7));
end

scanDateLB4 = cell2mat(LB4_Table.ScanDate);
scanDateLB4_Col = zeros(length(LB4_Table.ScanDate),1);
for i=1:length(LB4_Table.ScanDate)
    scanDateLB4_Col(i) = (str2num(LB4_Table.ScanDate{i}(1:4))-2000)*12 + str2num(LB4_Table.ScanDate{i}(6:7));
end


% Copy the column specifying membership of LB1 into an array.
if iscell(LB_Table.LB1)
  LB1_col = str2num(cell2mat(LB_Table.LB1));
else
  LB1_col = LB_Table.LB1;
end

% Copy the column specifying membership of LB2 into an array.
if iscell(LB_Table.LB2)
  LB2_col = str2num(cell2mat(LB_Table.LB2));
else
  LB2_col = LB_Table.LB2;
end

% Copy the column specifying membership of LB1 into an array.
if iscell(LB_Table_full.LB1)
  LB1_col_full = str2num(cell2mat(LB_Table_full.LB1));
else
  LB1_col_full = LB_Table_full.LB1;
end

% Copy the column specifying membership of LB2 into an array.
if iscell(LB_Table_full.LB2)
  LB2_col_full = str2num(cell2mat(LB_Table_full.LB2));
else
  LB2_col_full = LB_Table_full.LB2;
end


%% Generate the forecast

display('Fitting Gaussian models...');

% Use training LB1 set to estimate mean and variance of ADAS given CN, 
% MCI, AD.
lb1_inds = find(LB1_col);

% Find all LB1 entries that are NL and have ADAS13.
lb1_and_NL_and_ADAS13 = find(strcmp(CLIN_STAT_Col, 'NL') & LB1_col & ADAS13_Col>-1);
% Get the states of the list of ADAS13 scores for these.
NL_ADAS13_mean = mean(ADAS13_Col(lb1_and_NL_and_ADAS13));
NL_ADAS13_std = std(ADAS13_Col(lb1_and_NL_and_ADAS13));

% Similarly get stats for ADAS13 of MCIs.
lb1_and_MCI_and_ADAS13 = find(strcmp(CLIN_STAT_Col, 'MCI') & LB1_col & ADAS13_Col>-1);
MCI_ADAS13_mean = mean(ADAS13_Col(lb1_and_MCI_and_ADAS13));
MCI_ADAS13_std = std(ADAS13_Col(lb1_and_MCI_and_ADAS13));

% And for AD
lb1_and_AD_and_ADAS13 = find(strcmp(CLIN_STAT_Col, 'Dementia') & LB1_col & ADAS13_Col>-1);
AD_ADAS13_mean = mean(ADAS13_Col(lb1_and_AD_and_ADAS13));
AD_ADAS13_std = std(ADAS13_Col(lb1_and_AD_and_ADAS13));


display('Generating forecast ...')

%* Get the list of subjects to forecast from LB1_2 - the ordering is the
%* same as in the submission template.
lbInds = find(LB2_col);
LB2_SubjList = unique(RID_Col(lbInds));
N_LB2 = length(LB2_SubjList);

% As opposed to the proper submission, we require 84 months of forecast
% data. This is because some ADNI2 subjects from LB4 have visits even 6-7 years
% after their last ADNI1 visit from LB2.
%* Create arrays to contain the 84 monthly forecasts for each D2 subject
nForecasts = 7*12; % forecast 7 years (84 months).
% 1. Clinical status forecasts
%    i.e. relative likelihood of NL, MCI, and Dementia (3 numbers)
CLIN_STAT_forecast = zeros(N_LB2, nForecasts, 3);
% 2. ADAS13 forecasts 
%    (best guess, upper and lower bounds on 50% confidence interval)
ADAS13_forecast = zeros(N_LB2, nForecasts, 3);
% 3. Ventricles volume forecasts 
%    (best guess, upper and lower bounds on 50% confidence interval)
Ventricles_ICV_forecast = zeros(N_LB2, nForecasts, 3);

%* For this simple forecast, we will simply use the most recent exam of
%* each type from each D2 subject and base the forecast on that.
most_recent_CLIN_STAT = cell(N_LB2, 1);
most_recent_ADAS13 = zeros(N_LB2, 1);
most_recent_Ventricles_ICV = zeros(N_LB2, 1);

display_info = 1; % Useful for checking and debugging (see below)

%*** Some defaults where data is missing
%* Ventricles
  % Missing data = typical volume +/- broad interval = 25000 +/- 20000
Ventricles_typical = 25000;
Ventricles_broad_50pcMargin = 20000; % +/- (broad 50% confidence interval)
  % Default CI = 1000
Ventricles_default_50pcMargin = 1000; % +/- (broad 50% confidence interval)
  % Convert to Ventricles/ICV via linear regression
lm = fitlm(Ventricles_Col(Ventricles_Col>0),Ventricles_ICV_Col(Ventricles_Col>0));
Ventricles_ICV_typical = predict(lm,Ventricles_typical);
Ventricles_ICV_broad_50pcMargin = abs(predict(lm,Ventricles_broad_50pcMargin) - predict(lm,-Ventricles_broad_50pcMargin))/2;
Ventricles_ICV_default_50pcMargin = abs(predict(lm,Ventricles_default_50pcMargin) - predict(lm,-Ventricles_default_50pcMargin))/2;
%* ADAS13
ADAS13_typical = 12;
ADAS13_typical_lower = ADAS13_typical - 10;
ADAS13_typical_upper = ADAS13_typical + 10;

% Need forecasts starting from Feb 2010 and up to Jan 2017. Those are
% months 125 to 208 (from Jan 2000).
monthsToForecastInd = 125:208;



% ADAS13 - response (Y)
% AGE at visit - predictor (X)

% try solving Y = Xb, 
Y = ADAS13_Col;
nrVisits = size(Y,1);
unqSubj = unique(RID_Col);
nrUnqSubj = length(unqSubj);
X = zeros(nrVisits, 2+nrUnqSubj);

X(:,1) = 1;
X(:,2) = TADPOLE_Table.AGE;

% Estimate the age at scan for every subject visit, since the AGE column
% only contains the age at baseline visit
for s=1:nrUnqSubj
  % Find the most recent exam for this subject
  subj_rows = RID_Col == unqSubj(s);
  subj_exam_dates = ExamMonth_Col(subj_rows);
  m = min(subj_exam_dates);
  yearsDiff = (subj_exam_dates - m)/12;
  unqSubj(s)
  
  %X(subj_rows,2)
  assert(min(X(subj_rows,2)) == max(X(subj_rows,2)))
  X(subj_rows,2) = X(subj_rows,2) + yearsDiff;
  %X(subj_rows,2)
  
  % also map the entries in the design matrix corresponding to individual
  % subjects
  X(subj_rows, s+2) = 1;
end

beta = pinv(X'*X)*X'*Y;
Yhat = X*beta;
unqRIDsBeta = [-1; -1; unqSubj];

XpredAge = ones(N_LB2 * nForecasts, 2);
for i=1:N_LB2
 subj_rows = find(RID_Col==LB2_SubjList(i) & LB2_col);
 subj_exam_dates = ExamMonth_Col(subj_rows);
 m = min(subj_exam_dates);
 yearsDiff = (monthsToForecastInd - m)/12;
 
 XpredAgeCurr = TADPOLE_Table.AGE(subj_rows(1)) + yearsDiff;
 XpredAgeCurr = [ones(size(XpredAgeCurr)), XpredAgeCurr];
 
 Ypred = XpredAgeCurr * [beta(1:2); beta(unqRIDsBeta == LB2_SubjList(i))];
end

for i=1:N_LB2
    
    % Find the most recent exam for this subject
    subj_rows = find(RID_Col==LB2_SubjList(i) & LB2_col);
    subj_exam_dates = ExamMonth_Col(subj_rows);
    [a, b] = sort(subj_exam_dates);
    most_recent_exam_ind = subj_rows(max(b));
    
    subj_rows_lb4 = find(LB4_Table.RID == LB2_SubjList(i) );
    
    %* Identify most recent data
    % 1. Clinical status
    exams_with_CLIN_STAT = [];
    for j=1:length(subj_rows)
        if(~isempty(CLIN_STAT_Col{subj_rows(j)}))
            exams_with_CLIN_STAT = [exams_with_CLIN_STAT j];
        end
    end
    if(~isempty(exams_with_CLIN_STAT))
        [a, b] = max(subj_exam_dates(exams_with_CLIN_STAT));
        ind = subj_rows(exams_with_CLIN_STAT(b)); % Index of most recent visit that has an ADAS13 score
        most_recent_CLIN_STAT{i} = CLIN_STAT_Col(ind);
    end
    % 2. ADAS13 score
    exams_with_ADAS13 = find(ADAS13_Col(subj_rows)>0);
    ADAS13_Preds = zeros(84,1);
    if(length(exams_with_ADAS13)>=2)
        % Linearly regress ADAS13 against month for this subject
        M = [subj_exam_dates(exams_with_ADAS13)'; ones(1,length(exams_with_ADAS13))]';
        A = ADAS13_Col(subj_rows(exams_with_ADAS13));
        X = M\A;
        % Need forecasts starting from May 2010 and up to April 2017. Those are
        % stored in monthsToForecastInd.
        ADAS13_Preds = [monthsToForecastInd; ones(1,84)]'*X;

    else
        display(['Number of ADAS13: ' length(exams_with_ADAS13) '. Subject: ' LB2_SubjList(i)]);
    end
    
    ADAS13_forecast(i,:,1) = max([zeros(length(ADAS13_Preds),1), ADAS13_Preds]')';
    ADAS13_forecast(i,:,2) = max([zeros(length(ADAS13_Preds),1), ADAS13_Preds-1]')'; % Set to zero if best-guess less than 1.
    ADAS13_forecast(i,:,3) = ADAS13_forecast(i,:,1)+1;

    % 3. Most recent Ventricles volume
    exams_with_ventsv = find(Ventricles_ICV_Col(subj_rows)>0);
    ventsv_Preds = zeros(84,1);
    if(length(exams_with_ventsv)>=2)
        % Linearly regress ventsv against month for this subject
        M = [subj_exam_dates(exams_with_ventsv)'; ones(1,length(exams_with_ventsv))]';
        A = Ventricles_ICV_Col(subj_rows(exams_with_ventsv));
        X = M\A;
        ventsv_Preds = [125:208; ones(1,84)]'*X;

    else
        display(['Number of ventsv: ' length(exams_with_ventsv) '. Subject: ' LB2_SubjList(i)]);
    end
    
    Ventricles_ICV_forecast(i,:,1) = ventsv_Preds;
    Ventricles_ICV_forecast(i,:,2) = ventsv_Preds - Ventricles_ICV_default_50pcMargin;
    Ventricles_ICV_forecast(i,:,3) = ventsv_Preds + Ventricles_ICV_default_50pcMargin;
        
    %* Construct status forecast
    % Estimate probabilities from ADAS13 score alone.
    NL_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), NL_ADAS13_mean, NL_ADAS13_std);
    MCI_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), MCI_ADAS13_mean, MCI_ADAS13_std);
    AD_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), AD_ADAS13_mean, AD_ADAS13_std);
    
    CLIN_STAT_forecast(i,:,1) = NL_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13);
    CLIN_STAT_forecast(i,:,2) = MCI_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13);
    CLIN_STAT_forecast(i,:,3) = AD_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13); 
        
    %* Print out some stuff if in debug mode (set display_info=1 above).
    if(display_info)
        ExamMonth_Col(subj_rows)'
        CLIN_STAT_Col(subj_rows)'
        Ventricles_ICV_Col(subj_rows)'
        ADAS13_Col(subj_rows)'
        [i squeeze(CLIN_STAT_forecast(i,1,1:3))' squeeze(Ventricles_ICV_forecast(i,1,1:3))' squeeze(ADAS13_forecast(i,1,1:3))']
    end
    
    % compute mixed effects predictions

    
    % plot ADAS13
    figure(1)
    clf
    scatter(subj_exam_dates(exams_with_ADAS13)', ADAS13_Col(subj_rows(exams_with_ADAS13)),30,'magenta');
    hold on
    plot(monthsToForecastInd,ADAS13_forecast(i,:,1));
    hold on
    scatter(scanDateLB4_Col(subj_rows_lb4),LB4_Table.ADAS13(subj_rows_lb4),30,'blue')  
    
    % plot Ventricles
    figure(2)
    clf
    scatter(subj_exam_dates(exams_with_ventsv)', Ventricles_ICV_Col(subj_rows(exams_with_ventsv)),30,'magenta');
    hold on
    plot(monthsToForecastInd,Ventricles_ICV_forecast(i,:,1));
    hold on
    scatter(scanDateLB4_Col(subj_rows_lb4),LB4_Table.Ventricles(subj_rows_lb4),30,'blue')  
    
end



tbl = table(X(:,12),X(:,14),X(:,24),'VariableNames',{'Horsepower','CityMPG','EngineType'});


%% Now construct the forecast spreadsheet and output it.
display(sprintf('Constructing the output spreadsheet %s ...', outputFile))
startDate = datenum('01-May-2010');

submission_table =  cell2table(cell(N_LB2*nForecasts,12), ...
  'VariableNames', {'RID', 'ForecastMonth', 'ForecastDate', ...
  'CNRelativeProbability', 'MCIRelativeProbability', 'ADRelativeProbability', ...
  'ADAS13', 'ADAS1350_CILower', 'ADAS1350_CIUpper', ...
  'Ventricles_ICV', 'Ventricles_ICV50_CILower', 'Ventricles_ICV50_CIUpper' });
%* Repeated matrices - compare with submission template
submission_table.RID = reshape(repmat(LB2_SubjList, [1, nForecasts])', N_LB2*nForecasts, 1);
submission_table.ForecastMonth = repmat((1:nForecasts)', [N_LB2, 1]);
%* First subject's submission dates
for m=1:nForecasts
  submission_table.ForecastDate{m} = datestr(addtodate(startDate, m-1, 'month'), 'yyyy-mm');
end
%* Repeated matrices for submission dates - compare with submission template
submission_table.ForecastDate = repmat(submission_table.ForecastDate(1:nForecasts), [N_LB2, 1]);

%* Pre-fill forecast data, encoding missing data as NaN
nanColumn = nan(size(submission_table.CNRelativeProbability));
submission_table.CNRelativeProbability = nanColumn;
submission_table.MCIRelativeProbability = nanColumn;
submission_table.ADRelativeProbability = nanColumn;
submission_table.ADAS13 = nanColumn;
submission_table.ADAS1350_CILower = nanColumn;
submission_table.ADAS1350_CIUpper = nanColumn;
submission_table.Ventricles_ICV = nanColumn;
submission_table.Ventricles_ICV50_CILower = nanColumn;
submission_table.Ventricles_ICV50_CIUpper = nanColumn;

%*** Paste in month-by-month forecasts **
%* 1. Clinical status
  %*  a) CN probabilities
col = 4;
t = CLIN_STAT_forecast(:,:,1)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
  %*  b) MCI probabilities
col = 5;
t = CLIN_STAT_forecast(:,:,2)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
  %*  c) AD probabilities
col = 6;
t = CLIN_STAT_forecast(:,:,3)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
%* 2. ADAS13 score
col = 7;
t = ADAS13_forecast(:,:,1)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
  %*  a) Lower and upper bounds (50% confidence intervals)
col = 8;
t = ADAS13_forecast(:,:,2)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
col = 9;
t = ADAS13_forecast(:,:,3)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
%* 3. Ventricles volume (normalised by intracranial volume)
col = 10;
t = Ventricles_ICV_forecast(:,:,1)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
  %*  a) Lower and upper bounds (50% confidence intervals)
col = 11;
t = Ventricles_ICV_forecast(:,:,2)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
col = 12;
t = Ventricles_ICV_forecast(:,:,3)';
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

%* Convert all numbers to strings
hdr = submission_table.Properties.VariableNames;
for k=1:length(hdr)
  if ~iscell(submission_table.(hdr{k}))
    %submission_table{1:10,hdr{k}} = varfun(@num2str,submission_table{1:10,hdr{k}},'OutPutFormat','cell');
    submission_table.(hdr{k}) = strrep(cellstr(num2str(submission_table{:,hdr{k}})),' ','');
  end
end

%* Use column names that match the submission template
columnNames = {'RID', 'Forecast Month', 'Forecast Date',...
'CN relative probability', 'MCI relative probability', 'AD relative probability',	...
'ADAS13',	'ADAS13 50% CI lower', 'ADAS13 50% CI upper', 'Ventricles_ICV', ...
'Ventricles_ICV 50% CI lower',	'Ventricles_ICV 50% CI upper'};
%* Convert table to cell array to write to file, line by line
%  This is necessary because of spaces in the column names: writetable()
%  doesn't handle this.
tableCell = table2cell(submission_table);
tableCell = [columnNames;tableCell];
%* Write file line-by-line
fid = fopen(outputFile,'w');
for i=1:size(tableCell,1)
  fprintf(fid,'%s\n', strjoin(tableCell(i,:), ','));
end
fclose(fid);


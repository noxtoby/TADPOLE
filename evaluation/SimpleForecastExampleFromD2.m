% Example code showing how to construct a forecast in the right format from
% the D3 prediction set. The forecast just uses a set of predefined
% likelihoods of each class (CN, MCI, AD) that depend on the subject's
% most recent clinical status. Forecasts of future ADAS13 and ventricles
% volume are just that they are unchanged from the most recent measurement.
% The purpose of the code is not to give a good forecast! It is simply to
% show how to read in and make sense of the TADPOLE data sets and to output
% a forecase in the right format.

%% Read in the TADPOLE data set and extract a few columns of salient information.
% Script requires that TADPOLE_D1_D2.csv is in the parent directory. Change if
% necessary
dataLocation = '../';


tadpoleD1D2File = fullfile(dataLocation,'TADPOLE_D1_D2.csv');
outputFile = 'TADPOLE_Submission_SimpleForecast1.csv';
errorFlag = 0;
if ~(exist(tadpoleD1D2File, 'file') == 2)
  error(sprintf(strcat('File %s does not exist. You need to download\n ',  ... 
  'it from ADNI and/or move it in the right directory'), tadpoleD1D2File))
  errorFlag = 1;
end

if errorFlag
  exit;
end


% Read in the D1_D2 spreadsheet.
TADPOLE_Table = readtable(tadpoleD1D2File,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

% This currently outputs a warning about datetime not being in the right
% format, but the read does work.

% Copy the subject ID column from the spreadsheet into an array.
if iscell(TADPOLE_Table.RID)
  RID_Col = zeros(length(TADPOLE_Table.RID),1)-1;
  for i=1:length(TADPOLE_Table.RID)
    RID_Col(i) = str2num(TADPOLE_Table.RID{i});
  end
else
  RID_Col = TADPOLE_Table.RID;
end

% Create an array containing the clinical status column from the spreadsheet
CLIN_STAT_Col = TADPOLE_Table.DX_bl;

% Compute months since Jan 2000 for each exam date
EXAMDATE = cell2mat(TADPOLE_Table.EXAMDATE);
ExamMonthCol = zeros(length(TADPOLE_Table.EXAMDATE),1);
for i=1:length(TADPOLE_Table.EXAMDATE)
    ExamMonthCol(i) = (str2num(TADPOLE_Table.EXAMDATE{i}(1:4))-2000)*12 + str2num(TADPOLE_Table.EXAMDATE{i}(6:7));
end

% Copy the column specifying membership of D2 into an array.
if iscell(TADPOLE_Table.D2)
  D2_col = str2num(cell2mat(TADPOLE_Table.D2));
else
  D2_col = TADPOLE_Table.D2;
end

% Copy the ADAS13 scores column into an array; if the data point is missing
% the array contains -1.
if iscell(TADPOLE_Table.ADAS13)
  ADAS13_Col = zeros(length(TADPOLE_Table.ADAS13),1)-1;
  for i=1:length(TADPOLE_Table.ADAS13)
    if(~isempty(TADPOLE_Table.ADAS13{i}))
      ADAS13_Col(i) = str2num(TADPOLE_Table.ADAS13{i});
    end
  end
else
  ADAS13_Col = TADPOLE_Table.ADAS13;
  ADAS13_Col(isnan(ADAS13_Col)) = -1;
end

% Copy the ventricle volumes column into an array; if the data point is missing
% the array contains -1.
if iscell(TADPOLE_Table.Ventricles)
  VentriclesCol = zeros(length(TADPOLE_Table.Ventricles),1)-1;
  for i=1:length(TADPOLE_Table.Ventricles)
    if(~isempty(TADPOLE_Table.Ventricles{i}))
      VentriclesCol(i) = str2num(TADPOLE_Table.Ventricles{i});
    end
  end
else
  VentriclesCol = TADPOLE_Table.Ventricles;
  VentriclesCol(isnan(VentriclesCol)) = -1;
end


%% Generate the very simple forecast

display('Generating forecast ...')
% Get the list of subjects to forecast from D1_D2 - the ordering is the
% same as in the submission template.
d2inds = find(D2_col);
D2_SubjList = unique(RID_Col(d2inds));

% Create an array to contain the clinical status forecasts, i.e. relative
% likelihood of CN, MCI, and AD (3 numbers), at each of 60 months for each
% D2 subject.
status_forecast = zeros(length(D2_SubjList), 60, 3);
% Similar array for monthly ADAS13 forecasts (best guess, upper and lower
% bounds on 50% confidence interval).
ADAS13_forecast = zeros(length(D2_SubjList), 60, 3);
% Similar array for monthly ventricle volume forecasts (best guess, upper and lower
% bounds on 50% confidence interval).
ventsv_forecast = zeros(length(D2_SubjList), 60, 3);

% For this simple forecast, we will simply use the most recent exam of each
% type from each D2 subject and base the forecast on that.
most_recent_status = cell(length(D2_SubjList), 1);
most_recent_ADAS13 = zeros(length(D2_SubjList), 1);
most_recent_ventsv = zeros(length(D2_SubjList), 1);

display_info = 0;

for i=1:length(D2_SubjList)
    
    % Find the most recent exam for this subject
    subj_rows = find(RID_Col==D2_SubjList(i));
    subj_exam_dates = ExamMonthCol(subj_rows);
    [a, b] = sort(subj_exam_dates);
    most_recent_exam_ind = subj_rows(max(b));
    
    % Identify most recent clinical status, ADAS score, and vents volume.
    most_recent_status{i} = CLIN_STAT_Col(most_recent_exam_ind);
    % Most recent ADAS13 score
    exams_with_ADAS13 = find(ADAS13_Col(subj_rows)>0);
    if(~isempty(exams_with_ADAS13))
        [a, b] = max(subj_exam_dates(exams_with_ADAS13));
        ind = subj_rows(exams_with_ADAS13(b)); % Index of most recent visit that has an ADAS13 score
        most_recent_ADAS13(i) = ADAS13_Col(ind);
    else
        % The subjcet has no ADAS13 scores in the data set.
        most_recent_ADAS13(i) = -1;
    end
    
    % Most recent ventricle volume
    exams_with_ventsv = find(VentriclesCol(subj_rows)>0);
    if(~isempty(exams_with_ventsv))
        [a, b] = max(subj_exam_dates(exams_with_ventsv));
        ind = subj_rows(exams_with_ventsv(b)); % Index of most recent visit that has a ventricle volume
        most_recent_ventsv(i) = VentriclesCol(ind);
    else
        % The subject has no ventricle volume measurement in the data set.
        most_recent_ventsv(i) = -1;
    end
    
    % Print out some stuff if in debug mode (set display_info=1 above).
    if(display_info)
        CLIN_STAT_Col(subj_rows)
        ExamMonthCol(subj_rows)
        VentriclesCol(subj_rows)
        ADAS13_Col(subj_rows)
        [i most_recent_status{i} most_recent_ADAS13(i) most_recent_ventsv(i)]
    end
    
    % Construct status forecast using predefined likelihoods for each
    % current status.
    if(strcmp(most_recent_status{i}, 'CN'))
        CNp=0.75;
        MCIp=0.15;
        ADp=0.1;
    elseif(strcmp(most_recent_status{i}, 'SMC'))
        CNp=0.55;
        MCIp=0.25;
        ADp=0.2;
    elseif(strcmp(most_recent_status{i}, 'EMCI'))
        CNp=0.25;
        MCIp=0.5;
        ADp=0.25;
    elseif(strcmp(most_recent_status{i}, 'LMCI'))
        CNp=0.1;
        MCIp=0.5;
        ADp=0.4;
    elseif(strcmp(most_recent_status{i}, 'AD'))
        CNp=0.1;
        MCIp=0.1;
        ADp=0.8;
    else
        disp(['Unrecognised status '; most_recent_status{i}])
        CNp=0.33;
        MCIp=0.33;
        ADp=0.34;
    end

    status_forecast(i,:,1) = CNp;
    status_forecast(i,:,2) = MCIp;
    status_forecast(i,:,3) = ADp;

    
    % Construct ADAS13 forecast - copy the most recent score and use a
    % default confidence interval.
    if(most_recent_ADAS13(i)>=0)
        ADAS13_forecast(i,:,1) = most_recent_ADAS13(i);
        ADAS13_forecast(i,:,2) = max([0, most_recent_ADAS13(i)-1]); % Set to zero if best-guess less than 1.
        ADAS13_forecast(i,:,3) = most_recent_ADAS13(i)+1;
    else
        % Subject has no history of ADAS13 measurement, so we'll take a
        % typical score of 12 with wide confidence interval +/-10.
        ADAS13_forecast(i,:,1) = 12;
        ADAS13_forecast(i,:,2) = 2;
        ADAS13_forecast(i,:,3) = 22;
    end    
    
    % Construct ventricle volume forecast - copy the most recent
    % measurement and use a default confidence interval.
    if(most_recent_ventsv(i)>0)
        ventsv_forecast(i,:,1) = most_recent_ventsv(i);
        ventsv_forecast(i,:,2) = most_recent_ventsv(i)-1000;
        ventsv_forecast(i,:,3) = most_recent_ventsv(i)+1000;
    else
        % Subject has no imaging history, so we'll take a typical ventricle
        % volume of 25000 with wide confidence interval +/-20000.
        ventsv_forecast(i,:,1) = 25000;
        ventsv_forecast(i,:,2) = 5000;
        ventsv_forecast(i,:,3) = 45000;
    end    
        
end



%% Now construct the forecast spreadsheet and output it.

display(sprintf('Constructing the output spreadsheet %s...', outputFile))
nrRIDs = length(D2_SubjList);
nrMonthsToForecast = 5*12; % forecast 5 years (60 months).

submission_table =  cell2table(cell(nrRIDs*nrMonthsToForecast,12), 'VariableNames', {'RID', ...
'ForecastMonth', 'ForecastDate', 'CNRelativeProbability', ...
'MCIRelativeProbability', 'ADRelativeProbability', 'ADAS13', ...
'ADAS1350_CILower', 'ADAS1350_CIUpper', 'Ventricles_ICV', ...
'Ventricles_ICV50_CILower', 'Ventricles_ICV50_CIUpper' });

RIDrep = reshape(repmat(D2_SubjList, [1, nrMonthsToForecast])', ...
nrRIDs*nrMonthsToForecast, 1);

submission_table.RID = RIDrep(:);

startDate = datenum('01-Jan-2018');

submission_table.ForecastMonth = repmat((1:nrMonthsToForecast)', ...
[nrRIDs, 1]);
for m=1:nrMonthsToForecast
  submission_table.ForecastDate{m} = ...
  datestr(addtodate(startDate, m-1, 'month'), 'yyyy-mm');
end
submission_table.ForecastDate = repmat(...
submission_table.ForecastDate(1:nrMonthsToForecast), [nrRIDs, 1]);


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



% Paste in month-by-month CN probabilities
col = 4;
t = status_forecast(:,:,1)';
% submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
% Paste in month-by-month MCI probabilities
col = 5;
t = status_forecast(:,:,2)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
% Paste in month-by-month AD probabilities
col = 6;
t = status_forecast(:,:,3)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

% Paste in best-guess ADAS13 estimates
col = 7;
t = ADAS13_forecast(:,:,1)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
% Paste in upper and lower bounds of ADAS13 50% confidence intervals
col = 8;
t = ADAS13_forecast(:,:,2)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

col = 9;
t = ADAS13_forecast(:,:,3)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

% Paste in best-guess ventricle volume estimates
col = 10;
t = ventsv_forecast(:,:,1)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);
% Paste in upper and lower bounds of ventricle volume 50% confidence intervals
col = 11;
t = ventsv_forecast(:,:,2)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

col = 12;
t = ventsv_forecast(:,:,3)';
%submission(:,col) = t(:);
col = submission_table.Properties.VariableNames(col);
submission_table{:,col} = t(:);

columnNames = {'RID', 'Forecast Month', 'Forecast Date',...
'CN relative probability', 'MCI relative probability', 'AD relative probability',	...
'ADAS13',	'ADAS13 50% CI lower', 'ADAS13 50% CI upper', 'Ventricles_ICV', ...
'Ventricles_ICV 50% CI lower',	'Ventricles_ICV 50% CI upper'};

tableCell = table2cell(submission_table);
tableCell = [columnNames;tableCell];

% convert all numbers to strings
for i=1:size(tableCell,1)
  for j=1:size(tableCell,2)
    if ~isstr(tableCell{i,j})
      x = tableCell(i,j);
      tableCell{i,j} = num2str(x{1});
    end
  end
end
    
%# write file line-by-line
fid = fopen(outputFile,'w');
for i=1:size(tableCell,1)
  fprintf(fid,'%s\n', strjoin(tableCell(i,:), ','));
end
fclose(fid);
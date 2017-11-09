% TADPOLE_Leaderboard_BenchmarkMixedEffectsCov.m
%
% Leaderboard submission using linear mixed effects model on ADAS13 and VentVol (+ APOE as covariate).
%
% Adapted by Razvan Marinescu from Daniel Alexander's SimpleForecastFPC02_Leaderboard.m script
%============
% Date:
%   10 September 2017

%% Read in the TADPOLE data set and extract a few columns of salient information.
% Script requires that TADPOLE_D1_D2.csv is in the parent directory. Change if
% necessary
dataLocationD1D2 = '../'; % parent directory
dataLocationLB1LB2 = './';% current directory

tadpoleD1D2File = fullfile(dataLocationD1D2,'TADPOLE_D1_D2.csv');
tadpoleLB1LB2File = fullfile(dataLocationLB1LB2,'TADPOLE_LB1_LB2.csv');
tadpoleLB4File = fullfile(dataLocationLB1LB2,'TADPOLE_LB4.csv');
outputFile = 'TADPOLE_Submission_Leaderboard_BenchmarkMixedEffectsCov.csv';

[TADPOLE_Table, LB_Table, LB4_Table] = readTadpoleTables(tadpoleD1D2File, tadpoleLB1LB2File, tadpoleLB4File);

[ADAS13_Col, Ventricles_Col, ICV_Col, Ventricles_ICV_Col, CLIN_STAT_Col, ...
  RID_Col, ExamMonth_Col, ~]  = extractSalientColumns(TADPOLE_Table);

[scanDateLB4, LB1_col, LB2_col] = extractSalientColumnsLeaderboard(LB_Table, LB4_Table);

% choose whether to plot the data.
plotDataFlag = 0;

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

display_info = 1; % Useful for checking and debugging (see below)

%*** Some defaults for confidence intervals
Ventricles_ICV_default_50pcMargin = 0.05;
ADAS_default_50pcMargin = 1;

% Need forecasts starting from May 2010 and up to and inlcuding April 2017. Those are
% months 125 to 208 (from Jan 2000).
monthsToForecastInd = 125:208;
predictionStartDate = datenum('01-May-2010');

nrVisits = size(RID_Col,1);
unqSubj = unique(RID_Col);
nrUnqSubj = length(unqSubj);

%% Fit Mixed Effects Model as follows:
% response (Y) -ADAS 13
% design matrix (X) - [1, AgeAtVisit x (APOE=0), AgeAtVisit x (APOE>0), random effects] (1 random parameter per subject)
% Covariates - APOE4 (i.e. fit different slope for APOE=0 and APOE>=1)
% task: solve for beta: Y = Xb, where beta are the linear parameters 
% beta = [intercept, population_slope_APOE=0, population_slope_APOE>0, shift_subj_1, shift_subj_2, ...]
% fixed parameters: intercept, population_slope_APOE=0, population_slope_APOE>0
% random parameters: shift_subj_1, shift_subj_2, ...
% there is actually one extra degree of freedom (first parameter is unnecessary, but predictions should still be the same)

nrFixedParams = 3;
nrRandomParams = nrUnqSubj;

% Build the design matrix X
Xfull = zeros(nrVisits, nrFixedParams+nrRandomParams);

Xfull(:,1) = 1;
Xfull(:,2) = 0;
Xfull(:,3) = 0;

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
  assert(min(TADPOLE_Table.AGE(subj_rows)) == max(TADPOLE_Table.AGE(subj_rows)))
  Xfull(subj_rows,2) = TADPOLE_Table.AGE(subj_rows) + yearsDiff;
  %X(subj_rows,2)
  Xfull(subj_rows,3) = TADPOLE_Table.AGE(subj_rows) + yearsDiff;
  
  % also map the entries in the design matrix corresponding to individual
  % subjects
  Xfull(subj_rows, s+nrFixedParams) = 1;
end

Xfull(:,2) = Xfull(:,2) .* (TADPOLE_Table.APOE4 == 0);
Xfull(:,3) = Xfull(:,3) .* (TADPOLE_Table.APOE4 > 0);

Yadas = ADAS13_Col;
filterMaskADAS = (Yadas ~= -1) & (~isnan(Xfull(:,3)));
YadasFilt = Yadas(filterMaskADAS);
Xadas = Xfull(filterMaskADAS,:);

% Solve for beta using the Moore-Penrose pseudoinverse: b = (X'X)^{-1}X'Y
betaADAS = pinv(Xadas'*Xadas)*Xadas'*YadasFilt;
unqRIDsBeta = [-1*ones(nrFixedParams,1); unqSubj];

Yvents = Ventricles_ICV_Col;
filterMaskVents = (Yvents ~= -1) & (~isnan(Yvents)) & (~isnan(Xfull(:,3)));
YventsFilt = Yvents(filterMaskVents);
Xvents = Xfull(filterMaskVents,:);
betaVents = pinv(Xvents'*Xvents)*Xvents'*YventsFilt;

for i=1:N_LB2
    
    % Find the most recent exam for this subject
    subj_rows = find(RID_Col==LB2_SubjList(i) & LB2_col);
    subj_exam_dates = ExamMonth_Col(subj_rows);

    exams_with_CLIN_STAT = [];
    exams_with_ADAS13 = find(ADAS13_Col(subj_rows)>0);
    exams_with_ventsv = find(Ventricles_ICV_Col(subj_rows)>0);
    
    % compute mixed effects model predictions
    m = min(subj_exam_dates);
    yearsDiff = (monthsToForecastInd - m)/12;
    XpredAgeCurr = (TADPOLE_Table.AGE(subj_rows(1)) + yearsDiff)';
    XpredAgeAPOE0Curr = XpredAgeCurr * (TADPOLE_Table.APOE4(subj_rows(1)) == 0);
    XpredAgeAPOE12Curr =  XpredAgeCurr * (TADPOLE_Table.APOE4(subj_rows(1)) > 0);
    
    % construct design matrix for prediction (current subject only). This
    % is different than the training design matrix, since it contains the age of 
    % current subject at future timepoints, when we
    % need to make the predictions.
    XpredFull = [ones(size(XpredAgeCurr)), XpredAgeAPOE0Curr, XpredAgeAPOE12Curr, ones(size(XpredAgeCurr))];
    ADASpredCurrMixed = XpredFull * [betaADAS(1:nrFixedParams); betaADAS(unqRIDsBeta == LB2_SubjList(i))];
    VentsPredCurrMixed = XpredFull * [betaVents(1:nrFixedParams); betaVents(unqRIDsBeta == LB2_SubjList(i))];
    
    ADAS13_forecast(i,:,1) = ADASpredCurrMixed;
    ADAS13_forecast(i,:,2) = ADASpredCurrMixed - ADAS_default_50pcMargin;
    ADAS13_forecast(i,:,3) = ADASpredCurrMixed + ADAS_default_50pcMargin;
    
    Ventricles_ICV_forecast(i,:,1) = VentsPredCurrMixed;
    Ventricles_ICV_forecast(i,:,2) = VentsPredCurrMixed - Ventricles_ICV_default_50pcMargin;
    Ventricles_ICV_forecast(i,:,3) = VentsPredCurrMixed + Ventricles_ICV_default_50pcMargin;
    
    %* Construct status forecast
    % Estimate probabilities from ADAS13 score alone.
    NL_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), NL_ADAS13_mean, NL_ADAS13_std);
    MCI_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), MCI_ADAS13_mean, MCI_ADAS13_std);
    AD_LikFromADAS13 = normpdf(ADAS13_forecast(i,:,1), AD_ADAS13_mean, AD_ADAS13_std);
    
    CLIN_STAT_forecast(i,:,1) = NL_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13);
    CLIN_STAT_forecast(i,:,2) = MCI_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13);
    CLIN_STAT_forecast(i,:,3) = AD_LikFromADAS13./(NL_LikFromADAS13+MCI_LikFromADAS13+AD_LikFromADAS13); 
    
    if plotDataFlag == 1
      % find subjects in lb4 just for plotting
      subj_rows_lb4 = find(LB4_Table.RID == LB2_SubjList(i) );

      % plot ADAS13
      figure(1)
      clf
      scatter(subj_exam_dates(exams_with_ADAS13)', ADAS13_Col(subj_rows(exams_with_ADAS13)),30,'magenta');
      hold on
      plot(monthsToForecastInd,ADAS13_forecast(i,:,1), 'r', 'LineWidth',2);
      hold on
      scatter(scanDateLB4_Col(subj_rows_lb4),LB4_Table.ADAS13(subj_rows_lb4),30,'blue') 

      % plot Ventricles
      figure(2)
      clf
      scatter(subj_exam_dates(exams_with_ventsv)', Ventricles_ICV_Col(subj_rows(exams_with_ventsv)),30,'magenta');
      hold on
      plot(monthsToForecastInd,Ventricles_ICV_forecast(i,:,1), 'r', 'LineWidth',2);
      hold on
      scatter(scanDateLB4_Col(subj_rows_lb4),LB4_Table.Ventricles(subj_rows_lb4),30,'blue') 
    end
end

writePredictionsToFile(outputFile, nForecasts, N_LB2, LB2_SubjList, ...
  CLIN_STAT_forecast, ADAS13_forecast, Ventricles_ICV_forecast, predictionStartDate);


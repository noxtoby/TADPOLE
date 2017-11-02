function [Ventricles_typical, Ventricles_broad_50pcMargin, Ventricles_default_50pcMargin, ...
  Ventricles_ICV_typical,Ventricles_ICV_broad_50pcMargin, Ventricles_ICV_default_50pcMargin, ADAS13_typical] predModelDefaults()

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

end
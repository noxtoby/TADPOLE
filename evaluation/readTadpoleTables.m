function [TADPOLE_Table, LB_Table, LB4_Table] = readTadpoleTables(tadpoleD1D2File, tadpoleLB1LB2File, tadpoleLB4File)


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


end
function TADPOLE_Table = readTadpoleD1D2(tadpoleD1D2File)
%% Read the TADPOLE table and convert to some columns to numeric arrays
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
TADPOLE_Table = readtable(tadpoleD1D2File,'Delimiter','comma','TreatAsEmpty',{''},'HeaderLines',0);

%* Target variables: check whether numeric and convert if necessary
targetVariables = {'DX','ADAS13','Ventricles'};
variablesToCheck = [{'RID','ICV_bl', 'AGE', 'APOE4'},targetVariables]; % also check RosterID and IntraCranialVolume
for kt=1:length(variablesToCheck)
  if not(strcmpi('DX',variablesToCheck{kt}))
    if iscell(TADPOLE_Table.(variablesToCheck{kt}))
      %* Convert strings (cells) to numeric (arrays)
      TADPOLE_Table.(variablesToCheck{kt}) = str2double(TADPOLE_Table.(variablesToCheck{kt}));
    end
  end
end

end
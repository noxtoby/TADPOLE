function [ADAS13_Col, Ventricles_Col, ICV_Col, Ventricles_ICV_Col, ...
  CLIN_STAT_Col, RID_Col, ExamMonth_Col, AGE_Bl_Col, Viscode_Col, D2_col] = extractSalientColumns(TADPOLE_Table)

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

%* Compute months since Jan 2000 for each exam date
%EXAMDATE = cell2mat(TADPOLE_Table.EXAMDATE);
ExamMonth_Col = zeros(length(TADPOLE_Table.EXAMDATE),1);
for i=1:length(TADPOLE_Table.EXAMDATE)
%    ExamMonth_Col(i) = (str2num(TADPOLE_Table.EXAMDATE{i}(1:4))-2000)*12 + str2num(TADPOLE_Table.EXAMDATE{i}(6:7));
    ExamMonth_Col(i) = (year(TADPOLE_Table.EXAMDATE(i))-2000)*12 + month(TADPOLE_Table.EXAMDATE(i));
end

AGE_Bl_Col = TADPOLE_Table.AGE;
AGE_Bl_Col(isnan(AGE_Bl_Col)) = -1;

Viscode_Col = TADPOLE_Table.VISCODE;

%* Copy the column specifying membership of D2 into an array.
if ismember('D2', TADPOLE_Table.Properties.VariableNames)
  if iscell(TADPOLE_Table.D2)
    D2_col = str2num(cell2mat(TADPOLE_Table.D2));
  else
    D2_col = TADPOLE_Table.D2;
  end
else
  D2_col = nan;
end
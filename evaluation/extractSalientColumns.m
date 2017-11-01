function [ADAS13_Col, Ventricles_Col, ICV_Col, Ventricles_ICV_Col, ...
  CLIN_STAT_Col, RID_Col, ExamMonth_Col, scanDateLB4, LB1_col, LB2_col] = extractSalientColumns(TADPOLE_Table, LB_Table, LB4_Table)

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

end
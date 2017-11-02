function [scanDateLB4, LB1_col, LB2_col] = extractSalientColumnsLeaderboard(LB_Table, LB4_Table)

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
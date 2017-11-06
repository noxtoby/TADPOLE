function [TADPOLE_Table, LB_Table, LB4_Table] = readTadpoleTables(tadpoleD1D2File, tadpoleLB1LB2File, tadpoleLB4File)
%% Read TADPOLE_D1_D2 table and also the leaderboard tables

TADPOLE_Table_full = readTadpoleD1D2(tadpoleD1D2File);

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

end
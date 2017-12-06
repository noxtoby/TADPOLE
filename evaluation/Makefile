# change this to the matlab path on your computer
#MATLAB_PATH = /usr/local/bin/matlab
#MATLAB_PATH = ~/programs/MATLAB/bin/matlab
MATLAB_PATH = /Applications/MATLAB_R2015b.app/bin/matlab

######## pipeline for generating and evaluating a valid TADPOLE submission ###########
eval:
	# First save TADPOLE_D1_D2.csv in the parent directory
	# NOTE: Change the Matlab path above as required. Otherwise load the script manually in MATLAB and run it.

	# Generate a simple forecast from D2 and save it as TADPOLE_Submission_TeamName1.csv ...
	# In TADPOLE_SimpleForecastExample.m, you should replace TeamName1 with your team name and submission index, e.g., TADPOLE_Submission_TeamAwesome3.csv
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExample; exit";

	# Then make a dummy D4 dataset, which would be similar in format to the real D4
	python3 makeDummyD4.py;

	# Evaluate the user forecasts from TADPOLE_Submission_TeamName1.csv against D4_dummy.csv using the evaluation function
	# Be sure to change the spreadsheet filename here to match the one in TADPOLE_SimpleForecastExample.m (e.g. as above: TADPOLE_Submission_TeamAwesome3.csv)
	python3 evalOneSubmission.py --d4File D4_dummy.csv --forecastFile TADPOLE_Submission_TeamName1.csv;

########### pipeline for generating and evaluating a leaderboard submission ##########
leaderboard:
	# First generate the leaderboard datasets LB1, LB2 and LB4 and the submission skeleton
	python3 makeLeaderboardDataset.py;

	# Then generate a simple forecast from LB2, and save it as TADPOLE_Submission_Leaderboard_TeamName1.csv ...
	# In TADPOLE_SimpleForecastExampleLeaderboard.m, you should replace TeamName1 with your team name and submission index, e.g., TADPOLE_Submission_Leaderboard_TeamAwesome3.csv
	# NOTE: Change the Matlab path above as required. Otherwise load the TADPOLE_SimpleForecastExampleLeaderboard.m script manually in MATLAB and run it.
	# If the MATLAB script doesn't run, try the equivalent Python script: TADPOLE_SimpleForecastExampleLeaderboard.py
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExampleLeaderboard; exit";

	# Evaluate the user forecasts from TADPOLE_Submission_Leaderboard_TeamName1.csv against TADPOLE_LB4.csv using the evaluation function
	python3 evalOneSubmission.py --leaderboard --d4File TADPOLE_LB4.csv --forecastFile TADPOLE_Submission_Leaderboard_TeamName1.csv;

	# Submit (renamed version of) TADPOLE_Submission_Leaderboard_TeamName1.csv to TADPOLE website via the Submit page

clear:
	rm -f D4_dummy.csv TADPOLE_LB1_LB2.csv TADPOLE_Submission_TeamName1.csv TADPOLE_LB4.csv TADPOLE_Submission_Leaderboard_TeamName1.csv leaderboard_table.html





###### DEVELOPERS ONLY ##########

copyToPublicRepo:
	cp evalOneSubmission.py leaderboardRunAll.py TADPOLE_SimpleForecastExample.m makeDummyD4.py makeLeaderboardDataset.py TADPOLE_SimpleForecastExampleLeaderboard.m MAUC.py Makefile ../neil_repo/evaluation

# fast processing uses previously compured results, which are saved in a file. Only adds new or missing submissions. If a submission is deleted from Dropbox, it will still show up in the leaderboard. Use the slow method to fully remove it.
procLeaderboardFast:
	python3 leaderboardRunAll.py --runPart RR

# slow processing runs all the submissions. Run this only if submissions are deleted
procLeaderboardSlow:
	python3 leaderboardRunAll.py --runPart RR --fast 0

# change this to the matlab path on your computer
#MATLAB_PATH = /usr/local/bin/matlab
#MATLAB_PATH = ~/programs/MATLAB/bin/matlab
MATLAB_PATH = /Applications/MATLAB_R2015b.app/bin/matlab

######## pipeline for generating and evaluating a valid TADPOLE submission ###########
eval:
	# First save TADPOLE_D1_D2.csv in the parent directory
	# NOTE: Change the Matlab path above as required. Otherwise load the script manually in MATLAB and run it.

	# Generate a simple forecast from D2 and save it as TADPOLE_Submission_SimpleForecast1.csv ...
	# In TADPOLE_SimpleForecastExample.m, you should replace SimpleForecast1 with your team name and submission index, e.g., TADPOLE_Submission_TeamAwesome3.csv
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExample; exit";

	# Then make a dummy D4 dataset, which would be similar in format to the real D4
	python3 makeDummyD4.py;

	# Evaluate the user forecasts from TADPOLE_Submission_SimpleForecast1.csv against D4_dummy.csv using the evaluation function
	# Be sure to change the spreadsheet filename here to match the one in TADPOLE_SimpleForecastExample.m (e.g. as above: TADPOLE_Submission_TeamAwesome3.csv)
	python3 evalOneSubmission.py --d4File D4_dummy.csv --forecastFile TADPOLE_Submission_SimpleForecast1.csv;

########### pipeline for generating and evaluating a leaderboard submission ##########
leaderboard:
	# First generate the leaderboard datasets LB1, LB2 and LB4 and the submission skeleton
	python3 makeLeaderboardDataset.py;

	# Then generate a simple forecast from LB2, and save it as TADPOLE_Submission_Leaderboard_UCLTest1.csv ...
	# In TADPOLE_SimpleForecastExampleLeaderboard.m, you should replace SimpleForecast1 with your team name and submission index, e.g., TADPOLE_Submission_Leaderboard_TeamAwesome3.csv
	# NOTE: Change the Matlab path above as required. Otherwise load the TADPOLE_SimpleForecastExampleLeaderboard.m script manually in MATLAB and run it.
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExampleLeaderboard; exit";

	# Evaluate the user forecasts from TADPOLE_Submission_Leaderboard_UCLTest1.csv against TADPOLE_LB4.csv using the evaluation function
	python3 evalOneSubmission.py --leaderboard --d4File TADPOLE_LB4.csv --forecastFile TADPOLE_Submission_Leaderboard_SimpleForecast1.csv;

	# Submit (renamed version of) TADPOLE_Submission_Leaderboard_SimpleForecast1.csv to TADPOLE website via the Submit page

clear:
	rm -f D4_dummy.csv TADPOLE_LB1_LB2.csv TADPOLE_Submission_SimpleForecast1.csv TADPOLE_LB4.csv TADPOLE_Submission_Leaderboard_SimpleForecast1.csv leaderboard_table.html TADPOLE_Submission_Leaderboard_SimpleForecast1.csv





###### DEVELOPERS ONLY ##########

copyToPublicRepo:
	cp evalOneSubmission.py leaderboardRunAll.py TADPOLE_SimpleForecastExample.m makeDummyD4.py makeLeaderboardDataset.py TADPOLE_SimpleForecastExampleLeaderboard.m MAUC.py Makefile ../neil_repo/evaluation

processLeaderboardSubmissions:
	python3 leaderboardRunAll.py

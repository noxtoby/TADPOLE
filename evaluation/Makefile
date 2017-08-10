# change this to the matlab path of the local computer
MATLAB_PATH = ~/programs/MATLAB/bin/matlab
#MATLAB_PATH = /Applications/MATLAB_R2015b.app/bin/matlab

######## pipeline for generating and evaluating a proper TADPOLE submission ###########
eval:
	# First save TADPOLE_D1_D2.csv in the parent directory
	# NOTE: Change the Matlab path above as required. Otherwise load the script manually in MATLAB and run it.

	# Generate a simple forecast from D2 and save it as TADPOLE_Submission_SimpleForecast1.csv ...
	# Replace SimpleForecast1 with your team name and submission index
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExample; exit";

	# Then make a dummy D4 dataset, which would be similar in format to the real D4
	python3 makeDummyD4.py;

	# Evaluate the user forecasts from SimpleForecastExampleFromD2.csv against D4_dummy.csv using the evaluation function
	python3 evalOneSubmission.py --d4File D4_dummy.csv --forecastFile TADPOLE_Submission_SimpleForecast1.csv;

    #### Expected numbers for our generated dataset. These don't apply to the leaderboard submission
    #### or other types of predictive models or D4 dummy datasets
	# Clinical diagnosis metrics: should give around 0.5 since they were generated randomly
	# MAE should be around sqrt(2/pi)*sigma, which is 1.190 for ADAS and 1910 for Ventricles
	# WES should be similar to MAE, since the coefficients are almost equal.

########### pipeline for generating and evaluating a leaderboard submission ##########
leaderboard:
	# First generate the leaderboard datasets LB1, LB2 and LB4 and the submission skeleton
	python3 makeLeaderboardDataset.py;

	# Then generate a simple forecast from LB2, and save it as TADPOLE_Submission_Leaderboard_UCLTest1.csv ...
	# Replace UCLTest1 with your team name and submission index
	# NOTE: Change the Matlab path above as required. Otherwise load the script manually in MATLAB and run it.
	$(MATLAB_PATH) -nodesktop -nosplash -r "cd $(CURDIR); TADPOLE_SimpleForecastExampleLeaderboard; exit";

	# Evaluate the user forecasts from TADPOLE_Submission_Leaderboard_UCLTest1.csv against TADPOLE_LB4.csv using the evaluation function
	python3 evalOneSubmission.py --leaderboard --d4File TADPOLE_LB4.csv --forecastFile TADPOLE_Submission_Leaderboard_UCLTest1.csv;

	# submit TADPOLE_Submission_Leaderboard_UCLTest1.csv to TADPOLE website 

clear:
	rm -f D4_dummy.csv TADPOLE_LB1_LB2.csv TADPOLE_Submission_SimpleForecast1.csv TADPOLE_LB4.csv TADPOLE_Submission_Leaderboard_UCLTest1.csv leaderboard_table.html TADPOLE_Submission_Leaderboard_TeamName.csv





###### DEVELOPERS ONLY ##########

copyToPublicRepo:
	cp evalOneSubmission.py leaderboardRunAll.py SimpleForecastExampleFromD2.m makeDummyD4.py makeLeaderboardDataset.py SimpleForecastExampleFromLB2.m MAUC.py Makefile ../neil_repo/evaluation

processLeaderboardSubmissions:
	python3 leaderboardRunAll.py

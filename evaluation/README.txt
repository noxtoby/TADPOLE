
######## Evaluation scripts for used in TADPOLE Challenge 2017 ##########
Requires: Python version 3 (python3), and some dependencies.

Scripts provided in this subfolder are for two main purposes:
1. generating and evaluating an example of a valid TADPOLE submission
2. generating the leaderboard datasets (LB1, LB2 and LB4) + generating and evaluating a leaderboard submission

For both scenarios, we provide pipelines in the Makefile. These can be run as follows:
1. make eval (valid TADPOLE submission)
2. make leaderboard (leaderboard dataset generation + leaderboard submission using various scripts in this collection)

##### Generation and evaluation of a valid TADPOLE submission #########

We provide some scripts that can be used to test if the submission is valid and compute actual performance measures against a dummy D4 dataset, which is generated (almost) randomly

The following scripts need to be run in this order:
  1. TADPOLE_SimpleForecastExample.m (MATLAB) - constructs a simple forecast from the D2 dataset. Requires TADPOLE_D1_D2.csv spreadsheet. You can use this MATLAB script as a starting point for making your own forecasts via MATLAB, and generating a spreadsheet with the correct format for submission to the challenge.
  2. makeDummyD4.py (Python 3) - builds a dummy D4 dataset, which would be similar in format to the real D4
  3. evalOneSubmission.py (Python 3) - evaluates the previously-generated user forecasts against the D4 dummy dataset

See the Makefile (eval section) for how to run the scripts

###### Generation and evaluation of a leaderboard submission (optional) #########

An optional leaderboard submission is available for TADPOLE Challenge participants who want to get an idea of how their submission might perform against others. See the TADPOLE Challenge website for more details about the leaderboard.

We provide scripts that can be used to generate the leaderboard datasets (LB1, LB2 and LB4) from the TADPOLE datasets, then generate forecasts for LB2 subjects using a simple method. These forecasts are then compared against the true values in LB4. The results are published on the TADPOLE website.

The following scripts need to be run in this order:
  1. makeLeaderboardDataset.py - creates the leaderboard datasets LB1 (training), LB2 (subjects for which forecasts are requires) and LB4 (biomarker values for LB2 subjects at later visits). Also creates the submission skeleton for the leaderboard TADPOLE_Submission_Leaderboard_TeamName.csv
  2. TADPOLE_SimpleForecastExampleLeaderboard.m - generates forecasts for every subject in LB2 using a simple method
  3. evalOneSubmission.py - evaluates the previously generated user forecasts against LB4
If everything runs without errors and step 3 prints out the performance measures successfully, your leaderboard submission spreadsheet is ready to be uploaded via the TADPOLE website. You must be registered on the website, and logged in, in order to upload via the Submit page.

See the Makefile (leaderboard section) for how to run the scripts

##### Generating the leaderboard table ######

This section is mainly for the TADPOLE Challenge Organisers, but individual users are welcome to have a look at the leaderboardRunAll.py script, if they're interested to know how the leaderboard table is generated.

The script leaderboardRunAll.py downloads all the TADPOLE leaderboard submissions from the website (via the shared Dropbox folder), evaluates them against LB4 and then uploads the results back on the website in the leaderboard table.

The script only downloads and evaluates files that start with 'TADPOLE_Submission_Leaderboard'. Files are assumed to be in .csv format


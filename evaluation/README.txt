
######## Evaluation scripts for used in the TADPOLE challenge ##########

Scripts provided here are for two main purposes:
1. evaluation of a proper TADPOLE submission
2. evaluation of a leaderboard submission

For both scenarios, we provide pipelines in the Makefile. These can be run as follows:
1. make eval (TADPOLE submission)
2. make leaderboard (leaderboard submission)

##### Evaluation of a proper TADPOLE submission #########

We provide some scripts that can be used to test if the submission is valid and compute actual performance measures against a dummy D4 dataset, which is generated (almost) randomly

The following scripts need to be run in this order:
  1. SimpleForecastExampleFromD2.m - constructs a simple forecast from the D2 dataset. Requires TADPOLE_D1_D2.csv spreadsheet

  2. makeDummyD4.py - builds a dummy D4 dataset, which would be similar in format to the real D4

  3. evalOneSubmission.py - evaluates the previously-generated user forecasts against the D4 dummy dataset

See the Makefile (eval section) for how to run the scripts

###### Evaluation of a leaderboard submission #########

We provide scripts that can be used to generate the leaderboard datasets (LB1, LB2 and LB4) from the TADPOLE datasets, then generate forecasts for LB2 subjects using a simple method. These forecasts are then compared against the true values in LB4. The results are published on the TADPOLE website.

The following scripts need to be run in this order:
  1. makeLeaderboardDataset.py - creates the leaderboard datasets LB1 (training), LB2 (subjects for which forecasts are requires) and LB4 (biomarker values for LB2 subjects at later visits). Also creates the submission skeleton for the leaderboard TADPOLE_Submission_Leaderboard_TeamName.csv
  2. SimpleForecastExampleFromLB2.m - generates forecasts for every subject in LB2 using a simple method
  3. evalOneSubmission.py - evaluates the previously generated user forecasts against LB4
  4. If there are no errors and the performance measures are computed successfully, upload the script on the TADPOLE website.

See the Makefile (leaderboard section) for how to run the scripts

##### Generating the leaderboard table ######

This section is mainly for TADPOLE Organisers, but individual users are welcome to have a look at the leaderboardRunAll.py script, if they're interested to know how the leaderboard table is generated

The script leaderboardRunAll.py downloads all the TADPOLE leaderboard submissions from the website (via the shared Dropbox folder), evaluates them against LB4 and then uploads the results back on the website in the leaderboard table.

The script only downloads and evaluates files that start with 'TADPOLE_Submission_Leaderboard'. Files are assumed to be in .csv format


# Simple Score Aggregator
## Description
This basic python module allows for MLB, NBA, and NFL scores to be easily accessed from the web.
Scores are stored in objects called scorecards, which store basic information such as the teams playing a game, the score, the game status, and the game date.
Scores may also be optionally converted to a JSON or a pandas dataframe if pandas is installed.
## How to Use
This aggregator is dependent on some python modules, namely `requests` and optionally `pandas`.
The primary way to access scores is through the `ScoreLoader` object. This can easily be imported from `scores.py` into whichever python script needs it. Using the `ScoreLoader`, scores can be accessed and dumped to a file with relative ease.
# Simple Score Aggregator
## Description
This basic python module allows for MLB, NBA, and NFL scores to be easily accessed from the web.
Scores are stored in objects called scorecards, which store basic information such as the teams playing a game, the score, the game status, and the game date.
Scores may also be optionally converted to a JSON or a pandas dataframe if pandas is installed.
## How to Use
Create a virtual environment using the following command:
```
python3 -m venv venv
```
To activate the virtual environment, run one of the two following commands depending on your operating system:
```
Windows: venv/Scripts/activate
Unix/Linux: source venv/bin/activate
```
After activating the virtual environment, install all required modules using the following command:
```
pip install -r requirements.txt
```
The primary way to access scores is through the `ScoreLoader` object. This can easily be imported from `scores.py` into whichever python script needs it. Using the `ScoreLoader`, scores can be accessed and dumped to a file with relative ease.
## Known Issues
NBA scores are currently not working.

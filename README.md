# GWL_Season_Stats
Generate season stats for Gopherwatch League players.  The stats are calculted from all log files from a current season.

## Arguments:<br />
**Optional**: -d, --logs-dir = Path to the directory on your system that contains all the log files. <br />
* If you don't provide this argument, it will look for logs in a dir called 'game_logs' inside of the gwl_stats dir that you unzipped.  This is the default location to place the logs, but if you haven't manually put any logs in there then omitting this argument will crash the program.

**Required**: -o, --output-file = The path to the output file that will be created containing the season stats.

# HOW TO USE (Windows (cringe))
## Setup
* Download gwl_stats.zip from github and unzip as folder named 'gwl_stats'.
  * You can use a different folder name, but you'll have to reflect that change in the paths you use.
* Go to https://www.python.org/ and download python 3.10.5 for Windows.<br />
![image](https://user-images.githubusercontent.com/107881940/174663042-754b42c6-fe97-466c-a9f1-0df397a9b1ca.png)
* Open the installer, check "Add to PATH", click Install Now, and close the installer when it's finished.<br />
![image](https://user-images.githubusercontent.com/107881940/174663629-dc21451b-8bee-4719-9bc7-b7f40a0c0946.png)
* Opend Command Prompt (START+R and type CMD)
* cd into gwl_stats directory. -> ```cd <PATH to gwl_stats dir>```<br />
![image](https://user-images.githubusercontent.com/107881940/174665441-09f76977-189c-4ce6-b90b-5cc86297dccf.png)
* Check that your PATH isn't FUBAR and py points to the correct python version. <br />
![image](https://user-images.githubusercontent.com/107881940/174665734-7b8bd19a-13c2-430e-a37c-117287ac3cd0.png)
* Run ```py -m venv .venv```. <br />
This creates a new virtual environment to run the script in.
* Run ```.\.venv\Scripts\activate``` to enter the virtual env.  Type ```deactivate``` at any time to exit.
If you fuck up inside of virtual environment, you can delete it and try over as many times as you want.
* Check that pip was installed correctly alongside python.<br />
![image](https://user-images.githubusercontent.com/107881940/174666276-b61ebfcc-3eab-4f86-8a50-b8aefb08ab93.png)
* Install requirements
  * Run ```pip install -r requirements.txt```.  At the moment this only installs Pandas.<br />
It will likely complain that your pip is out of date. We don car. <br />
![image](https://user-images.githubusercontent.com/107881940/174666515-cf71b4cf-3f2d-4b81-94b0-bd889cb79c90.png)

## Running the Program
To run the program enter the 'gwl_stats' directory from Command Prompt and enter ```py main.py``` and specify your arguments.<br />

Example: <br />
```py main.py --logs-dir="C:\Users\E\Documents\dev\GWL_Stats\game_logs" --output-file="C:\Users\E\Documents\stats.csv"```

It will spit out a copy of the season stats dataframe before saving it into the output file whose path/name you specified.






# Artist-Sentimentality-Quantification

This is an attempt to quantify sentimentality of tracks by a few of my favorite artists (it's a work in progress to increase the number of artists I can accomodate and analyze the work of, dynamically).

### Setting up

Running these files requires the below packages to be installed and imported - 

```
pip install numpy
pip install pandas
pip install bokeh
pip install spotipy
pip install lyricsgenius
pip install nltk
#For the latest version of Lyricsgenius - 
pip install git+https://github.com/johnwmillr/LyricsGenius.git
math #import this directly, as it is installed by default
requests #import this directly, as it is installed by default
```

### Data Acquisition

The script for acquiring the song and lyrics data can be found in the file - dataAcquisition.py

To run this script successfully, add your own Spotify Client Id on line 13 and your Spotify Client Secret on line 16

Also, add your Genius Access Token on line 19

Running this file as is with above details, would fetch the song metadata for Radiohead, Porcupine Tree, The Beatles and John Mayer's studio albums from Spotify and the lyrics of each of their tracks from Genius, and store all of this data in an excel file - track_data.xlsx (this file is included in the repository)


### Running and generating the Dashboard

Using the data acquired using dataAcquisition.py, we can now generate the bokeh dashboard. To generate the same, run the below command in the directory where this repository is downloaded - 

```
bokeh serve --show generateDashboard.py
```

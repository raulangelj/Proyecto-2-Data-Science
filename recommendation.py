from string import punctuation
import matplotlib.pyplot as plt
import re

class Recommendation(object):
  def __init__(self, df):
    self.df = df

  def get_top_5_artists(self):
    artist_names = self.df['artist_name'].value_counts().keys()[:5]
    songs = self.df['artist_name'].value_counts().values[:5]

    # plt.bar(artist_names, songs)
    # return plt.show()
    """
      return x = artist_names and y = songs for bar chart
    """
    return artist_names, songs

  def get_top_5_albums(self):
    album_name = self.df['album_name'].value_counts().keys()[:5]
    songs = self.df['album_name'].value_counts().values[:5]

    # plt.bar(album_name, songs)
    # plt.show()
    """
      return x = album_name and y = songs for bar chart
    """
    return album_name, songs

  def cleaning(self):
    df = self.df
    # remove the nan values from test and train data sets
    df = df.dropna()
    df = df.drop(['track_uri'], axis=1)
    # remove the artist_uri column frolm df
    df = df.drop(['artist_uri'], axis=1)
    # remove the album_uri column frolm df
    df = df.drop(['album_uri'], axis=1)
    # tranform artist_name column to a lower case
    df['artist_name'] = df['artist_name'].str.lower()
    # tranform track_name column to a lower case
    df['track_name'] = df['track_name'].str.lower()
    # tranform album_name column to a lower case
    df['album_name'] = df['album_name'].str.lower()
    # remove the url texts from the track_name column
    for i in range(len(df)):
        df.loc[i,'track_name'] = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', "", df.loc[i,'track_name'])
        
        # remove the url texts from the artist_name column
        df.loc[i,'artist_name'] = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', "", df.loc[i,'artist_name'])

        # remove the url texts from the album_name column
        df.loc[i,'album_name'] = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', "", df.loc[i,'album_name'])

        # remove the punctuation from the track_name column
        df.loc[i,'track_name'] = ''.join(c for c in df.loc[i,'track_name'] if c not in punctuation)

        # remove the punctuation from the artist_name column
        df.loc[i,'artist_name'] = ''.join(c for c in df.loc[i,'artist_name'] if c not in punctuation)

        # remove the punctuation from the album_name column
        df.loc[i,'album_name'] = ''.join(c for c in df.loc[i,'album_name'] if c not in punctuation)
    #Create unique string id for each track
    df['track_id'] = df['track_name'] + df['artist_name'] + df['album_name']
    # ! REVIEW IF THIS IS NEEDED IN THE FUTURE
    # #standardize the nambe of the variables 
    # df = clean(df, method = "standardize")

    self.df = df
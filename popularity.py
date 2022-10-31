
class PopularityRecommender:
  def __init__(self, tracks, playlist_df):
    self.tracks = tracks
    self.rec_model_name = 'Popularity Recommender'
    self.playlist_df = playlist_df
  
  def make_recommendation(self, pid):
    pid_most_followers = self.playlist_df.sort_values('playlist_followers', ascending=False)['pid'].iloc[0]
    recommendations_df = self.tracks.loc[self.tracks['pid'] == pid_most_followers]

    return recommendations_df

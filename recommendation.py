from collaborative import *
from string import punctuation
from popularity import PopularityRecommender
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

class Recommendation(object):
	def __init__(self, df, original_df):
		# df is the dataframe with only the tracks
		self.df = df
		# original_df is the original dataframe with the tracks and the playlists
		self.original_df = original_df
		# interacted tracks is the tracks of the playlist selected
		self.interacted_tracks = None
		# recomendation model is the recomendation model
		self.recommendation_model = None
		# Create the playlist dataframe
		self.create_playlist_dataframe()

		#Metrics results
		self.global_results = None
		self.details_results = None

	def collaborative_filtering(self, pid):
		# get songs where pid is elected
		interacted_tracks, non_interacted_tracks=get_interactions(self.df, pid)
		#Get track name , pid and artist head
		interacted_tracks[['track_name', 'pid', 'artist_name']].head(50)
		# store the tracks of the playlist selected
		interacted_tracks = interacted_tracks

		# start the collaborative filteringx
		#Crear la matriz con pid como row y cancion como column, con pivot tira error por las rows duplicadas
		factorization_matrix = self.df.pivot_table(index='pid',columns='track_id',values='event_strength',aggfunc='sum',).fillna(0)

		#Crear la sparse matrix para svds
		sparse_matrix = csr_matrix(factorization_matrix.values)
		# Performs matrix factorisation of the original user item matrix
		u, sigma, vt = svds(sparse_matrix, k = 30)  # k is number of factors
		sigma = np.diag(sigma) #para hacerla diagonal

		predicted_playlist_evaluations = np.dot(np.dot(u, sigma), vt)

		#Normalizar los valores
		playlist_predicted_ratings_norm = (predicted_playlist_evaluations - predicted_playlist_evaluations.min()) / (predicted_playlist_evaluations.max() - predicted_playlist_evaluations.min())

		#Convertir a dataframe
		factorization_matrix_df = pd.DataFrame(playlist_predicted_ratings_norm, columns = factorization_matrix.columns, index=factorization_matrix.index).transpose()

		# usamos el modelo de colaborative filetring
		collaborative_rec_model = CF_Rec(factorization_matrix_df)

		interacted_tracks_list = interacted_tracks['track_id'].tolist()
		collaborative_rec_model_recommendations = collaborative_rec_model.make_recommendation(pid, interacted_tracks_list)

		#Obtener la informacion completa del dataframe original sin dupliccados
		tracks_df = self.df[['track_id', 'track_name', 'artist_name']].drop_duplicates()
		#Merge con el dataframe de recomendaciones
		collaborative_rec_model_recommendations = collaborative_rec_model_recommendations.merge(tracks_df, how = 'left', left_on = 'track_id', right_on = 'track_id')[['rec_punctuation', 'track_id', 'track_name', 'artist_name']]

		# store the recomendation model
		recommendation_model = collaborative_rec_model_recommendations
		
		#Get model metrics
		global_results, details_results = get_metrics_rec_model(self.df,collaborative_rec_model)

		return recommendation_model, interacted_tracks, global_results, details_results

	def popularity_filtering(self, pid):
		# get songs where pid is elected
		interacted_tracks, non_interacted_tracks=get_interactions(self.df, pid)
		#Get track name , pid and artist head
		interacted_tracks[['track_name', 'pid', 'artist_name']].head(50)
		# store the tracks of the playlist selected
		interacted_tracks = interacted_tracks
	
		popularity_rec_model = PopularityRecommender(self.df, self.original_df)

		#Get model metrics
		global_results, details_results = get_metrics_rec_model(self.df, popularity_rec_model)

		popularity_rec_model_recommendations = popularity_rec_model.make_recommendation(pid)

		return popularity_rec_model_recommendations, interacted_tracks, global_results, details_results

	

	def create_playlist_dataframe(self):
		#save pid and name of the playlist
		pid = self.original_df['pid']
		name = self.original_df['name']
		self.playlist_df = pd.DataFrame({'pid': pid, 'playlist_name': name})
		# sort by pid
		self.playlist_df = self.playlist_df.sort_values(by=['pid'])
		# playlist_df.head(50)

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
		self.df['event_strength'] = 1
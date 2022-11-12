from turtle import color
from recommendation import *
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

@st.cache(allow_output_mutation=True)
def get_collaborative(filtered_playlist,recommendation_class):
	recommendation_model, interacted_tracks, global_results, details_results = recommendation_class.collaborative_filtering(filtered_playlist['pid'].iloc[0])
	return recommendation_model, interacted_tracks, global_results, details_results
	# return recommendation_class

@st.cache(allow_output_mutation=True)
def get_popularity(filtered_playlist, recommendation_class):
	recommendation_model, interacted_tracks, global_results, details_results = recommendation_class.popularity_filtering(filtered_playlist['pid'].iloc[0])
	return recommendation_model, interacted_tracks, global_results, details_results

@st.cache(allow_output_mutation=True)
def get_model(data):
	jsons = [json.loads(line.read()) for line in data]
	for file in jsons:
		file.pop('info')

    # move all the data from jsons to a single object
	data = {}
	for file in jsons:
		for key in file.keys():
			if key not in data:
				data[key] = []
			data[key].extend(file[key])
	df_original = pd.DataFrame(pd.json_normalize(data['playlists']))
    #New dataframe with tracks and pid
	df = pd.DataFrame(df_original['tracks'])
	df['pid'] = df_original['pid']

    #Separate tracks in different rows
	df_with_tracks= df.explode('tracks')

	df_with_tracks2 = pd.json_normalize(df_with_tracks['tracks'])

	#Reindex dataframe
	df_with_tracks = df_with_tracks.reset_index(drop=True)

	df_with_tracks2['pid'] = df_with_tracks['pid']
	# pid = train_dataset['pid']
	# name = train_dataset['name']
	# followers = train_dataset['num_followers']
	# playlist_df = pd.DataFrame({'pid': pid, 'playlist_name': name, 'playlist_followers': followers})

	# df = cleaning(df_with_tracks2)
	recommendation_class = Recommendation(df_with_tracks2, df_original)
	recommendation_class.cleaning()

	# Getting the top 5 albums
	ALBUMS_X, ALBUMS_Y = recommendation_class.get_top_5_albums()

	# Getting the top 5 artists
	ARTIST_X, ARTIST_Y = recommendation_class.get_top_5_artists()




	return recommendation_class, ALBUMS_X, ALBUMS_Y, ARTIST_X, ARTIST_Y


st.title("""
    # Proyecto 2 | Data Science
    """)
image = Image.open('./assets/spotify-logo.jpg')
st.sidebar.image(image)
st.write('Waiting for data input...')
#print("im here")
data = st.sidebar.file_uploader('Upload your data', type=['json'], accept_multiple_files=True)

if data is not None and len(data) > 0:

	recommendation_class, ALBUMS_X, ALBUMS_Y, ARTIST_X, ARTIST_Y = get_model(data)



	# Show the actual dataframe to wrok with
	st.write(recommendation_class.df)
    # Getting the top 5 artists bar chart
	if st.sidebar.checkbox('Show top 5 Artists'):
		# create a data frame with the top 5 artists
		top_5_artists = pd.DataFrame({'Artists': ARTIST_X, 'Songs Amount': ARTIST_Y})

		st.bar_chart(top_5_artists, x='Artists', y='Songs Amount')

	if st.sidebar.checkbox('Show top 5 Albums'):
		# create a data frame with the top 5 albums
		top_5_albums = pd.DataFrame({'Albums': ALBUMS_X, 'Songs Amount': ALBUMS_Y})

		st.bar_chart(top_5_albums, x='Albums', y='Songs Amount')

	checkbox_collaborative = st.sidebar.checkbox('Collaborative Filtering')
#......
	if checkbox_collaborative:
		st.write("""## Collaborative Filtering""")
		playlists = recommendation_class.playlist_df['playlist_name'].tolist()
		option = st.selectbox(
			'Choose a playlist',
			playlists,
			key=1
		)
		filtered_playlist = recommendation_class.original_df.loc[recommendation_class.original_df['name'] == option]
		# order filter playlist by pid
		filtered_playlist = filtered_playlist.sort_values(by=['pid'])
		# print('filtered_playlist', filtered_playlist)

		recommendation_model, interacted_tracks, global_results, details_results = get_collaborative(filtered_playlist, recommendation_class)
		# Show the user the playlist
		st.write('This are the songs of the playlist you selected:')
		st.write(interacted_tracks)

		# show the user the recommendations
		st.write('This are the recommendations for the playlist you selected:')
		st.write(recommendation_model)
		#Show metrics
		if st.checkbox("Global collaborative filtering metrics"):
			st.write("This are the global results:")
			st.write(global_results)
		if st.checkbox("Detail collaborative filtering metrics"):
			st.write("This are the detail results:")
			st.write(details_results)
#......
	checkbox_popularity = st.sidebar.checkbox('Popularity Filtering')
	if checkbox_popularity:
		st.write("""## Popularity Filtering""")
		playlists = recommendation_class.playlist_df['playlist_name'].tolist()
		option = st.selectbox(
			'Choose a playlist',
			playlists,
			key=2
		)
		filtered_playlist = recommendation_class.original_df.loc[recommendation_class.original_df['name'] == option]
		# order filter playlist by pid
		filtered_playlist = filtered_playlist.sort_values(by=['pid'])
		# print('filtered_playlist', filtered_playlist)

		recommendation_model, interacted_tracks, global_results, details_results_popularity = get_popularity(filtered_playlist,recommendation_class)
		# Show the user the playlist
		st.write('This are the songs of the playlist you selected:')
		st.write(interacted_tracks)

		# show the user the recommendations
		st.write('This are the recommendations for the playlist you selected:')
		st.write(recommendation_model)
		#Show metrics
		if st.checkbox("Global Popularity filtering metrics"):
			st.write("This are the global results:")
			st.write(global_results)
		if st.checkbox("Detail Popularity filtering metrics"):
			st.write("This are the detail results:")
			st.write(details_results_popularity)

	if checkbox_popularity == True and checkbox_collaborative == True:
			if st.sidebar.checkbox('General metrics'):
				st.write("## General metrics")
				#Hits
				# create one dataframe with percentage of hits for popularity and collaborative metrics
				total_hits_5 = details_results_popularity['hits5'].sum() + details_results['hits5'].sum()
				percentage_p = round(details_results_popularity['hits5'].sum() / total_hits_5 * 100, 2)
				percentage_c = round(details_results['hits5'].sum() / total_hits_5 * 100, 2)
				# create one dataframe with percentage of hits for popularity and collaborative metrics
				total_hits_10 = details_results_popularity['hits10'].sum() + details_results['hits10'].sum()
				percentage_p10 = round(details_results_popularity['hits10'].sum() / total_hits_10 * 100, 2)
				percentage_c10 = round(details_results['hits10'].sum() / total_hits_10 * 100, 2)

				# create one dataframe with percentage of hits with popularity and collaborative as column name
				hits = pd.DataFrame({'Popularity': [percentage_p, percentage_p10], 'Collaborative': [percentage_c, percentage_c10]}, index=['Hits 5', 'Hits 10'])
				st.write(hits)

				names = ['Popularity', 'Collaborative']
				values = [percentage_p, percentage_c]
				fig = px.pie(values =values,names = names, title='Percentage of hits 5')
				st.plotly_chart(fig)
				# fig.show()

				#values of hits 10
				values = [percentage_p10, percentage_c10]
				fig = px.pie(values =values,names = names, title='Percentage of hits 10')
				st.plotly_chart(fig)

				#px.bar of hits
				df = pd.DataFrame(
					[["Hits 5 ",details_results_popularity['hits5'].sum(), details_results['hits5'].sum()], ["Hits 10", details_results_popularity['hits10'].sum(), details_results['hits10'].sum()]],
					columns=["Hits", "Popularity", "Collaborative"]
				)

				fig = px.bar(df, x="Hits", y=["Popularity", "Collaborative"], barmode='group', height=400, title='Hits of Popularity and Collaborative')
				# st.dataframe(df) # if need to display dataframe
				st.plotly_chart(fig)

				models= ["Recall 5", "Recall 10"]

				total_count = details_results_popularity['count'].sum()
				popularity_global_recall_at_5 = details_results_popularity['hits5'].sum() / total_count
				popularity_global_recall_at_10 = details_results_popularity['hits10'].sum() / total_count

				total_count = details_results['count'].sum()
				collaborative_global_recall_at_5 = details_results['hits5'].sum() / total_count
				collaborative_global_recall_at_10 = details_results['hits10'].sum() / total_count

				modelo1 = [popularity_global_recall_at_5, popularity_global_recall_at_10]
				modelo2 = [collaborative_global_recall_at_5, collaborative_global_recall_at_10]

				X_axis = np.arange(len(models))
				fig2 = plt.figure()
				#make px.bar of model recall results
				df = pd.DataFrame(
					[["Recall 5", popularity_global_recall_at_5,collaborative_global_recall_at_5], ["Recall 10", popularity_global_recall_at_10,collaborative_global_recall_at_10]],
					columns=["Recall", "Popularity", "Collaborative"]
				)

				fig = px.bar(df, x="Recall", y=["Popularity","Collaborative"], barmode='group', height=400, title='Recall of Popularity and Collaborative')
				# st.dataframe(df) # if need to display dataframe
				st.plotly_chart(fig)

from recommendation import *
import json
import numpy as np
import pandas as pd
import streamlit as st

#get data with text input
st.title("""
    # Proyecto 2 | Data Science
    """)
st.write('Waiting for data input...')
print("im here")
data = st.sidebar.file_uploader('Upload your data', type=['json'], accept_multiple_files=True)

if data is not None and len(data) > 0:
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

    # df = cleaning(df_with_tracks2)
    recommendation_class = Recommendation(df_with_tracks2)
    recommendation_class.cleaning()


    st.write(recommendation_class.df)

    # Getting the top 5 albums
    ALBUMS_X, ALBUMS_Y = recommendation_class.get_top_5_albums()

    # Getting the top 5 artists
    ARTIST_X, ARTIST_Y = recommendation_class.get_top_5_artists()

    # Getting the top 5 artists bar chart
    if st.sidebar.checkbox('Show top 5 Artists'):
      # create a data frame with the top 5 artists
      top_5_artists = pd.DataFrame({'Artists': ARTIST_X, 'Songs Amount': ARTIST_Y})

      st.bar_chart(top_5_artists, x='Artists', y='Songs Amount')

    if st.sidebar.checkbox('Show top 5 Albums'):
      # create a data frame with the top 5 albums
      top_5_albums = pd.DataFrame({'Albums': ALBUMS_X, 'Songs Amount': ALBUMS_Y})

      st.bar_chart(top_5_albums, x='Albums', y='Songs Amount')

    if st.checkbox('Collaborative Filtering'):
      st.write("""
        ## Collaborative Filtering
      """)
      option = st.selectbox(
        'Elija una playlist',
        (playlists))
      filtered_playlist = df.loc[df['name'] == option]
      songs_list = filtered_playlist['tracks'][playlists.index(option)]
      tracks = pd.DataFrame(songs_list).set_index('pos')
      tracks

      # filtered_playlist['tracks']
      # songs = filtered_playlist['tracks'][0]
      # songs_list = []
      # for i in songs:
      #   songs_list.append(i['track_name'])
      # songs_df = pd.DataFrame (songs_list, columns=['Track name'])
      # songs_df
      # st.write('TIPO DEL RESULTADO: ', type(filtered_playlist))
      # st.write('TIPO DEL RESULTADO 2: ', type(songs))

      st.write('### Mostrando resultados para:', option)

      if st.checkbox('Sistema de popularidad'):
        st.write("""
          ## Sistema de popularidad
        """)
        data = pd.DataFrame({
          'first column': [1, 2, 3, 4],
          'second column': [10, 20, 30, 40]
          })
        data


# st.write("Here's our first attempt at using data to create a table:")
# st.write(pd.DataFrame({
#     'first column': [1, 2, 3, 4],
#     'second column': [10, 20, 30, 40]
# }))

# chart_data = pd.DataFrame(
#      np.random.randn(20, 3),
#      columns=['a', 'b', 'c'])

# st.line_chart(chart_data)

# x = st.slider('x')  # 👈 this is a widget
# st.write(x, 'squared is', x * x)

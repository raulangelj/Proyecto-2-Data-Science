from io import StringIO
import json
import numpy as np
import pandas as pd
import streamlit as st

def cleaning(df):
  # remove the nan values from test and train data sets
  df = df.dropna()
  df = df.drop(['track_uri'], axis=1)
  # remove the artist_uri column frolm df
  df = df.drop(['artist_uri'], axis=1)
  # remove the album_uri column frolm df
  df = df.drop(['album_uri'], axis=1)
  
  
  return df

#get data with text input
st.title('Data Science Project')
st.write('This is a data science project')
st.write('Please enter the data below')
print("im here")
data = st.sidebar.file_uploader('Upload your data', type=['json'], accept_multiple_files=True)
loaded = False
if data is not None and len(data) > 0 and not loaded:
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
    df = pd.DataFrame(pd.json_normalize(data['playlists']))
    
    # df = cleaning(df)

    st.write(df)
    playlists = df['name'].tolist()

    st.write("""
    # Proyecto 2 | Data Science
    """)

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

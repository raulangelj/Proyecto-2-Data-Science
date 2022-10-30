from sklearn.model_selection import train_test_split
import pandas as pd

def get_interactions(tracks, pid):
    #Se obtiene los ids de las tracks que estan en la playlist
    favorite_tracks_ids = tracks[tracks['pid'] == pid]['track_id']
    #Se obtiene la info de esas canciones
    interacted_tracks = tracks[tracks['pid'] == pid]
    #Se obtiene las que no han interactuado en la playlist
    non_interacted_tracks = tracks[~tracks['track_id'].isin(favorite_tracks_ids)]

    interacted_tracks = interacted_tracks.drop_duplicates(subset='track_id',keep="first").reset_index()
    non_interacted_tracks = non_interacted_tracks.drop_duplicates(subset = 'track_id',keep="first").reset_index()


    return interacted_tracks, non_interacted_tracks

def format_results(n,len_test,hits5,hits10,pid):
    #Calcular recall 5 y 10
    recall5 = hits5/len_test
    recall10 = hits10/len_test

    return {'n': n, 'recall5': recall5, 'recall10': recall10, 'hits5': hits5, 'hits10': hits10, 'pid': pid, 'count': len_test}

def get_hits_results(test,no_interacted,recomendations,n=100, seed=60):
    #Hacer loop en test para evaluar 
    hits5 = 0
    hits10 = 0

    for i in range(len(test)):
        #Se toma una muestra de las que no interactuaron
        sample_no_present = no_interacted.sample(n=n, random_state=seed)
        #Get the track id of the i element in test 
        track_id = test.iloc[i]['track_id']
        evaluation_ids = sample_no_present['track_id'].tolist()
        evaluation_ids.extend([track_id])

        #Se obtiene las canciones que si estan en los ids
        recommendations_present = recomendations[recomendations['track_id'].isin(evaluation_ids)]

        if test.iloc[i]['track_id'] in recommendations_present['track_id'][:5].tolist():
            hits5 += 1
        if test.iloc[i]['track_id'] in recommendations_present['track_id'][:10].tolist():
            hits10 += 1
    
    return hits5,hits10

def get_metrics_rec_model_for_playlist(songs_dataframe,rec_model, pid, n=100, seed=60):
    
    hits5, hits10 = 0, 0
    #Del dataframe se obtiene las que no han interactuado y las que si con el playlist id es curso
    tracks_present_df, no_present_track_df = get_interactions(songs_dataframe, pid)
    
    #Se divide las que interactuaron en train y test para evaluar la eficiencia
    train, test = train_test_split(tracks_present_df, test_size=0.2, random_state=seed)
    
    #Se recomienda para el playlist id en curso 
    df_recomendations = rec_model.make_recommendation(pid)

    #Se obtiene los hits
    hits5, hits10 = get_hits_results(test,no_present_track_df,df_recomendations)

    #Append results 
    return format_results(n,len(test),hits5,hits10,pid)


#Obtiene las metricas en general de toda la evaluacion
def get_global_results(detailed_playlists_metrics, rec_model):
    #Obtener el total de conteo
    total_count = detailed_playlists_metrics['count'].sum()
    global_recall_at_5 = detailed_playlists_metrics['hits5'].sum() / total_count
    global_recall_at_10 = detailed_playlists_metrics['hits10'].sum() / total_count

    #Retornar string con resultados, nombre de rec_modelo , recall 5 y 10
    return 'rec_model: ' + rec_model.rec_model_name + ' Recall5: ' + str(global_recall_at_5) + ' Recall10: ' + str(global_recall_at_10)

#https://stackoverflow.com/questions/28056171/how-to-build-and-fill-pandas-dataframe-from-for-loop
def get_metrics_rec_model(songs_dataframe,rec_model, n=100, seed=60):
    temporal = []
    for pid in songs_dataframe['pid'].unique():
        evaluation_results = get_metrics_rec_model_for_playlist(songs_dataframe,rec_model, pid, n=n, seed=seed)
        temporal.append(evaluation_results)
        
    #Sort results according to count 
    evaluation_results = pd.DataFrame(temporal).sort_values('count',ascending=False)

    general_rec_model_metrics = get_global_results(evaluation_results, rec_model)
    
    return general_rec_model_metrics, evaluation_results

class CF_Rec:

    def __init__(self, factorization_matrix_df):
        self.factorization_matrix_df = factorization_matrix_df
        self.rec_model_name = 'Collaborative Filtering Recommendation'

    def make_recommendation(self, pid, ids_to_ignore=None):
        if ids_to_ignore is None:
            ids_to_ignore = []
        sorted_playlist_predictions = self.factorization_matrix_df[pid].sort_values(ascending=False).reset_index()

        sorted_playlist_predictions = sorted_playlist_predictions.rename(columns={pid: 'rec_punctuation'})

        return sorted_playlist_predictions[~sorted_playlist_predictions['track_id'].isin(ids_to_ignore)].drop_duplicates(subset='track_id', keep="first").reset_index().sort_values('rec_punctuation', ascending=False)
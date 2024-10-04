import streamlit as st
import pandas as pd
import numpy as np
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from data_loading import load_competitions, load_matches_for_competition, load_match_events
#from visualizations import test_pitch_creation  # Importação da função
from statsbombpy import sb
from mplsoccer import Pitch, FontManager, Sbopen


st.set_page_config(page_title="Análise Futebolística", layout="wide")

st.markdown("""
# Bem-vindo à Análise de Futebol Interativa!
Explore dados detalhados de jogos de futebol, visualize mapas de passes, chutes e muito mais. 
Esta aplicação permite que você filtre eventos por jogador e visualize métricas específicas que ajudam a entender o desempenho no campo.

## Recursos Disponíveis:
- **Seleção de Partida:** Selecione a partida e obtenha informações sobre os times, como nomes dos jogadores, técnicos e juízes.
- **Seleção de Jogador:** Escolha um jogador para analisar seus passes, chutes e dribles.
- **Visualização de Eventos:** Veja mapas detalhados de passes e chutes para entender as táticas e a precisão.
- **Download de Dados:** Baixe os dados filtrados para análise offline ou apresentações.
- **Métricas Detalhadas:** Explore o total de chutes, passes e outros indicadores de desempenho.

Prepare-se para mergulhar nos detalhes como nunca antes! 🚀
""")

st.title('⚽ Análise de Futebol Interativa 📊')

# Carregar dados
competitions = load_competitions()
competition_names = competitions['competition_name'].unique()

with st.sidebar:
    st.title("Filtros de Dados")
    selected_competition_name = st.selectbox("Selecione a Competição", options=competition_names)
    competition_id = competitions[competitions['competition_name'] == selected_competition_name]['competition_id'].iloc[0]
    seasons = competitions[competitions['competition_name'] == selected_competition_name]['season_name'].unique()
    selected_season_name = st.selectbox("Selecione a Temporada", options=seasons)
    season_id = competitions[(competitions['competition_name'] == selected_competition_name) & (competitions['season_name'] == selected_season_name)]['season_id'].iloc[0]

    matches = load_matches_for_competition(competition_id, season_id)
    match_options = matches['match_id'].astype(str) + " - " + matches['home_team'] + " vs " + matches['away_team']
    selected_match_option = st.selectbox("Selecione a Partida", options=match_options)
    match_id = int(selected_match_option.split(" - ")[0])
    selected_match_data = matches[matches['match_id'] == int(match_id)]

    # Extraindo home e away team para a partida selecionada
    match_info = matches[matches['match_id'] == match_id].iloc[0]
    teams = [match_info['home_team'], match_info['away_team']]
    team_name = st.sidebar.selectbox("Escolha o time", options=teams)


# Carregar e exibir partidas
matches = load_matches_for_competition(competition_id, season_id)
st.title("Dados da Partida:")
st.dataframe(selected_match_data)

def display_match_summary(match_id, matches):
    # Filtrar o DataFrame para a partida específica
    match_details = matches[matches['match_id'] == match_id]

    # Extrair informações
    home_team = match_details['home_team'].iloc[0]
    away_team = match_details['away_team'].iloc[0]
    home_score = match_details['home_score'].iloc[0]
    away_score = match_details['away_score'].iloc[0]
    home_managers = match_details['home_managers'].iloc[0]
    away_managers = match_details['away_managers'].iloc[0]
    match_date = match_details['match_date'].iloc[0]
    stadium = match_details['stadium'].iloc[0]
    referee = match_details['referee'].iloc[0]

    # Criar um DataFrame resumido
    summary_data = {
        "Time da casa": [home_team],
        "Time desafiante": [away_team],
        "Gols do time da casa": [home_score],
        "Técnico da casa": [home_managers], 
        "Técnico desafiante": [away_managers],
        "Gols do time desafiante": [away_score],
        "Data": [match_date],
        "Estádio": [stadium],
        "Juiz": [referee]
    }
    summary_df = pd.DataFrame(summary_data)

    
    
    # Exibir o DataFrame
    st.title("Sumário da Partida:")
    st.dataframe(summary_df)

    # Usando st.columns para organizar a informação
    col1, col2 = st.columns(2)
    
    with col1:
        st.title(home_team)
        st.subheader(f"Gols Marcados: {home_score}")
        st.write(f"Técnico: {home_managers}")


    with col2:
        st.title(away_team)
        st.subheader(f"Gols Marcados: {away_score}")
        st.write(f"Técnico: {away_managers}")



# Chamar a função para exibir o resumo da partida selecionada
display_match_summary(match_id, matches)

events = sb.events(match_id)
keys = list(events.keys())
event_type = st.selectbox('Selecione o tipo de evento para visualizá-los', keys)
st.dataframe((events[event_type]), use_container_width = True)



match_info = matches[matches['match_id'] == match_id].iloc[0]

st.subheader('Detalhes da Partida')
st.write(f"Nome da Competição: {selected_competition_name}")
st.write(f"Temporada: {match_info['season']}")
st.write(f"Partida: {match_info['home_team']} vs {match_info['away_team']}")

# Carregar events
events = sb.events(match_id=match_id)

# Estatísticas básicas
st.subheader('Estatísticas Básicas')
st.write(f"Gols: {len(events[events['shot_outcome'] == 'Goal'])}")
st.write(f"Chutes: {len(events[events['type'] == 'Shot'])}")
st.write(f"Passes: {len(events[events['type'] == 'Pass'])}")

# DataFrame de events
st.subheader('Eventos da Partida')
st.dataframe(events[['type', 'player', 'location', 'minute', 'team', 'shot_outcome']], use_container_width=True)


# Filtrar passes do time especificado
passes = events[(events['type'] == 'Pass') & (events['team'] == team_name)]
mask_complete = passes['shot_outcome'].isnull()



def passes_map(events):
    passes = events[events['type'] == 'Pass']
    pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.arrows(passes['location'].apply(lambda x: x[0]),
                 passes['location'].apply(lambda x: x[1]),
                 passes['pass_end_location'].apply(lambda x: x[0]),
                 passes['pass_end_location'].apply(lambda x: x[1]),
                 ax=ax, color='blue', lw=1, label='Passes')
    
    plt.title('Mapa de passes')
    plt.legend()
    st.pyplot(fig)

def shots_map(eventos):
    chutes = eventos[eventos['type'] == 'Shot']
    pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.scatter(chutes['location'].apply(lambda x: x[0]),
                  chutes['location'].apply(lambda x: x[1]),
                  ax=ax, color='blue', s=100, edgecolor='black', label='Chutes')
    
    plt.title('Mapa de chutes')
    plt.legend()
    st.pyplot(fig)

# Gerar visualizações
st.subheader('Mapa de passes da partida selecionada:')
passes_map(events)
st.subheader('Mapa de chutes da partida selecionada:')
shots_map(events)

import streamlit as st
from mplsoccer import Pitch
from matplotlib import pyplot as plt


def interactive_event_map(events):
    # Sidebar para seleção do tipo de evento e jogador
    event_type = st.sidebar.selectbox("Escolha o tipo de evento", ['Passes', 'Chutes'])
    unique_players = events['player'].dropna().unique()
    selected_player = st.sidebar.selectbox("Escolha o jogador", unique_players)
    
    # Filtragem de eventos por tipo e jogador
    selected_events = events[(events['type'] == event_type) & (events['player'] == selected_player)]
    
    # Configuração do pitch
    pitch = Pitch(pitch_color='#aabb97', line_color='white', stripe_color='#c2d59d', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Assegurando que as coordenadas são numéricas e tratando NaNs
    if not selected_events.empty:
        x_start = pd.to_numeric(selected_events['location'].apply(lambda x: x[0] if isinstance(x, list) else None), errors='coerce')
        y_start = pd.to_numeric(selected_events['location'].apply(lambda x: x[1] if isinstance(x, list) else None), errors='coerce')
        x_end = pd.to_numeric(selected_events['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) else None), errors='coerce')
        y_end = pd.to_numeric(selected_events['pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) else None), errors='coerce')

        if event_type == 'Passes':
            pitch.arrows(x_start.dropna(), y_start.dropna(), x_end.dropna(), y_end.dropna(),
                         ax=ax, color='blue', lw=1, label='Passes')
            plt.title('Mapa de Passes de ' + selected_player)
        elif event_type == 'Chutes':
            pitch.scatter(x_start, y_start, ax=ax, color='red', s=100, edgecolor='black', label='Chutes')
            plt.title('Mapa de Chutes de ' + selected_player)
    
    
    plt.legend()
    st.pyplot(fig)

# Exemplo de chamada da função no seu código principal
interactive_event_map(events)


def filtrar_por_jogador(eventos, jogador):
    return eventos[eventos['player'] == jogador]

def download_csv(data, filename):
    csv = data.to_csv(index=False)
    st.download_button(label='Baixar dados em CSV', data=csv, file_name=filename, mime='text/csv')

def calcular_metricas(eventos, jogador):
    eventos_jogador = filtrar_por_jogador(eventos, jogador)
    total_chutes = eventos_jogador[eventos_jogador['type'] == 'Shot'].shape[0]
    total_passes_tentados = eventos_jogador[eventos_jogador['type'] == 'Pass'].shape[0]
    total_dibres = eventos_jogador[eventos_jogador['type'] == 'Dribble'].shape[0]
    return total_chutes, total_passes_tentados, total_dibres

def main():
    st.title('Desempenho do jogador na partida:')
    st.markdown('Abaixo veja dados de passes, dribles e chutes a gol do jogador selecionado!')

    with st.spinner('Carregando dados...'):
        # Aqui você deve definir como carregar os dados
        eventos = events
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)

    # Selecionar jogador para filtrar eventos
    jogadores = eventos['player'].dropna().unique()
    jogador_selecionado = st.selectbox('Selecione um jogador', jogadores)

    eventos_filtrados = filtrar_por_jogador(eventos, jogador_selecionado)
    total_chutes, total_passes_tentados, total_dibres = calcular_metricas(eventos, jogador_selecionado)

    # Exibir métricas
    st.subheader('Indicadores do jogador')
    st.metric(label='Chutes', value=total_chutes)
    st.metric(label='Passes', value=total_passes_tentados)
    st.metric(label='Dribles', value=total_dibres)

    # Visualizações de eventos
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Mapa de passes')
            passes_map(eventos_filtrados)
        with col2:
            st.subheader('Mapa de chutes')
            shots_map(eventos_filtrados)

    # Download dos dados filtrados
    st.subheader('Faça aqui o Download dos dados filtrados')
    download_csv(eventos_filtrados, f'eventos_{jogador_selecionado}.csv')

if __name__ == "__main__":
    main()

# Formulário para entrada de dados
with st.form("options_form"):
    st.write("Configurações de Visualização")
    
    # Seleção da quantidade de eventos
    num_events = st.slider("Escolha a quantidade de eventos para visualizar:", min_value=10, max_value=500, value=100)
    
    # Intervalo de tempo em minutos
    min_time, max_time = st.slider("Escolha o intervalo de tempo (em minutos):", min_value=0, max_value=90, value=(0, 90), step=1)
    
    # Comparação entre dois jogadores
    if st.checkbox("Comparar dois jogadores?"):
        player1 = st.selectbox("Jogador 1", options=events['player'].dropna().unique())
        player2 = st.selectbox("Jogador 2", options=events['player'].dropna().unique(), index=1)
    
    # Submissão do formulário
    submitted = st.form_submit_button("Atualizar Visualização")
    if submitted:
        st.write("Configurações aplicadas:")
        st.write(f"Quantidade de eventos: {num_events}")
        st.write(f"Intervalo de tempo: de {min_time} a {max_time} minutos")
        if 'player1' in locals() and 'player2' in locals():
            st.write(f"Comparando {player1} com {player2}")  


if "num_events" not in st.session_state:
    st.session_state.num_events = 100

if submitted:
    st.session_state.num_events = num_events 

st.write(f"A quantidade atual de eventos para visualizar é {st.session_state.num_events}")
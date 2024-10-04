from statsbombpy import sb
import streamlit as st
@st.cache_data()
def load_competitions():
    """Carrega a lista de competições disponíveis."""
    return sb.competitions()
@st.cache_data()
def load_matches_for_competition(competition_id, season_id):
    """Carrega todos os matches de uma competição e temporada especificados."""
    return sb.matches(competition_id=competition_id, season_id=season_id)
@st.cache_data()
def load_match_events(match_id):
    """Carrega os eventos de uma partida específica."""
    return sb.events(match_id=match_id)

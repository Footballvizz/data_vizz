import streamlit as st
import pandas as pd

from fonctions import passe, shot, pass_cross,succ_pass, ball_loss,final_third_entries,passing_network


import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("soccer.jpg")  # Mets ici le nom de ton image locale
st.markdown("""
    <style>
        .title-container {
            background-color: rgba(0, 0, 0, 0.6);  /* Fond noir semi-transparent */
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .title-text {
            color: white;
            font-size: 30px;
            font-weight: bold;
        }
    </style>
    <div class="title-container">
        <p class="title-text">📂 Chargement de données pour les VizZ 📊⚽</p>
    </div>
""", unsafe_allow_html=True)

import streamlit as st

# Définis un mot de passe secret
SECRET_CODE = "FootballVizz_@2025"

# Crée un champ de mot de passe
code = st.text_input("🔑 Entrez le code d'accès :", type="password")

# Vérifie si le code est correct
if code != SECRET_CODE:
    st.warning("⛔ Accès refusé ! Entrez un code valide.")
    st.stop()  # Arrête l'exécution ici si le code est faux

st.success("✅ Accès autorisé ! Bienvenue dans l'application.")


#st.markdown("<h1 style='text-align: center; color: white;'> Football  DataVizZ📊⚽</h1>", unsafe_allow_html=True)

# Streamlit UI
#st.title("📂 Chargement de données pour les VizZ ⚽")

# File uploader
uploaded_file = st.file_uploader("📂 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Detect file type and load data
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file, engine="openpyxl")

    # Check required columns
    required_columns = {"pos_x_meters", "pos_y_meters", "pos_target_x_meters", "pos_target_y_meters"}
    if not required_columns.issubset(data.columns):
        st.error(f"The file must contain the columns: {required_columns}")
    else:
        # Transform data to fit a 120x80 pitch
        data["x"] = (data["pos_x_meters"] * 120) / 100
        data["y"] = (data["pos_y_meters"] * 80) / 68
        data["end_x"] = (data["pos_target_x_meters"] * 120) / 100
        data["end_y"] = (data["pos_target_y_meters"] * 80) / 68
        # Liste des équipes possibles
        teams=list(data['team'].drop_duplicates())
        # Sélection de l'équipe qui commence de gauche à droite
        st.markdown("<h3 style='font-size:24px;'>Sélectionnez l'équipe qui a commencé de droite à gauche :</h3>", unsafe_allow_html=True)
        left_to_right_team = st.selectbox("", teams)
        # Affichage du choix
        if (data['half'] == 1).any():
            mask=(data.team==left_to_right_team)
            data.loc[data['team']==left_to_right_team, 'x']= 120- data['x']
            data.loc[data['team']==left_to_right_team, 'y']= 80- data['y']
            data.loc[data['team']==left_to_right_team, 'end_x']= 120- data['end_x']
            data.loc[data['team']==left_to_right_team, 'end_y']= 80- data['end_y']
        if (data['half'] == 2).any():
            maskk= ~(mask)
            data.loc[maskk, 'x']= 120- data['x']
            data.loc[maskk, 'y']= 80- data['y']
            data.loc[maskk, 'end_x']= 120- data['end_x']
            data.loc[maskk, 'end_y']= 80- data['end_y']

    teams=list(data['team'].drop_duplicates())
    teams_choice = st.sidebar.selectbox('Team', teams)
    df_team_selected=data[data['team']==teams_choice]
    plot_options=['Passes',"Succ/Unsucc Passes","Crosses",'Shots',"Passing Network","Ball Loss","Ball Recovery","Final Third"]
    selected_plot = st.sidebar.selectbox('VizZ type:', plot_options)

    if selected_plot == 'Passes':
       
       #st.markdown('<h1 class="custom-header">Description </h1>', unsafe_allow_html=True)
       st.markdown('<h1 class="custom-subheader">Ball Pass: </h1>', unsafe_allow_html=True)
       text="Ball is passed between teammates."
       beige_text = f'<span style="color: #F5F5DC;font-size: 20px">{text}</span>'
       st.markdown(beige_text, unsafe_allow_html=True)
       st.markdown('<h1 class="custom-subheader">Ball Receipt: </h1>', unsafe_allow_html=True)
       text="The receipt or intended receipt of a pass."
       beige_text = f'<span style="color: #F5F5DC;font-size: 20px">{text}</span>'
       st.markdown(beige_text, unsafe_allow_html=True)
       passe(data,teams_choice)


    elif selected_plot == 'Shots':
          #st.markdown('<h1 class="custom-header">Description </h1>', unsafe_allow_html=True)
          st.markdown('<h1 class="custom-subheader">Shot: </h1>', unsafe_allow_html=True)
          text="An attempt to score a goal, made with any (legal) part of the body."
          beige_text = f'<span style="color: #F5F5DC;font-size: 20px">{text}</span>'
          st.markdown(beige_text, unsafe_allow_html=True)

          shot(df_team_selected)
    elif selected_plot == 'Crosses':
         #st.markdown('<h1 class="custom-header">Description </h1>', unsafe_allow_html=True)
         st.markdown('<h1 class="custom-subheader">Cross: </h1>', unsafe_allow_html=True)

         text='A [cross](https://www.soccerhelp.com/terms/soccer-cross.shtml) is a "square pass" to the area in front of the goal.'
         beige_text = f'<span style="color: #F5F5DC;font-size: 20px">{text}</span>'
         st.markdown(beige_text, unsafe_allow_html=True)
         pass_cross(df_team_selected)
    elif selected_plot== 'Succ/Unsucc Passes' :
        succ_pass(df_team_selected)
    elif selected_plot == "Ball Loss" :
        ball_loss(df_team_selected)
    elif selected_plot == "Final Third" :
        final_third_entries(df_team_selected)
    elif selected_plot == "Passing Network" :
        passing_network(df_team_selected)
    




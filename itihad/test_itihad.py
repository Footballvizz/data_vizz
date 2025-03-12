import streamlit as st
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba,LinearSegmentedColormap
from mplsoccer import Pitch, VerticalPitch, FontManager
from matplotlib.markers import MarkerStyle
from matplotlib.colors import LinearSegmentedColormap,to_rgba
from scipy.ndimage import gaussian_filter
import matplotlib.patheffects as path_effects
import matplotlib.patches as patches


import bcrypt
import json
from pathlib import Path
# Add this to your Streamlit app
import time
import streamlit as st
from datetime import datetime



# Configure the page
st.set_page_config(
    page_title="Al-Ittihad Football Analysis",
    page_icon='itihad.png',
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Cache data with 24-hour TTL
@st.cache_data(ttl=24*60*60)  # 24 hours in seconds
def get_cached_data():
    # This will force a rerun every 24 hours
    return datetime.now()

# Center the image at the bottom
st.sidebar.image("itihad.png")


# Custom CSS for Al-Ittihad theme
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #000000, #1a1a1a);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.9),
            rgba(26, 26, 26, 0.9)
        ),
        url("https://images.unsplash.com/photo-1522778119026-d647f0596c20?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80");
        background-size: cover;
        background-position: center;
        border-right: 2px solid #FFD700;
    }
    
    [data-testid="stSidebarNav"] {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Sidebar title and text */
    [data-testid="stSidebar"] .sidebar-title {
        color: #FFD700;
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
        border-bottom: 2px solid #FFD700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Sidebar selectbox styling */
    [data-testid="stSelectbox"] {
        background-color: rgba(255, 215, 0, 0.1);
        border-radius: 5px;
        margin: 10px 0;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background-color: transparent;
        color: #FFD700 !important;
        border: 1px solid #FFD700;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #FFD700, #ffc107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Analyst name styling */
    .analyst-name {
        color: #FFD700;
        font-size: 1.2em;
        text-align: right;
        padding: 10px;
    }
    
    /* Custom container for content */
    .custom-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Button styling */
    .stButton button {
        background-color: rgba(255, 215, 0, 0.1);
        color: #FFD700;
        font-weight: bold;
        border: 1px solid #FFD700;
        padding: 10px 20px;
        border-radius: 5px;
        transition: all 0.3s ease;
        width: 100%;
        margin: 5px 0;
    }
    
    .stButton button:hover {
        background-color: #FFD700;
        color: #000000;
        transform: translateY(-2px);
    }
    
    /* Analysis buttons container */
    .analysis-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        padding: 20px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        margin: 20px 0;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 215, 0, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 1px dashed #FFD700;
    }
    
    /* Welcome message container */
    .welcome-container {
        background: rgba(255, 215, 0, 0.1);
        border-radius: 10px;
        padding: 30px;
        margin: 30px 0;
        text-align: center;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)




# Constants for visualization
bg_color = '#1a1a1a'
line_color = '#FFD700'
pass_color="#05FF00"
sub_list = []  # List of substituted players
# Match Analysis Functions
def create_defensive_actions_player_map(df):
    # Filter defensive actions
    defensive_types = ['Tackle', 'Clearance', 'Save', 'Challenge']
    defensive_df = df[df['typeId'].isin(defensive_types)].copy()
    #defensive_df = defensive_df[defensive_df['shortName'] == player_name]
    defensive_df.reset_index(drop=True, inplace=True)
    player_name=df["shortName"].unique()
    # Create figure with reduced size
    pitch = pitch = VerticalPitch(pitch_type='statsbomb', corner_arcs=True,
                         pitch_color=bg_color, line_color=line_color, line_zorder=2)
    fig, axs= pitch.grid(ncols=2,grid_height=0.8, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
    fig.suptitle(f"{player_name} - Defensive Actions Map", fontsize=14, color=line_color, y=0.95)  # Reduced font size
    
    # Set up the pitch
    
    
    # Define markers and colors for different actions
    markers = {
        'Tackle': '^',
        'Clearance': 's',
        'Save': '*',
        'Challenge': 'D'
    }
    
    colors = {
        'Tackle': '#ff0000',
        'Clearance': '#00ff00',
        'Save': '#0000ff',
        'Challenge': '#ffff00'
    }
    
    # Plot each type of defensive action with reduced marker size
    for action_type in defensive_types:
        actions = defensive_df[defensive_df['typeId'] == action_type]
        pitch.scatter(
            actions.x,
            actions.y,
            s=50,  # Reduced from 200
            marker=markers[action_type],
            edgecolors=colors[action_type],
            facecolors='none',
            linewidths=1.5,  # Reduced from 2
            alpha=0.7,
            ax=axs['pitch'][0],
            label=action_type  
        )
        bin_statistic = pitch.bin_statistic(defensive_df.x, defensive_df.y, statistic='count', bins=(25, 25))
        bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
        pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'][1], cmap='hot', edgecolors='#22312b',label=f' entries')
        axs["pitch"][0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=4,
            facecolor=bg_color, edgecolor=line_color, labelcolor=line_color,
             fontsize=10)  # Added smaller font size
    
    fig.set_facecolor(bg_color)
    plt.tight_layout()
    return fig



def final_third_pass_map(df,selected_team):
    df=df[df["team_name"]== selected_team]
    df= df[df["end_x"]>= 80]

    # Constants
    #bg_color = '#2A5A27'
    #line_color = '#FFFFFF'
    team_color = '#FFD700'  # Silver for away, Gold for home
    violet_color = '#8A2BE2'  # For key passes
    green_color = '#00FF00'   # For assists
    # Create figure and pitch
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg_color)
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True, 
                 pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    

    
    # Filter player's passes
    player_df = df[(df['typeId'] == 'Pass')]
    
    # Categorize passes
    pass_comp = player_df[player_df['outcome'] == 'Successful']
    pass_incomp = player_df[player_df['outcome'] == 'Unsuccessful']
    key_passes = player_df[player_df['keyPass'] == 1]
    assists = player_df[player_df['assist'] == 1]
    
    # Draw pass lines
    pitch.lines(pass_comp.x, pass_comp.y, 
               pass_comp.end_x, pass_comp.end_y,
               lw=3, transparent=True, comet=True, 
               color=team_color, ax=ax, alpha=0.65)
    
    pitch.lines(pass_incomp.x, pass_incomp.y,
               pass_incomp.end_x, pass_incomp.end_y,
               lw=3, transparent=True, comet=True,
               color='red', ax=ax, alpha=0.25)
    
    pitch.lines(key_passes.x, key_passes.y,
               key_passes.end_x, key_passes.end_y,
               lw=4, transparent=True, comet=True,
               color=violet_color, ax=ax, alpha=0.9)
    
    pitch.lines(assists.x, assists.y,
               assists.end_x, assists.end_y,
               lw=4, transparent=True, comet=True,
               color=green_color, ax=ax, alpha=1)
    
    # Add end points for passes
    pitch.scatter(pass_comp.end_x, pass_comp.end_y,
                 s=30, color=bg_color, edgecolor=team_color,
                 zorder=2, ax=ax)
    
    pitch.scatter(pass_incomp.end_x, pass_incomp.end_y,
                 s=30, color=bg_color, edgecolor='red',
                 alpha=0.25, zorder=2, ax=ax)
    
    pitch.scatter(key_passes.end_x, key_passes.end_y,
                 s=40, color=bg_color, edgecolor=violet_color,
                 linewidth=1.5, zorder=2, ax=ax)
    
    pitch.scatter(assists.end_x, assists.end_y,
                 s=50, color=bg_color, edgecolor=green_color,
                 linewidth=1.5, zorder=2, ax=ax)
    
    # Add statistics text
    ax.text(80, 83, f'Successful Pass: {len(pass_comp)}',
                color=team_color, va='center', ha='right', fontsize=12)
    ax.text(120, 83, f'Unsuccessful Pass: {len(pass_incomp)}',
                color='red', va='center', ha='right', fontsize=12)
    ax.text(80, 88, f'Key Pass: {len(key_passes)}',
                color=violet_color, va='center', ha='right', fontsize=12)
    ax.text(120, 88, f'Assist: {len(assists)}',
                color=green_color, va='center', ha='right', fontsize=12)
    ax.text(0, 85, "Attacking Direction ----->",
                color=team_color, fontsize=15, va='center', ha='left')
    
    # Set title
    ax.set_title(f"{selected_team} PassMap",
                 color=team_color, fontsize=25, fontweight='bold')
    
    return fig
def get_short_name(full_name):
    """Convert player name to shorter version"""
    if not isinstance(full_name, str):
        return None
    parts = full_name.split()
    if len(parts) == 1:
        return full_name
    elif len(parts) == 2:
        return parts[0][0] + ". " + parts[1]
    else:
        return parts[0][0] + ". " + parts[1][0] + ". " + " ".join(parts[2:])
def create_received_passes_map(df, player_name, is_away=False):
    """
    Create a visualization of passes received by a specific player.
    
    Args:
        df (DataFrame): Match event data
        player_name (str): Name of the player to analyze
        is_away (bool): Whether the player is from the away team
    """
    # Constants
    bg_color = '#2A5A27'
    line_color = '#FFFFFF'
    team_color = '#C0C0C0' if is_away else '#FFD700'  # Silver for away, Gold for home
    violet_color = '#8A2BE2'  # For key passes
    green_color = '#00FF00'   # For assists
    
    # Create figure and pitch
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg_color)
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True,
                 pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()
    
    # Filter passes received by the player
    received_passes = df[
        (df['typeId'] == 'Pass') & 
        (df['outcome'] == 'Successful') & 
        (df['receiver'] == player_name)
    ]
    
    # Categorize received passes
    key_passes_received = received_passes[received_passes['keyPass'] == 1]
    assists_received = received_passes[received_passes['assist'] == 1]
    normal_passes = received_passes[
        (received_passes['keyPass'] != 1) & 
        (received_passes['assist'] != 1)
    ]
    
    # Draw pass lines
    pitch.lines(normal_passes.x, normal_passes.y,
               normal_passes.end_x, normal_passes.end_y,
               lw=3, transparent=True, comet=True,
               color=team_color, ax=ax, alpha=0.5)
    
    pitch.lines(key_passes_received.x, key_passes_received.y,
               key_passes_received.end_x, key_passes_received.end_y,
               lw=4, transparent=True, comet=True,
               color=violet_color, ax=ax, alpha=0.75)
    
    pitch.lines(assists_received.x, assists_received.y,
               assists_received.end_x, assists_received.end_y,
               lw=4, transparent=True, comet=True,
               color=green_color, ax=ax, alpha=0.75)
    
    # Add end points for received passes
    pitch.scatter(normal_passes.end_x, normal_passes.end_y,
                 s=30, edgecolor=team_color, linewidth=1,
                 color=bg_color, zorder=2, ax=ax)
    
    pitch.scatter(key_passes_received.end_x, key_passes_received.end_y,
                 s=40, edgecolor=violet_color, linewidth=1.5,
                 color=bg_color, zorder=2, ax=ax)
    
    pitch.scatter(assists_received.end_x, assists_received.end_y,
                 s=50, edgecolors=green_color, linewidths=1,
                 marker='football', c=bg_color, zorder=2, ax=ax)
    
    # Add average position lines
    if len(received_passes) > 0:
        avg_endY = received_passes['end_y'].median()
        avg_endX = received_passes['end_x'].median()
        ax.axvline(x=avg_endX, ymin=0, ymax=68, color='gray',
                  linestyle='--', alpha=0.6, linewidth=2)
        ax.axhline(y=avg_endY, xmin=0, xmax=105, color='gray',
                  linestyle='--', alpha=0.6, linewidth=2)
    
    # Add title and statistics
    name_show = get_short_name(player_name)
    total_received = len(received_passes)
    key_passes_count = len(key_passes_received)
    
    ax.set_title(f"{name_show} Passes Received",
                 color=team_color, fontsize=25, fontweight='bold')
    
    stats_text = f'Passes Received: {total_received} (Key Passes: {key_passes_count})'
    if is_away:
        ax.text(60, -2, stats_text,
                color=line_color, fontsize=15,
                ha='center', va='center')
        ax.text(0, -5, "<----- Attacking Direction",
                color=team_color, fontsize=15,
                va='center', ha='right')
    else:
        ax.text(60, 83, stats_text,
                color=line_color, fontsize=15,
                ha='center', va='center')
        ax.text(0, 85, "Attacking Direction ----->",
                color=team_color, fontsize=15,
                va='center', ha='left')
    
    return fig



def create_player_pass_map(df, player_name, is_away=False):
    """
    Create a pass map visualization for a specific player.
    
    Args:
        df (DataFrame): Match event data
        player_name (str): Name of the player to analyze
        is_away (bool): Whether the player is from the away team
    """
    # Constants
    #bg_color = '#2A5A27'
    #line_color = '#FFFFFF'
    team_color = '#C0C0C0' if is_away else '#FFD700'  # Silver for away, Gold for home
    violet_color = '#8A2BE2'  # For key passes
    green_color = '#00FF00'   # For assists
    
    # Create figure and pitch
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg_color)
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True, 
                 pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()
    
    # Filter player's passes
    player_df = df[(df['shortName'] == player_name) & (df['typeId'] == 'Pass')]
    
    # Categorize passes
    pass_comp = player_df[player_df['outcome'] == 'Successful']
    pass_incomp = player_df[player_df['outcome'] == 'Unsuccessful']
    key_passes = player_df[player_df['keyPass'] == 1]
    assists = player_df[player_df['assist'] == 1]
    
    # Draw pass lines
    pitch.lines(pass_comp.x, pass_comp.y, 
               pass_comp.end_x, pass_comp.end_y,
               lw=3, transparent=True, comet=True, 
               color=team_color, ax=ax, alpha=0.65)
    
    pitch.lines(pass_incomp.x, pass_incomp.y,
               pass_incomp.end_x, pass_incomp.end_y,
               lw=3, transparent=True, comet=True,
               color='red', ax=ax, alpha=0.25)
    
    pitch.lines(key_passes.x, key_passes.y,
               key_passes.end_x, key_passes.end_y,
               lw=4, transparent=True, comet=True,
               color=violet_color, ax=ax, alpha=0.9)
    
    pitch.lines(assists.x, assists.y,
               assists.end_x, assists.end_y,
               lw=4, transparent=True, comet=True,
               color=green_color, ax=ax, alpha=1)
    
    # Add end points for passes
    pitch.scatter(pass_comp.end_x, pass_comp.end_y,
                 s=30, color=bg_color, edgecolor=team_color,
                 zorder=2, ax=ax)
    
    pitch.scatter(pass_incomp.end_x, pass_incomp.end_y,
                 s=30, color=bg_color, edgecolor='red',
                 alpha=0.25, zorder=2, ax=ax)
    
    pitch.scatter(key_passes.end_x, key_passes.end_y,
                 s=40, color=bg_color, edgecolor=violet_color,
                 linewidth=1.5, zorder=2, ax=ax)
    
    pitch.scatter(assists.end_x, assists.end_y,
                 s=50, color=bg_color, edgecolor=green_color,
                 linewidth=1.5, zorder=2, ax=ax)
    
    # Add statistics text
    if is_away:
        ax.text(85, -3, f'Successful Pass: {len(pass_comp)}',
                color=team_color, va='center', ha='left', fontsize=12)
        ax.text(120, -3, f'Unsuccessful Pass: {len(pass_incomp)}',
                color='gray', va='center', ha='left', fontsize=12)
        ax.text(85, -8, f'Key Pass: {len(key_passes)}',
                color=violet_color, va='center', ha='left', fontsize=12)
        ax.text(120, -8, f'Assist: {len(assists)}',
                color=green_color, va='center', ha='left', fontsize=12)
        ax.text(0, -5, "<----- Attacking Direction",
                color=team_color, fontsize=15, va='center', ha='right')
    else:
        ax.text(80, 83, f'Successful Pass: {len(pass_comp)}',
                color=team_color, va='center', ha='right', fontsize=12)
        ax.text(120, 83, f'Unsuccessful Pass: {len(pass_incomp)}',
                color='gray', va='center', ha='right', fontsize=12)
        ax.text(80, 88, f'Key Pass: {len(key_passes)}',
                color=violet_color, va='center', ha='right', fontsize=12)
        ax.text(120, 88, f'Assist: {len(assists)}',
                color=green_color, va='center', ha='right', fontsize=12)
        ax.text(0, 85, "Attacking Direction ----->",
                color=team_color, fontsize=15, va='center', ha='left')
    
    # Set title
    ax.set_title(f"{player_name} PassMap",
                 color=team_color, fontsize=25, fontweight='bold')
    
    return fig
def get_short_name(full_name):
    """Convert player name to shorter version"""
    if not isinstance(full_name, str):
        return None
    parts = full_name.split()
    if len(parts) == 1:
        return full_name
    elif len(parts) == 2:
        return parts[0][0] + ". " + parts[1]
    else:
        return parts[0][0] + ". " + parts[1][0] + ". " + " ".join(parts[2:])
def create_received_passes_map(df, player_name, is_away=False):
    """
    Create a visualization of passes received by a specific player.
    
    Args:
        df (DataFrame): Match event data
        player_name (str): Name of the player to analyze
        is_away (bool): Whether the player is from the away team
    """
    # Constants
    bg_color = '#2A5A27'
    line_color = '#FFFFFF'
    team_color = '#C0C0C0' if is_away else '#FFD700'  # Silver for away, Gold for home
    violet_color = '#8A2BE2'  # For key passes
    green_color = '#00FF00'   # For assists
    
    # Create figure and pitch
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=bg_color)
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True,
                 pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()
    
    # Filter passes received by the player
    received_passes = df[
        (df['typeId'] == 'Pass') & 
        (df['outcome'] == 'Successful') & 
        (df['receiver'] == player_name)
    ]
    
    # Categorize received passes
    key_passes_received = received_passes[received_passes['keyPass'] == 1]
    assists_received = received_passes[received_passes['assist'] == 1]
    normal_passes = received_passes[
        (received_passes['keyPass'] != 1) & 
        (received_passes['assist'] != 1)
    ]
    
    # Draw pass lines
    pitch.lines(normal_passes.x, normal_passes.y,
               normal_passes.end_x, normal_passes.end_y,
               lw=3, transparent=True, comet=True,
               color=team_color, ax=ax, alpha=0.5)
    
    pitch.lines(key_passes_received.x, key_passes_received.y,
               key_passes_received.end_x, key_passes_received.end_y,
               lw=4, transparent=True, comet=True,
               color=violet_color, ax=ax, alpha=0.75)
    
    pitch.lines(assists_received.x, assists_received.y,
               assists_received.end_x, assists_received.end_y,
               lw=4, transparent=True, comet=True,
               color=green_color, ax=ax, alpha=0.75)
    
    # Add end points for received passes
    pitch.scatter(normal_passes.end_x, normal_passes.end_y,
                 s=30, edgecolor=team_color, linewidth=1,
                 color=bg_color, zorder=2, ax=ax)
    
    pitch.scatter(key_passes_received.end_x, key_passes_received.end_y,
                 s=40, edgecolor=violet_color, linewidth=1.5,
                 color=bg_color, zorder=2, ax=ax)
    
    pitch.scatter(assists_received.end_x, assists_received.end_y,
                 s=50, edgecolors=green_color, linewidths=1,
                 marker='football', c=bg_color, zorder=2, ax=ax)
    
    # Add average position lines
    if len(received_passes) > 0:
        avg_endY = received_passes['end_y'].median()
        avg_endX = received_passes['end_x'].median()
        ax.axvline(x=avg_endX, ymin=0, ymax=68, color='gray',
                  linestyle='--', alpha=0.6, linewidth=2)
        ax.axhline(y=avg_endY, xmin=0, xmax=105, color='gray',
                  linestyle='--', alpha=0.6, linewidth=2)
    
    # Add title and statistics
    name_show = get_short_name(player_name)
    total_received = len(received_passes)
    key_passes_count = len(key_passes_received)
    
    ax.set_title(f"{name_show} Passes Received",
                 color=team_color, fontsize=25, fontweight='bold')
    
    stats_text = f'Passes Received: {total_received} (Key Passes: {key_passes_count})'
    if is_away:
        ax.text(60, -2, stats_text,
                color=line_color, fontsize=15,
                ha='center', va='center')
        ax.text(0, -5, "<----- Attacking Direction",
                color=team_color, fontsize=15,
                va='center', ha='right')
    else:
        ax.text(60, 83, stats_text,
                color=line_color, fontsize=15,
                ha='center', va='center')
        ax.text(0, 85, "Attacking Direction ----->",
                color=team_color, fontsize=15,
                va='center', ha='left')
    
    return fig

def draw_progressive_pass_map(ax, df, team_name, col):
    unique_teams = df['team_name'].unique()
    
    if len(unique_teams) < 2:
        print("Not enough teams to analyze.")
        return  # or raise an Exception

    pitch = Pitch(pitch_type='statsbomb', pitch_color=bg_color, line_color=line_color, linewidth=2, corner_arcs=True)
    pitch.draw(ax=ax)

    if team_name == unique_teams[1]:  # away team
        ax.invert_xaxis()
        ax.invert_yaxis()

    # filtering the progressive passes only
    dfpro = df[(df['team_name'] == team_name) & (df['pro'] >= 9.144) & (df['cross'] != 'Cross') & (df['x'] <= 115) & (df['x'] >= 40)]
    pro_count = len(dfpro)

    # calculating the counts
    left_pro = len(dfpro[dfpro['y'] >= 45.33])
    mid_pro = len(dfpro[(dfpro['y'] >= 22.67) & (dfpro['y'] < 45.33)])
    right_pro = len(dfpro[(dfpro['y'] >= 0) & (dfpro['y'] < 22.67)])
    left_percentage = round((left_pro / pro_count) * 100) if pro_count > 0 else 0
    mid_percentage = round((mid_pro / pro_count) * 100) if pro_count > 0 else 0
    right_percentage = round((right_pro / pro_count) * 100) if pro_count > 0 else 0

    ax.hlines(80 / 3, xmin=0, xmax=120, colors=line_color, linestyle='dashed', alpha=0.35)
    ax.hlines(160 / 3, xmin=0, xmax=120, colors=line_color, linestyle='dashed', alpha=0.35)

    # showing the texts in the pitch
    if team_name == unique_teams[0]:  # home team
        ax.text(27, 80 / 6, f'{right_pro}\n({right_percentage}%)', color=col, fontsize=24, va='center', ha='center')
        ax.text(27, 40, f'{mid_pro}\n({mid_percentage}%)', color=col, fontsize=24, va='center', ha='center')
        ax.text(27, 400 / 6, f'{left_pro}\n({left_percentage}%)', color=col, fontsize=24, va='center', ha='center')
    else:
        ax.text(27, 80 / 6, f'{right_pro}\n({right_percentage}%)', color=col, fontsize=24, va='center', ha='center')
        ax.text(27, 40, f'{mid_pro}\n({mid_percentage}%)', color=col, fontsize=24, va='center', ha='center')
        ax.text(27, 400 / 6, f'{left_pro}\n({left_percentage}%)', color=col, fontsize=24, va='center', ha='center')

    # plotting the passes
    pitch.lines(dfpro.x, dfpro.y, dfpro.end_x, dfpro.end_y, lw=3.5, transparent=True, comet=True, color=col, ax=ax, alpha=0.5)
    pitch.scatter(dfpro.end_x, dfpro.end_y, s=35, edgecolor=col, linewidth=1, color=bg_color, zorder=2, ax=ax)

    counttext = f"{pro_count} Progressive Passes"

    # Heading and other texts
    if team_name == unique_teams[0]:  # home team
        ax.text(0, 85, "Attacking Direction --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"{team_name}\n{counttext}", color=line_color, fontsize=25, fontweight='bold')
    else:
        ax.text(0, -5, "<--- Attacking Direction", color=col, size=15, ha='right', va='center')
        ax.set_title(f"{team_name}\n{counttext}", color=line_color, fontsize=25, fontweight='bold')


def draw_pass_map(ax, df, title, col, home_team, away_team, home_col, away_col):
    pitch = Pitch(pitch_type='statsbomb', pitch_color=bg_color, line_color=line_color, linewidth=2, corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_facecolor(bg_color)
    if title == away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()

    # setting the count variables
    z14 = 0
    hs = 0

    # iterating each pass and according to the conditions plotting only zone14 and half spaces passes
    for index, row in df.iterrows():
        if row['end_x'] >= 80 and row['end_x'] <= 100 and row['end_y'] >= 80/3 and row['end_y'] <= 160/3:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['end_x'], row['end_y']), 
                                          arrowstyle='->', alpha=0.75, mutation_scale=20, 
                                          color='#00D9FF', linewidth=1.5)
            ax.add_patch(arrow)
            z14 += 1
        if row['end_x'] >= 80 and row['end_y'] >= 80/6 and row['end_y'] <= 80/3:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['end_x'], row['end_y']), 
                                          arrowstyle='->', alpha=0.75, mutation_scale=20, 
                                          color=col, linewidth=1.5)
            ax.add_patch(arrow)
            hs += 1
        if row['end_x'] >= 80 and row['end_y'] >= 160/3 and row['end_y'] <= 66.67:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['end_x'], row['end_y']), 
                                          arrowstyle='->', alpha=0.75, mutation_scale=20, 
                                          color=col, linewidth=1.5)
            ax.add_patch(arrow)
            hs += 1

    # coloring those zones in the pitch
    y_z14 = [80/3, 80/3, 160/3, 160/3]
    x_z14 = [80, 100, 100, 80]
    ax.fill(x_z14, y_z14, '#00D9FF', alpha=0.2, label='Zone14')

    y_rhs = [80/6, 80/6, 80/3, 80/3]
    x_rhs = [80, 120, 120, 80]
    ax.fill(x_rhs, y_rhs, col, alpha=0.2, label='HalfSpaces')

    y_lhs = [160/3, 160/3, 66.67, 66.67]
    x_lhs = [80, 120, 120, 80]
    ax.fill(x_lhs, y_lhs, col, alpha=0.2, label='HalfSpaces')

    # showing the counts in an attractive way
    z14name = "Zone14"
    hsname = "H.Spaces"
    z14count = f"{z14}"
    hscount = f"{hs}"
    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color),
                path_effects.Normal()]
    ax.scatter(24, 24, color=col, s=15000, edgecolor=line_color, linewidth=2, alpha=1, marker='h')
    ax.scatter(24, 56, color='orange', s=15000, edgecolor=line_color, linewidth=2, alpha=1, marker='h')
    ax.text(24, 24-5, hsname, fontsize=20, color="w", ha='center', va='center')
    ax.text(24, 56-5, z14name, fontsize=20, color="w", ha='center', va='center')
    ax.text(24, 24+2, hscount, fontsize=40, color="w", ha='center', va='center')
    ax.text(24, 56+2, z14count, fontsize=40, color="w", ha='center', va='center')

    # Headings and other texts
    if col == home_col:
        ax.text(0, 85, "Attacking Direction --->", color=home_col, size=15, ha='left', va='center')
        ax.set_title(f"{home_team}\nZone14 & Half spaces. Pass", color=line_color, fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "<--- Attacking Direction", color=away_col, size=15, ha='right', va='center')
        ax.set_title(f"{away_team}\nZone14 & Half spaces. Pass", color=line_color, fontsize=25, fontweight='bold', path_effects=path_eff)
def HighTO(ax, df):

    unique_teams = df['team_name'].unique()
    
    if len(unique_teams) < 2:
        print("Not enough teams to analyze.")
        return  # or raise an Exception
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True, pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    ax.set_ylim(-0.5,80.5)
    ax.set_xlim(-0.5,120.5)

    teams = df['team_name'].unique()
    home_team = teams[0]
    away_team = teams[1]
    home_col = '#FFD700'  # Gold for home team
    away_col = '#C0C0C0'  # Silver for away team

    # filtering the high turnovers
    home_TO = df[(df['team_name']==home_team) & 
                 ((df['typeId']=='Ball recovery') | (df['typeId']=='Interception')) & 
                 (df['x']>=80)]
    away_TO = df[(df['team_name']==away_team) & 
                 ((df['typeId']=='Ball recovery') | (df['typeId']=='Interception')) & 
                 (df['x']>=80)]

    home_TO['distance'] = ((home_TO['x'] - 120)**2 + (home_TO['y'] - 40)**2)**0.5
    home_TO = home_TO[home_TO['distance']<=47]
    away_TO['distance'] = ((away_TO['x'] - 120)**2 + (away_TO['y'] - 40)**2)**0.5
    away_TO = away_TO[away_TO['distance']<=47]

    hto_count = len(home_TO)
    ato_count = len(away_TO)

    # Plot turnovers
    ax.scatter((120-home_TO.x), (80-home_TO.y), s=250, c=home_col, edgecolor=line_color, marker='o', linewidth=2)
    ax.scatter((away_TO.x), (away_TO.y), s=250, c=away_col, edgecolor=line_color, marker='o', linewidth=2)

    # Draw circles
    left_circle = plt.Circle((0,40), 47, color=home_col, fill=True, alpha=0.25, linestyle='dashed', linewidth=3)
    ax.add_artist(left_circle)
    right_circle = plt.Circle((120,40), 47, color=away_col, fill=True, alpha=0.25, linestyle='dashed', linewidth=3)
    ax.add_artist(right_circle)
    
    ax.set_aspect('equal', adjustable='box')
    
    # Add labels
    ax.text(0, 82, f"{home_team}\nHigh Turnovers: {hto_count}", color=home_col, size=20, 
            ha='left', va='bottom', fontweight='bold')
    ax.text(120, 82, f"{away_team}\nHigh Turnovers: {ato_count}", color=away_col, size=20, 
            ha='right', va='bottom', fontweight='bold')
    
def chance_creating_zone(ax, df, title, cm, tcm, home_team, away_team):
    pitch = Pitch(pitch_type='statsbomb', line_color=line_color, corner_arcs=True, line_zorder=2, pitch_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)
    if title == away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cc = 0
    pearl_earring_cmap = cm
    df = df[df['end_x'] > 0]
    bin_statistic = pitch.bin_statistic(df.x, df.y, bins=(6,5), statistic='count', normalize=False)
    pitch.heatmap(bin_statistic, ax=ax, cmap=pearl_earring_cmap, edgecolors='#d9d9d9')
    pitch.scatter(df.x, df.y, c='gray', s=5, ax=ax)
    
    for index, row in df.iterrows():
        if row['assist'] == 1 and row['end_x'] > 0 and row['end_y'] > 0:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['end_x'], row['end_y']), 
                                          arrowstyle='->', mutation_scale=20, color='#00ff00', 
                                          linewidth=1.25, alpha=1)
            ax.add_patch(arrow)
            cc += 1
        if row['assist'] != 1 and row['end_x'] > 0 and row['end_y'] > 0:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['end_x'], row['end_y']), 
                                          arrowstyle='->', mutation_scale=20, color='#00D9FF', 
                                          linewidth=1.25, alpha=1)
            ax.add_patch(arrow)
            cc += 1
    
    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]
    labels = pitch.label_heatmap(bin_statistic, color=line_color, fontsize=25, ax=ax, 
                                ha='center', va='center', str_format='{:.0f}',
                                exclude_zeros=True, path_effects=path_eff)

    # Headings and other texts
    if tcm == '#FFD700':  # home team
        ax.text(120, 83.5, "cyan arrow = key pass\ngreen arrow = assist", 
                color='#FFD700', size=15, ha='right', va='center')
        ax.text(0, 85, "Attacking Direction --->", color='#FFD700', size=15, ha='left', va='center')
        ax.text(60, -2, f"Total Chances Created = {cc}", color=tcm, fontsize=15, ha='center', va='center')
        ax.set_title(f"{home_team}\nChance Creating Zone", color=line_color, fontsize=25, 
                    fontweight='bold', path_effects=path_eff)
    else:
        ax.text(120, -3.5, "Cyan arrow = key pass\ngreen arrow = assist", 
                color='#C0C0C0', size=15, ha='left', va='center')
        ax.text(0, -5, "<--- Attacking Direction", color='#C0C0C0', size=15, ha='right', va='center')
        ax.text(60, 82, f"Total Chances Created = {cc}", color=tcm, fontsize=15, ha='center', va='center')
        ax.set_title(f"{away_team}\nChance Creating Zone", color=line_color, fontsize=25, 
                    fontweight='bold', path_effects=path_eff)
    



def create_detailed_match_analysis(df):
    teams = df['team_name'].unique()
    
    if len(teams) < 2:
        print("Not enough teams to analyze.")
        return None
    
    teams = teams.tolist()
    home_team = teams[0]
    away_team = teams[1]
    
    # Set up the figure with a 3x2 grid
    fig = plt.figure(figsize=(40, 50), facecolor=bg_color)
    fig.suptitle('Detailed Match Analysis', color=line_color, fontsize=28, x=0.37,y=0.92)
    
    # Define team colors
    home_col = '#FFD700'  # Gold for home team
    away_col = '#C0C0C0'  # Silver for away team
    
    # Create grid
    gs = fig.add_gridspec(5, 3, hspace=0.4, wspace=0.3)
    
    # Progressive Passes Maps
    ax1 = fig.add_subplot(gs[0, 0])
    draw_progressive_pass_map(ax1, df, home_team, home_col)
    
    ax2 = fig.add_subplot(gs[0, 1])
    draw_progressive_pass_map(ax2, df, away_team, away_col)
    
    # Zone 14 & Half Spaces
    dfhp = df[(df['team_name'] == home_team) & (df['typeId'] == "Pass") & 
              (df['outcome'] == "Successful") & (df['x'] <= 115)]
    dfap = df[(df['team_name'] == away_team) & (df['typeId'] == "Pass") & 
              (df['outcome'] == "Successful") & (df['x'] <= 115)]
    
    ax3 = fig.add_subplot(gs[1, 0])
    draw_pass_map(ax3, dfhp, home_team, home_col, home_team, away_team, home_col, away_col)
    
    ax4 = fig.add_subplot(gs[1, 1])
    draw_pass_map(ax4, dfap, away_team, away_col, home_team, away_team, home_col, away_col)
    
    # Chance Creation Analysis
    # Filter key passes and assists
    dfkph = df[(df['team_name'] == home_team) & (df['keyPass'] == 1)]
    dfkpa = df[(df['team_name'] == away_team) & (df['keyPass'] == 1)]
    dfassh = df[(df['team_name'] == home_team) & (df['assist'] == 1)]
    dfassa = df[(df['team_name'] == away_team) & (df['assist'] == 1)]
    
    # Concatenate key passes and assists
    dfchch = pd.concat([dfkph, dfassh])
    dfchca = pd.concat([dfkpa, dfassa])
    
    # Create custom colormaps
    pearl_earring_cmaph = LinearSegmentedColormap.from_list("Pearl Earring - Home", 
                                                           [bg_color, home_col], N=20)
    pearl_earring_cmapa = LinearSegmentedColormap.from_list("Pearl Earring - Away", 
                                                           [bg_color, away_col], N=20)
    
    # Add chance creation plots
    ax5 = fig.add_subplot(gs[2, 0])
    chance_creating_zone(ax5, dfchch, home_team, pearl_earring_cmaph, home_col, home_team, away_team)
    
    ax6 = fig.add_subplot(gs[2, 1])
    chance_creating_zone(ax6, dfchca, away_team, pearl_earring_cmapa, away_col, home_team, away_team)
    
    # Add High Turnovers plot
    ax7 = fig.add_subplot(gs[3, 0:2])  # Create a new row for the high turnovers plot
    HighTO(ax7, df)
    
    plt.tight_layout()
    return fig
def get_shorter_name(name):
    """Convert player name to shorter version"""
    parts = name.split()
    if len(parts) > 1:
        return f"{parts[0][0]}. {parts[-1]}"
    return name

def get_passes_df(df):
    df["receiver"] = df["shortName"].shift(-1)
    passes_ids = df.index[df['typeId'] == 'Pass']
    df_passes = df.loc[passes_ids, ["id", "x", "y", "end_x", "end_y", "team_name", "shortName", "shorter name", "receiver", "typeId", "outcome", "timeMin"]]
    return df_passes

def get_passes_between_df(team_id, passes_df, start_minute, end_minute):
    team_passes_df = passes_df[
        (passes_df['team_name'] == team_id) & 
        (passes_df['timeMin'] >= start_minute) & 
        (passes_df['timeMin'] < end_minute)
    ]
    
    passes_player_ids_df = team_passes_df.loc[:, ['id', 'shortName', "shorter name", 'receiver', 'team_name']]
    passes_player_ids_df['shortName'] = passes_player_ids_df['shortName'].astype(str)
    passes_player_ids_df['receiver'] = passes_player_ids_df['receiver'].astype(str)
    
    passes_player_ids_df['pos_max'] = passes_player_ids_df[['shortName', 'receiver']].max(axis='columns')
    passes_player_ids_df['pos_min'] = passes_player_ids_df[['shortName', 'receiver']].min(axis='columns')
    
    average_locs_and_count_df = team_passes_df.groupby('shortName').agg({
        'x': ['median'],
        'y': ['median', 'count']
    }).rename(columns={'id': 'pass_count'})
    average_locs_and_count_df.columns = ['pass_avg_x', 'pass_avg_y', 'count']
    
    passes_between_df = passes_player_ids_df.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between_df.rename({'id': 'pass_count'}, axis='columns', inplace=True)
    
    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_min', right_index=True)
    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_max', right_index=True, suffixes=['', '_end'])
    
    return passes_between_df, average_locs_and_count_df

def attack_map(df, team_id):
    # Filter shots
    shot_types = ['Goal', 'Miss', 'Attempt Saved', 'Post']
    shots_df = df[df['typeId'].isin(shot_types)].copy()
    shots_df.reset_index(drop=True, inplace=True)
    #prog
    dfpro = df[(df['team_name']==team_id) & (df['pro'] >= 9.144) & (df['cross']!='Cross') & (df['x']<=115) & (df['x']>=40)& (df['outcome']=="Successful")]
    #assiste and key pass 
    key= df[(df['team_name']==team_id) & ((df['keyPass']==1))& (df['outcome']=="Successful")]
    assist= df[(df['team_name']== team_id) & ((df['assist']==1))& (df['outcome']=="Successful")]
    # corss
    cross=df[(df['team_name']==team_id) & (df['cross']=='Cross')]
    #fianalt third passes
    passses=df[(df["team_name"]==team_id) & (df['typeId']=='Pass') & (df['outcome']=="Successful")]
    final_pass= passses[passses["end_x"]  >= 80 ]
    # Create figure
    robotto_regular = FontManager()
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),path_effects.Normal()]
    fig, ax = plt.subplots(figsize=(16, 10), facecolor=bg_color)
    fig.suptitle(f"{team_id} - Shot Map", fontsize=16, color=line_color, y=0.95)
    
    # Set up the pitch
    pitch = VerticalPitch(pitch_type='statsbomb', corner_arcs=True, half=True,
                 pitch_color=bg_color, line_color=line_color, linewidth=1)
    fig, axs= pitch.grid(ncols=2,grid_height=0.6, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
    # Filter shots by type
    goals = shots_df[(shots_df['team_name'] == team_id) & (shots_df['typeId'] == 'Goal')]
    posts = shots_df[(shots_df['team_name'] == team_id) & (shots_df['typeId'] == 'Post')]
    saves = shots_df[(shots_df['team_name'] == team_id) & (shots_df['typeId'] == 'Attempt Saved')]
    misses = shots_df[(shots_df['team_name'] == team_id) & (shots_df['typeId'] == 'Miss')]
    
    # Plot different types of shots
    pitch.scatter(
        goals.x,
        goals.y,
        s=200,
        marker='football',
        edgecolors=line_color,
        facecolors='none',
        linewidths=2,
        alpha=1,
        ax=axs["pitch"][0],
        label='Goal'
    )
    
    pitch.scatter(
        posts.x,
        posts.y,
        s=200,
        marker='o',
        edgecolors=line_color,
        facecolors=line_color,
        alpha=0.6,
        ax=axs["pitch"][0],
        label='Post'
    )
    
    pitch.scatter(
        saves.x,
        saves.y,
        s=200,
        marker='o',
        edgecolors=line_color,
        facecolors='none',
        hatch='///////',
        alpha=0.6,
        ax=axs["pitch"][0],
        label='Saved'
    )
    
    pitch.scatter(
        misses.x,
        misses.y,
        s=200,
        marker='o',
        edgecolors=line_color,
        facecolors='none',
        alpha=0.6,
        ax=axs["pitch"][0],
        label='Miss'
    )
    # plotting the passes
    pitch.lines(key['x'], key['y'], key['end_x'], key['end_y'], lw=3.5, transparent=True, comet=True, color=line_color, ax=axs["pitch"][0], alpha=0.5)
    # plotting some scatters at the end of each pass
    pitch.scatter(key["end_x"], key["end_y"], s=35, edgecolor=line_color, linewidth=1, 
              color=bg_color, zorder=2, ax=axs['pitch'][0], label="Key Pass")
    pitch.lines(assist.x, assist.y, assist.end_x, assist.end_y, lw=3.5, transparent=True, comet=True, color=pass_color, ax=axs["pitch"][0], alpha=0.5)
    # plotting some scatters at the end of each pass
    pitch.scatter(assist["end_x"], assist["end_y"], s=35, edgecolor=pass_color, linewidth=1, 
              color=bg_color, zorder=2, ax=axs['pitch'][0], label="Assist")

    #pitch.lines(final_pass.x, final_pass.y, final_pass.end_x, final_pass.end_y, lw=3.5, transparent=True, comet=True, color=line_color, ax=axs["pitch"][1], alpha=0.5)
    # plotting some scatters at the end of each pass
   # pitch.scatter(final_pass["end_x"], final_pass["end_y"], s=35, edgecolor=line_color, linewidth=1, 
             # color=bg_color, zorder=2, ax=axs['pitch'][1])

    pitch.lines(cross.x, cross.y, cross.end_x, cross.end_y, lw=3.5, transparent=True, comet=True, color=line_color, ax=axs["pitch"][1], alpha=0.5)
    # plotting some scatters at the end of each pass
    pitch.scatter(cross["end_x"], cross["end_y"], s=35, edgecolor=line_color, linewidth=1, 
              color=bg_color, zorder=2, ax=axs['pitch'][1])
    axs['pitch'][0].set_title("Shots/Key Passes",color=line_color,
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)
    axs['pitch'][1].set_title('Crosses',color=line_color,
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)

    #pitch.lines(dfpro.x, dfpro.y, dfpro.end_x, dfpro.end_y, lw=3.5, transparent=True, comet=True, color=line_color, ax=axs["pitch"][1], alpha=0.5)
    # plotting some scatters at the end of each pass
    #pitch.scatter(dfpro["end_x"], dfpro["end_y"], s=35, edgecolor=line_color, linewidth=1, 
              #color=bg_color, zorder=2, ax=axs['pitch'][1])
      

    



    axs["pitch"][0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
              ncol=4, facecolor=bg_color, edgecolor=line_color, labelcolor=line_color)
    
    fig.set_facecolor(bg_color)
    plt.tight_layout()
    return fig


def create_defensive_actions_map(df, team_id):
    # Filter defensive actions
    defensive_types = ['Tackle', 'Clearance', 'Save', 'Challenge']
    defensive_df = df[df['typeId'].isin(defensive_types)].copy()
    defensive_df = defensive_df[defensive_df['team_name'] == team_id]
    defensive_df.reset_index(drop=True, inplace=True)
    
    # Create figure with reduced size
    pitch = pitch = VerticalPitch(pitch_type='statsbomb', corner_arcs=True,
                         pitch_color=bg_color, line_color=line_color, line_zorder=2)
    fig, axs= pitch.grid(ncols=2,grid_height=0.8, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
    fig.suptitle(f"{team_id} - Defensive Actions Map", fontsize=14, color=line_color, y=0.95)  # Reduced font size
    
    # Set up the pitch
    
    
    # Define markers and colors for different actions
    markers = {
        'Tackle': '^',
        'Clearance': 's',
        'Save': '*',
        'Challenge': 'D'
    }
    
    colors = {
        'Tackle': '#ff0000',
        'Clearance': '#00ff00',
        'Save': '#0000ff',
        'Challenge': '#ffff00'
    }
    
    # Plot each type of defensive action with reduced marker size
    for action_type in defensive_types:
        actions = defensive_df[defensive_df['typeId'] == action_type]
        pitch.scatter(
            actions.x,
            actions.y,
            s=50,  # Reduced from 200
            marker=markers[action_type],
            edgecolors=colors[action_type],
            facecolors='none',
            linewidths=1.5,  # Reduced from 2
            alpha=0.7,
            ax=axs['pitch'][0],
            label=action_type
        )
        bin_statistic = pitch.bin_statistic(defensive_df.x, defensive_df.y, statistic='count', bins=(25, 25))
        bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
        pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'][1], cmap='hot', edgecolors='#22312b',label=f' entries')
        axs["pitch"][0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=4,
            facecolor=bg_color, edgecolor=line_color, labelcolor=line_color,
             fontsize=10)  # Added smaller font size
    
    fig.set_facecolor(bg_color)
    plt.tight_layout()
    return fig



def create_high_recoveries_map(df, team_id):
    # Filter high recovery actions
    recovery_types = ['Ball recovery', 'Dispossessed', 'Claim']
    recovery_df = df[df['typeId'].isin(recovery_types)].copy()
    recovery_df = recovery_df[recovery_df['team_name'] == team_id]
    recovery_df.reset_index(drop=True, inplace=True)
    
    # Create pitch
    pitch = VerticalPitch(pitch_type='statsbomb', corner_arcs=True,
                         pitch_color=bg_color, line_color=line_color, line_zorder=2)
    fig, axs = pitch.grid(ncols=2, grid_height=0.8, title_height=0.05, 
                          axis=False, endnote_height=0.04, title_space=0, 
                          endnote_space=0, grid_width=0.88, figheight=10)
    
    fig.suptitle(f"{team_id} - Recoveries Map", fontsize=14, color=line_color, y=0.95)
    
    # Define markers and colors for different recovery actions
    markers = {
        'Ball recovery': 'o',
        'Dispossessed': 'X',
        'Claim': 's'
    }
    
    colors = {
        'Ball recovery': '#1f77b4',  # Blue
        'Dispossessed': '#ff7f0e',  # Orange
        'Claim': '#2ca02c'  # Green
    }
    
    # Plot each type of recovery action
    for action_type in recovery_types:
        actions = recovery_df[recovery_df['typeId'] == action_type]
        pitch.scatter(
            actions.x,
            actions.y,
            s=50,  # Reduced marker size
            marker=markers[action_type],
            edgecolors=colors[action_type],
            facecolors='none',
            linewidths=1.5,
            alpha=0.7,
            ax=axs['pitch'][0],
            label=action_type
        )
    
    # Create heatmap
    bin_statistic = pitch.bin_statistic(recovery_df.x, recovery_df.y, statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pitch.heatmap(bin_statistic, ax=axs['pitch'][1], cmap='hot', edgecolors='#22312b')
    
    # Add legend
    axs["pitch"][0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3,
                           facecolor=bg_color, edgecolor=line_color, labelcolor=line_color,
                           fontsize=10)
    
    fig.set_facecolor(bg_color)
    plt.tight_layout()
    return fig


def create_set_pieces_and_cards_chart(df):
    # Filter relevant events
    events = ['Corner Awarded', 'Card', 'Offside provoked', 'Offside']
    events_df = df[df['typeId'].isin(events)].copy()
    
    # Create figure with dark theme
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=bg_color)
    fig.suptitle('Set Pieces & Cards Analysis by Team', fontsize=16, color=line_color, y=0.95)
    
    # Get unique teams
    teams = events_df['team_name'].unique()
    
    if len(teams) == 0:
        # No data available
        ax.text(0.5, 0.5, 'No event data available', 
                ha='center', va='center', color=line_color,
                fontsize=14, transform=ax.transAxes)
        ax.set_facecolor(bg_color)
        plt.tight_layout()
        return fig
    
    # Set up the positions of the bars
    x = np.arange(len(events))
    width = 0.35 if len(teams) > 1 else 0.5  # Adjust width based on number of teams
    
    # Calculate counts for each team and event
    for idx, team in enumerate(teams):
        team_data = []
        for event in events:
            count = len(events_df[(events_df['team_name'] == team) & 
                                (events_df['typeId'] == event)])
            team_data.append(count)
            
        # Position bars based on number of teams
        if len(teams) > 1:
            offset = width/2 * (-1 if idx == 0 else 1)
        else:
            offset = 0
            
        bars = ax.bar(x + offset, team_data, width, 
                     label=team,
                     color='#FFD700' if idx == 0 else '#C0C0C0',
                     alpha=0.7,
                     edgecolor=line_color)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       color=line_color, fontsize=10)
    
    # Customize the chart
    ax.set_ylabel('Number of Events', color=line_color, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(events, rotation=45, ha='right', color=line_color)
    
    # Customize grid and background
    ax.set_facecolor(bg_color)
    ax.grid(True, linestyle='--', alpha=0.3, color=line_color)
    
    # Customize legend if there's more than one team
    if len(teams) > 1:
        ax.legend(facecolor=bg_color, edgecolor=line_color, labelcolor=line_color)
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_color(line_color)
        spine.set_linewidth(0.5)
    
    # Set tick colors
    ax.tick_params(colors=line_color)
    
    plt.tight_layout()
    return fig


def pass_network_visualization(ax, passes_between_df, average_locs_and_count_df, color_val, team_id, period=""):
    MAX_LINE_WIDTH = 15
    MIN_TRANSPARENCY = 0.05
    MAX_TRANSPARENCY = 0.85
    
    if len(passes_between_df) > 0:
        base_color = to_rgba(color_val)
        color = np.array([base_color for _ in range(len(passes_between_df))])
        c_transparency = passes_between_df.pass_count / passes_between_df.pass_count.max()
        c_transparency = (c_transparency * (MAX_TRANSPARENCY - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
        color[:, 3] = c_transparency
        passes_between_df['width'] = (passes_between_df.pass_count / passes_between_df.pass_count.max() * MAX_LINE_WIDTH)
    else:
        color = np.array([to_rgba(color_val)])
    
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True, pitch_color=bg_color, line_color=line_color, linewidth=1)
    pitch.draw(ax=ax)
    
    if len(passes_between_df) > 0:
        pitch.lines(
            passes_between_df.pass_avg_x,
            passes_between_df.pass_avg_y,
            passes_between_df.pass_avg_x_end,
            passes_between_df.pass_avg_y_end,
            lw=passes_between_df.width,
            color=color,
            zorder=1,
            ax=ax
        )
    
    average_locs_and_count_df = average_locs_and_count_df.reset_index()
    for _, row in average_locs_and_count_df.iterrows():
        marker = 's' if row['shortName'] in sub_list else 'o'
        pitch.scatter(
            row['pass_avg_x'],
            row['pass_avg_y'],
            s=1000,
            marker=marker,
            color=bg_color,
            edgecolor=line_color,
            linewidth=2,
            alpha=1,
            ax=ax
        )
    
    average_locs_and_count_df['shorter name'] = average_locs_and_count_df['shortName'].apply(get_shorter_name)
    for _, row in average_locs_and_count_df.iterrows():
        pitch.annotate(
            row["shorter name"],
            xy=(row.pass_avg_x, row.pass_avg_y),
            c=line_color,
            ha='center',
            va='center',
            size=8,
            ax=ax
        )
    
    if len(average_locs_and_count_df) > 0:
        avgph = round(average_locs_and_count_df['pass_avg_x'].median(), 2)
        ax.axvline(x=avgph, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.text(2, 2, f"{period}", color=color_val, size=10, ha='left', va='top')
    if period == "0-15'":
        ax.text(-2, 85, "Attacking Direction --->", color=color_val, size=12, ha='left', va='center')
        ax.text(60, 85, f"{team_id}", color=color_val, size=12, ha='right', va='center')

def create_15min_passing_networks(df, team_id, col=line_color):
    passes_df = get_passes_df(df)
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12), facecolor=bg_color)
    fig.suptitle(f"{team_id} - Passing Networks by 15-minute Intervals", 
                 fontsize=16, color=line_color, y=0.95)
    
    fig.patch.set_facecolor(bg_color)
    
    intervals = [
        (0, 15, "0-15'"),
        (15, 30, "15-30'"),
        (30, 45, "30-45'"),
        (45, 60, "45-60'"),
        (60, 75, "60-75'"),
        (75, 90, "75-90'")
    ]
    
    for idx, (start, end, period) in enumerate(intervals):
        row = idx // 3
        col = idx % 3
        
        axes[row, col].set_facecolor(bg_color)
        
        passes_between_df, average_locs_and_count_df = get_passes_between_df(
            team_id,
            passes_df,
            start,
            end
        )
        
        pass_network_visualization(
            axes[row, col],
            passes_between_df,
            average_locs_and_count_df,
            line_color,
            team_id,
            period
        )
    
    plt.tight_layout()
    return fig




## PLAYER PERFORMANCE FUNCTIONS 
def create_player_stats_chart(player_data):
    # Count different types of events
    offensive_events = ['Pass', 'Take On', 'Goal', 'Miss', 'Attempt Saved']
    defensive_events = ['Tackle', 'Interception', 'Ball recovery', 'Clearance', 'Aerial']
    
    # Create figure with dark theme
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor=bg_color)
    
    # Offensive Stats
    off_stats = {event: len(player_data[player_data['typeId'] == event]) for event in offensive_events}
    off_events = list(off_stats.keys())
    off_counts = list(off_stats.values())
    
    # Defensive Stats
    def_stats = {event: len(player_data[player_data['typeId'] == event]) for event in defensive_events}
    def_events = list(def_stats.keys())
    def_counts = list(def_stats.values())
    
    # Plot offensive stats
    bars1 = ax1.bar(off_events, off_counts, color='#FFD700', alpha=0.7)
    ax1.set_title('Offensive Actions', color=line_color, pad=20)
    ax1.set_facecolor(bg_color)
    
    # Plot defensive stats
    bars2 = ax2.bar(def_events, def_counts, color='#C0C0C0', alpha=0.7)
    ax2.set_title('Defensive Actions', color=line_color, pad=20)
    ax2.set_facecolor(bg_color)
    
    # Customize both axes
    for ax in [ax1, ax2]:
        ax.tick_params(colors=line_color)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color(line_color)
        ax.grid(True, linestyle='--', alpha=0.3, color=line_color)
    
    plt.tight_layout()
    return fig
def create_player_heatmap(player_data):
    # Create pitch
    pitch = VerticalPitch(pitch_type='statsbomb', corner_arcs=True,
                         pitch_color=bg_color, line_color=line_color, line_zorder=2)
    
    fig, ax = plt.subplots(facecolor=bg_color)
    fig.suptitle('Player Position Heatmap', color=line_color,x=0.57, y=0.95)
    
    # Generate heatmap
    bin_statistic = pitch.bin_statistic(player_data.x, player_data.y, 
                                      statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    
    pitch.draw(ax=ax)
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')
    
    # Add colorbar
    ax_cbar = fig.colorbar(pcm, ax=ax)
    ax_cbar.outline.set_edgecolor(line_color)
    ax_cbar.ax.yaxis.set_tick_params(color=line_color)
    plt.setp(plt.getp(ax_cbar.ax.axes, 'yticklabels'), color=line_color)
    
    return fig
def create_player_comparison_chart(player1_data, player2_data, player1_name, player2_name):
    # Create figure
    fig = plt.figure(figsize=(12, 8), facecolor=bg_color)
    ax = fig.add_subplot(111, projection='polar')
    
    # Calculate metrics for both players
    def calculate_player_metrics(player_data, team_id):
        # Pass accuracy
        total_passes = len(player_data[player_data['typeId'] == 'Pass'])
        successful_passes = len(player_data[(player_data['typeId'] == 'Pass') & 
                                         (player_data['outcome'] == 'Successful')])
        pass_accuracy = (successful_passes / total_passes * 100) if total_passes > 0 else 0
        
        # Total xT
        total_xt = player_data['xT'].sum()
        
        # Key passes
        key_passes = len(player_data[(player_data['typeId'] == 'Pass') & 
                                   (player_data['outcome'] == 'Successful') &
                                   (player_data['keyPass'] == 1)])
        
        # Progressive passes
        progressive_passes = len(player_data[
            (player_data['team_name'] == team_id) & 
            (player_data['pro'] >= 9.144) & 
            (player_data['cross'] != 'Cross') & 
            (player_data['x'] <= 115) & 
            (player_data['x'] >= 40) & 
            (player_data['outcome'] == "Successful")
        ])
        
        # Defensive actions
        tackles = len(player_data[player_data['typeId'] == 'Tackle'])
        interceptions = len(player_data[player_data['typeId'] == 'Interception'])
        ball_recoveries = len(player_data[player_data['typeId'] == 'Ball recovery'])
        
        return [
            pass_accuracy,
            total_xt,
            key_passes,
            progressive_passes,
            tackles,
            interceptions,
            ball_recoveries
        ]
    
    # Get team_id from player data
    team_id = player1_data['team_name'].iloc[0]
    
    # Calculate metrics for both players
    p1_metrics = calculate_player_metrics(player1_data, team_id)
    p2_metrics = calculate_player_metrics(player2_data, team_id)
    
    # Metrics labels
    metrics = [
        'Pass\nAccuracy\n(%)',
        'Total xT',
        'Key Passes',
        'Progressive\nPasses',
        'Tackles',
        'Interceptions',
        'Ball\nRecoveries'
    ]
    
    # Number of metrics
    num_metrics = len(metrics)
    
    # Compute angles for the radar chart
    angles = np.linspace(0, 2*np.pi, num_metrics, endpoint=False)
    
    # Close the plot by appending first value
    angles = np.concatenate((angles, [angles[0]]))
    p1_metrics = np.concatenate((p1_metrics, [p1_metrics[0]]))
    p2_metrics = np.concatenate((p2_metrics, [p2_metrics[0]]))
    
    # Normalize metrics for better visualization
    max_values = np.maximum(p1_metrics, p2_metrics)
    p1_metrics_norm = p1_metrics / max_values
    p2_metrics_norm = p2_metrics / max_values
    
    # Plot radar chart
    ax.plot(angles, p1_metrics_norm, 'o-', linewidth=2, label=player1_name, color='#FFD700', alpha=0.7)
    ax.fill(angles, p1_metrics_norm, color='#FFD700', alpha=0.25)
    ax.plot(angles, p2_metrics_norm, 'o-', linewidth=2, label=player2_name, color='#C0C0C0', alpha=0.7)
    ax.fill(angles, p2_metrics_norm, color='#C0C0C0', alpha=0.25)
    
    # Add metric labels with rotation
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, color=line_color, size=8)
    
    # Rotate labels
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        if angle == 0:  # Pass Accuracy label
            label.set_rotation(90)
        else:
            label.set_rotation(angle * 180/np.pi)
    
    # Add title and customize appearance
    ax.set_title('Player Performance Comparison', color=line_color, pad=20, size=14)
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=line_color)
    ax.grid(True, linestyle='--', alpha=0.3, color=line_color)
    
    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1),
             facecolor=bg_color, edgecolor=line_color, labelcolor=line_color)
    
    # Set the same color for all spines
    for spine in ax.spines.values():
        spine.set_color(line_color)
    
    # Add values at each point
    for i in range(len(angles)-1):  # Skip the last duplicated point
        # Player 1 values
        ax.text(angles[i], p1_metrics_norm[i], f'{p1_metrics[i]:.1f}',
                ha='center', va='bottom', color='#FFD700', size=8,
                bbox=dict(facecolor=bg_color, edgecolor='none', alpha=0.7))
        
        # Player 2 values
        ax.text(angles[i], p2_metrics_norm[i], f'{p2_metrics[i]:.1f}',
                ha='left', va='center', color='#C0C0C0', size=8,
                bbox=dict(facecolor=bg_color, edgecolor='none', alpha=0.7))
    
    plt.tight_layout()
    return fig





# MATCH ANALYSIS 

def create_team_comparison_chart(df):
    # Get unique teams
    teams = df['team_name'].unique()
    
    # Event categories to compareS
    event_categories = {
        'Pass': ['Pass'],
        'Ball Recovery': ['Ball recovery'],
        "Attacking" : ['Take On', 'Goal', 'Miss', 'Attempt Saved',"Post"],
        'Defensive': ['Tackle', 'Interception', 'Clearance', 'Aerial'],
        'Set Pieces': ['Corner Awarded', 'Offside provoked']
    }
    
    # Calculate stats for each team
    team_stats = {}
    for team in teams:
        team_stats[team] = {}
        team_df = df[df['team_name'] == team]
        
        for category, events in event_categories.items():
            category_count = sum(len(team_df[team_df['typeId'] == event]) for event in events)
            team_stats[team][category] = category_count
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#1a1a1a')
    
    # Set up bar positions
    categories = list(event_categories.keys())
    x = np.arange(len(categories))
    width = 0.35
    
    # Plot bars for each team
    rects1 = ax.bar(x - width/2, [team_stats[teams[0]][cat] for cat in categories],
                    width, label=teams[0], color='#C0C0C0', alpha=0.7)
    rects2 = ax.bar(x + width/2, [team_stats[teams[1]][cat] for cat in categories],
                    width, label=teams[1], color='#FFD700', alpha=0.7)
    
    # Customize chart
    ax.set_ylabel('Number of Events', color='#ffffff')
    ax.set_title('Team Comparison by Event Category', color='#ffffff', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, color='#ffffff')
    ax.legend(facecolor='#1a1a1a', edgecolor='#ffffff', labelcolor='#ffffff')
    
    # Add value labels on bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(rect.get_x() + rect.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       color='#ffffff')
    
    autolabel(rects1)
    autolabel(rects2)
    
    ax.set_facecolor('#1a1a1a')
    plt.grid(True, linestyle='--', alpha=0.3, color='#ffffff')
    
    return fig

def create_momentum_chart(df):
    teams = df['team_name'].unique()
    home_team = teams[0]
    away_team = teams[1]
    
    # Calculate xT per minute for each team
    df['timeMin'] = df['timeMin'].astype(int)
    home_df = df[df['team_name'] == home_team]
    away_df = df[df['team_name'] == away_team]
    
    # Create momentum dataframe
    momentum_df = df.copy()
    # Multiply away team values by -1
    momentum_df.loc[momentum_df['team_name'] == away_team, 'xT'] *= -1
    
    # Calculate average xT per minute
    momentum_df = momentum_df.groupby('timeMin')['xT'].mean().reset_index()
    momentum_df['xT'].fillna(0, inplace=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='#1a1a1a')
    
    # Plot momentum
    colors = ['#FFD700' if x > 0 else '#C0C0C0' for x in momentum_df['xT']]
    
    # Get goal times
    home_goals = home_df[home_df['typeId'] == 'Goal']['timeMin'].tolist()
    away_goals = away_df[away_df['typeId'] == 'Goal']['timeMin'].tolist()
    
    # Calculate total xT for each team
    home_xt = home_df['xT'].sum().round(2)
    away_xt = away_df['xT'].sum().round(2)
    
    # Plot bars
    ax.bar(momentum_df['timeMin'], momentum_df['xT'], color=colors)
    
    # Add goal markers
    max_xt = momentum_df['xT'].max()
    min_xt = momentum_df['xT'].min()
    
    ax.scatter(home_goals, [max_xt] * len(home_goals), s=200, c='none',
              edgecolor='#00ff00', marker='o', label='Goal')
    ax.scatter(away_goals, [min_xt] * len(away_goals), s=200, c='none',
              edgecolor='#00ff00', marker='o')
    
    # Customize chart
    ax.set_xlabel('Match Minute', color=line_color)
    ax.set_ylabel('Team Momentum (xT)', color=line_color)
    ax.set_title('Match Momentum', color=line_color, pad=20)
    
    # Add half-time line
    ax.axvline(45, color=line_color, linestyle='--', alpha=0.5)
    
    # Add team labels
    ax.text(90, max_xt, f'{home_team}\nxT: {home_xt}', color='#FFD700',
            horizontalalignment='right', verticalalignment='top')
    ax.text(80, min_xt, f'{away_team}\nxT: {away_xt}', color='#C0C0C0',
            horizontalalignment='right', verticalalignment='bottom')
    ax.tick_params(axis='both', colors='#ffffff')

    ax.set_facecolor('#1a1a1a')
    ax.grid(True, linestyle='--', alpha=0.3, color='#ffffff')
    
    return fig




analyst_name = "Sara Bentelli"
st.markdown(f'<p class="analyst-name">Created by: {analyst_name}</p>', unsafe_allow_html=True)

# Main header with Al-Ittihad logo and title
st.markdown('<h1 class="main-header">Al-Ittihad Football Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar customization
st.sidebar.markdown('<div class="sidebar-title">Al-Ittihad Analysis Hub</div>', unsafe_allow_html=True)

# Initialize session state for analysis options
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = None
if "teams" not in st.session_state:
    st.session_state["teams"] = ["---"]

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Match Data", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Update teams in session_state
        df['y'] = 80- df['y']
        st.session_state["teams"] = list(df['team_name'].drop_duplicates())
        
        # Team selection
        st.sidebar.markdown('<p style="color: #FFD700; font-size: 1.2em; margin-top: 20px;">Select Team</p>', unsafe_allow_html=True)
        selected_team = st.sidebar.selectbox('', st.session_state["teams"])
        
        # Analysis options
        st.sidebar.markdown('<p style="color: #FFD700; font-size: 1.2em; margin-top: 20px;">Analysis Type</p>', unsafe_allow_html=True)
        analysis_type = st.sidebar.selectbox('', ["Team Performance", "Player Performance", "Match Analysis"])
        
        # Main content area
        if selected_team != "---":
            st.markdown('<div class="custom-container">', unsafe_allow_html=True)
            
            if analysis_type == "Team Performance":
                st.header("Team Performance Analysis")
                st.markdown('<div class="analysis-buttons">', unsafe_allow_html=True)
                
                col1, col2, col3, col4,col5 = st.columns(5)
                
                with col1:
                    if st.button("Passing Networks"):
                        st.session_state.current_view = "passing_networks"
                with col2:
                    if st.button('F.Third Pass'):
                        st.session_state.current_view = 'final_third'
                with col3:
                    if st.button("Attack"):
                        st.session_state.current_view = "shot_map"
                        
                with col4:
                    if st.button("Recoveries"):
                        st.session_state.current_view = "high_recov"

                with col5:
                    if st.button("Defensive Actions"):
                        st.session_state.current_view = "defensive_actions"
                
               
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display the selected view
                if st.session_state.current_view == "passing_networks":
                    fig = create_15min_passing_networks(df, selected_team)
                    st.pyplot(fig)
                elif st.session_state.current_view == "final_third":
                    fig = final_third_pass_map(df,selected_team)
                    st.pyplot(fig)

                elif st.session_state.current_view == "shot_map":
                    fig = attack_map(df, selected_team)
                    st.pyplot(fig)
                elif st.session_state.current_view == "high_recov":
                    fig =  create_high_recoveries_map(df,selected_team)
                    st.pyplot(fig)
                elif st.session_state.current_view == "defensive_actions":
                    fig = create_defensive_actions_map(df, selected_team)
                    st.pyplot(fig)
                elif st.session_state.current_view == "set_piece":
                    fig = create_set_pieces_and_cards_chart(df)
                    st.pyplot(fig)
            
            elif analysis_type == "Player Performance":
                st.header("Player Performance Analysis")
                team_players = df[df['team_name'] == selected_team]['shortName'].unique()
                # Add styled header for player selection
                st.markdown('<p style="color: #FFD700; font-size: 1.2em; margin-top: 20px;">Select Player</p>', unsafe_allow_html=True)
                 # Player selection dropdown
                selected_player = st.selectbox(
                   '',  # Empty label since we're using the styled header above
                     team_players,
                     key='player_selector')
                st.markdown('<div class="analysis-buttons">', unsafe_allow_html=True)
                col1, col2, col3,col4 = st.columns(4)
                with col1:
                    if st.button("Player Stats"):
                        st.session_state.current_view = "player_stats"
                        st.session_state.compare_with = None
                with col2:
                    if st.button("Heat Maps"):
                        st.session_state.current_view = "heat_maps"
                        st.session_state.compare_with = None
                with col3:
                    if st.button('Player Comparison'):
                        st.session_state.current_view = "player_comparison"
                with col4: 
                    if st.button('Player Detailed'):
                        st.session_state.current_view = "player_detailed"

                st.markdown('</div>', unsafe_allow_html=True)
                # Display the selected view with player-specific data
                if st.session_state.current_view == "player_stats":
                    fig = create_player_stats_chart(df[df['shortName'] == selected_player])
                    st.pyplot(fig)
                elif st.session_state.current_view == "heat_maps":
                    fig = create_player_heatmap(df[df['shortName'] == selected_player])
                    st.pyplot(fig)
                elif st.session_state.current_view == "player_detailed" :
                    fig = create_player_pass_map(df, selected_player, is_away=False)
                    st.pyplot(fig)
                    fig = create_defensive_actions_player_map(df[df['shortName'] == selected_player])
                    st.pyplot(fig)
                elif st.session_state.current_view == "player_comparison":
                     # Add another player selection for comparison
                     other_players = [p for p in team_players if p != selected_player]
                     st.markdown('<p style="color: #FFD700; font-size: 1.2em; margin-top: 20px;">Compare with</p>', unsafe_allow_html=True)
                     st.session_state.compare_with = st.selectbox( '',other_players, key='comparison_player' )
                     if st.session_state.compare_with :
                         player1_data = df[df['shortName'] == selected_player]
                         player2_data = df[df['shortName'] == st.session_state.compare_with]
                         fig = create_player_comparison_chart(player1_data, player2_data, selected_player, st.session_state.compare_with)
                         st.pyplot(fig)
               


        


                
    

    
                  
    

            elif analysis_type == "Match Analysis":
                st.header("Match Analysis")
                st.markdown('<div class="analysis-buttons">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                     if st.button("Team Comparison"):
                         st.session_state.current_view = "team_comparison"
                with col2:
                     if st.button("Match Momentum"):
                        st.session_state.current_view = "match_momentum"
                with col3:
                    if st.button('Detailed Analysis'):
                        st.session_state.current_view = "detailed_analysis"

    
                st.markdown('</div>', unsafe_allow_html=True)

                if st.session_state.current_view == "team_comparison":
                     fig = create_team_comparison_chart(df)
                     st.pyplot(fig)
                elif st.session_state.current_view == "match_momentum":
                     fig = create_momentum_chart(df)
                     st.pyplot(fig)
                elif st.session_state.current_view == "detailed_analysis":
                     fig = create_detailed_match_analysis(df)
                     st.pyplot(fig)
                     
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    # Show welcome message only when no file is uploaded
    st.markdown("""
    <div class="welcome-container">
        <h2 style="color: #FFD700; margin-bottom: 20px;">Welcome to the Al-Ittihad Football Analysis Dashboard</h2>
        <p style="font-size: 1.2em; margin-bottom: 20px;">Upload your match data file (CSV or Excel) from the sidebar to begin the analysis.</p>
        <p>Required columns in your data:</p>
        <ul>
            <li>team_name: Team identifier</li>
            <li>shortName: Player name</li>
            <li>typeId: Event type (e.g., 'Pass', 'Tackle', 'Clearance', 'Save', 'Challenge')</li>
            <li>x, y: Starting coordinates</li>
            <li>end_x, end_y: Ending coordinates</li>
            <li>timeMin: Match minute</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #FFD700; padding: 20px;'>
    Al-Ittihad Club Football Analysis Platform
</div>
""", unsafe_allow_html=True)
# Add footer text
footer_text = """
    <style>
        .footer {
            position: fixed;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            font-family: 'Georgia', serif;
            font-style: italic;

            font-size: 14px;
            color: #888;
            text-align: center
        }
    </style>
    <div class="footer">"Bringing clarity to the game you love." — <b>Sara Bentelli</b></div>
"""
st.markdown(footer_text, unsafe_allow_html=True)

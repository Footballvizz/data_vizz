import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import Sbopen, Pitch, VerticalPitch,FontManager
from statsbombpy import sb
import cmasher as cmr
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap,to_rgba
from scipy.ndimage import gaussian_filter
from mplsoccer import Pitch, VerticalPitch, FontManager,Sbopen

def passe(df,selected_team):
   team1=selected_team
   robotto_regular = FontManager()
   path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
   mask=(((df.tag_name=='successful pass')|(df.tag_name=='unseccesful pass'))&(df.team==selected_team))
   df_pass=df.loc[mask]
   df_ball_receipt=df.loc[mask,['end_x','end_y']]
   
   DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
   NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
   LINEWIDTH = 0.5
   ALPHA_PITCH_LINE = 0.2
   ALPHA_PASS_LINE = 0.6
   cmap='Oranges'
   back='black'
   LINE_COLOR="w"
   PASS_COLOR='w'
   flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['black','#e88013' ,'white'], N=400)
   pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,line_zorder=4, linestyle='-')
   fig, axs= pitch.grid(ncols=2,grid_height=0.7, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
   fig.set_facecolor(back)

   kde_Pass = pitch.kdeplot(df_pass.x,df_pass.y, ax=axs['pitch'][0],
                          levels=200, shade_lowest=True,
                          cut=50, cmap=flamingo_cmap,fill=True)
   
   
   kde_receipt=pitch.kdeplot(df_ball_receipt.end_x,df_ball_receipt.end_y, ax=axs['pitch'][1],levels=200,shade_lowest=True,cut=100,cmap=flamingo_cmap,fill=True)
   
   
   # endnote and title
   axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['endnote'].text(0.2, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['title'].text(0.5, 1.5,f'{team1}  Passes ', color='#F5F5DC',fontsize=25,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)
   
   axs['pitch'][0].set_title('Ball Pass',color='#F5F5DC',
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)
   axs['pitch'][1].set_title('Ball Receipt',color='#F5F5DC',
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)
   return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)



def shot(df):
  robotto_regular = FontManager()
  path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
  shot_blocked=df[df['tag_name']=='shot blocked']
  shot_target=df[df['tag_name']=='shot on taget']
  shot_off_target=df[df['tag_name']=='shot off target']
  df_goal=df[df['tag_name']=='goal']
  DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
  NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
  LINEWIDTH = 0.5
  ALPHA_PITCH_LINE = 0.2
  ALPHA_PASS_LINE = 0.6
  cmap=cmr.jungle
  back='black'
  LINE_COLOR="w"
  PASS_COLOR='#F5F5DC'
  pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,line_zorder=4, linestyle='-',half=True)
  fig, axs= pitch.grid(figheight=10, title_height=0.08, endnote_space=0,
                     
                      axis=False,
                      title_space=0, grid_height=0.82, endnote_height=0.05,grid_width=0.88)
  fig.set_facecolor(back)
  pitch.scatter(df_goal.x,df_goal.y,marker="football", c='white',ax=axs['pitch'],s=450,edgecolors='#b94b75',label='Goal')
  pitch.scatter(shot_blocked.x,shot_blocked.y,c='red',ax=axs['pitch'],s=450,marker="X",alpha=.8,label='Blocked')
  pitch.scatter(shot_target.x,shot_target.y,c='w',ax=axs['pitch'],s=450,marker="o",alpha=.8,label='On Target')
  pitch.scatter(shot_off_target.x,shot_off_target.y,c='orange',ax=axs['pitch'],s=450,marker="D",alpha=.8,label='Off Target')
  for _, row in df_goal.iterrows():
            axs['pitch'].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=3,edgecolor="green", facecolor="red"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 color="Red")
  for _, row in shot_target.iterrows():
            axs['pitch'].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=3,edgecolor="white", facecolor="red"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 color="Red")
  for _, row in shot_blocked.iterrows():
            axs['pitch'].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=3,edgecolor="red", facecolor="red"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 color="Red")
            
  for _, row in shot_off_target.iterrows():
            axs['pitch'].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=3,edgecolor="yellow", facecolor="red"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 color="Red")
  for i in range(1, NUM_GLOW_LINES + 1):
      pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,half=True,
                  linewidth=LINEWIDTH + (DIFF_LINEWIDTH * i),
                  line_alpha=ALPHA_PITCH_LINE / NUM_GLOW_LINES,
                  goal_alpha=ALPHA_PITCH_LINE / NUM_GLOW_LINES,
                  goal_type='box')
      
      pitch.draw(ax=axs['pitch'])
  axs['title'].text(0.5, 0.6,'Shots', color='#F5F5DC',fontsize=35,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)
  axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
  axs['endnote'].text(0.2, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
  axs['pitch'].legend(facecolor='w', handlelength=2, edgecolor='None', fontsize=20, loc='upper left')

  return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)

def pass_cross(df):
   robotto_regular = FontManager()
   path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),path_effects.Normal()]
   mask=(df.tag_name=='cross')
   df=df[mask]
   ### LINEWIDTH = 1  # starting linewidth
   DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
   NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
   LINEWIDTH = 0.3
# in each loop, for the glow, we plot the alpha divided by the num_glow_lines
# I have a lower alpha_pass_line value as there is a slight overlap in
# the pass comet lines when using capstyle='round'
   ALPHA_PITCH_LINE = 0.2
   ALPHA_PASS_LINE = 1

   flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['#064534','#e88013' ,'white'], N=100)
   PASS_COLOR = 'w'#"pink" #'#89103F'   
   LINE_COLOR =  'w'#"#0FF4FF" #'#BF7117'  #'#FE53BB' 
   DIVISION_LINES='#800080'
   back='black'#'#73737
   pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,line_zorder=2, linestyle='-',half=True)
   fig, axs= pitch.grid(figheight=10, title_height=0.08, endnote_space=0,
                      # Turn off the endnote/title axis. I usually do this after
                      # I am happy with the chart layout and text placement
                      axis=False,
                      title_space=0, grid_height=0.82, endnote_height=0.05,grid_width=0.88)
   fig.set_facecolor(back)
    
   pitch.lines(df.x,df.y,df.end_x,df.end_y,ax=axs['pitch'],capstyle='butt',  # cut-off the line at the end-location.
            linewidth=LINEWIDTH, color=PASS_COLOR,label='Crosses')
   pitch.scatter(df.x,df.y, color="w",s=100,edgecolor="w",marker="o",alpha=.5,ax=axs['pitch'])
   for i in range(1, NUM_GLOW_LINES + 1):
       pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,half=True,
                  linewidth=LINEWIDTH + (DIFF_LINEWIDTH * i),
                  line_alpha=ALPHA_PITCH_LINE / NUM_GLOW_LINES,
                  goal_alpha=ALPHA_PITCH_LINE / NUM_GLOW_LINES,
                  goal_type='box')
    
   pitch.draw(ax=axs['pitch'])  # we plot on-top of our previous axis from pitch.grid
   pitch.lines(df.x, df.y,
                df.end_x,df.end_y,
                linewidth=LINEWIDTH + (DIFF_LINEWIDTH * i),
                capstyle='round',  # capstyle round so the glow extends past the line
                alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES,
                color=PASS_COLOR, comet=True, ax=axs['pitch'])
   axs['title'].text(0.5, 0.6,'Crosses', color='#F5F5DC',fontsize=35,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)
   axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=13,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['endnote'].text(0.2, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)
def succ_pass(df):
   
   robotto_regular = FontManager()
   path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),path_effects.Normal()]
   mask_succ=(df.tag_name=='successful pass')
   mask_unsuc=(df.tag_name=="unseccesful pass")
   df_succ=df[mask_succ]
   df_unsucc=df[mask_unsuc]
   ### LINEWIDTH = 1  # starting linewidth
   DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
   NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
   LINEWIDTH = 0.3
# in each loop, for the glow, we plot the alpha divided by the num_glow_lines
# I have a lower alpha_pass_line value as there is a slight overlap in
# the pass comet lines when using capstyle='round'
   ALPHA_PITCH_LINE = 0.2
   ALPHA_PASS_LINE = 1

   flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['#064534','#e88013' ,'white'], N=100)
   PASS_COLOR = 'w'#"pink" #'#89103F'   
   LINE_COLOR =  'w'#"#0FF4FF" #'#BF7117'  #'#FE53BB' 
   DIVISION_LINES='#800080'
   back='black'#'#73737
   pitch = VerticalPitch(line_color=LINE_COLOR, pitch_color=back,line_zorder=2, linestyle='-')
   fig, axs= pitch.grid(ncols= 2,figheight=10, title_height=0.08, endnote_space=0,
                      # Turn off the endnote/title axis. I usually do this after
                      # I am happy with the chart layout and text placement
                      axis=False,
                      title_space=0, grid_height=0.82, endnote_height=0.05,grid_width=0.88)
   fig.set_facecolor(back)
   for _, row in df_succ.iterrows():
            axs['pitch'][0].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=2, edgecolor="#3EFF16", facecolor="#3EFF16"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 )
   for _, row in df_unsucc.iterrows():
            axs['pitch'][1].annotate('', xy=(row["end_y"], row["end_x"]), xytext=(row["y"], row["x"]),
                                 arrowprops=dict(arrowstyle='->', lw=3,edgecolor="red", facecolor="red"),
                                                 alpha=ALPHA_PASS_LINE / NUM_GLOW_LINES, 
                                                 color="Red")
 
   axs['pitch'][0].annotate('', xy=(84,85), xytext=(84, 35),
                                 arrowprops=dict(arrowstyle='->', lw=2, edgecolor="white", facecolor="white")
                                               
                                                 )
   #pitch.lines(df_unsucc.x,df_unsucc.y,df_unsucc.end_x,df_unsucc.end_y,ax=axs['pitch'][1],capstyle='butt',  # cut-off the line at the end-location.
            #linewidth=LINEWIDTH, color="red",label='Unsucc')
   axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['endnote'].text(0.15, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['title'].text(0.5, 0.6,'Passes', color='#F5F5DC',fontsize=25,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)
   axs['pitch'][0].set_title("Succesful",color='white',
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)
   axs['pitch'][1].set_title('Unsuccesful',color='white',
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=20)

   return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)
def ball_loss(df):
    # fontmanager for google font (robotto)
   robotto_regular = FontManager()
   path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
   

   pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                      ['#15242e', '#4393c4'], N=10)
   df=df[df['tag_name']== 'ball loss']
   text_color='#F5F5DC'
   ### LINEWIDTH = 1  # starting linewidth
   DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
   NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
   LINEWIDTH = 0.3
# in each loop, for the glow, we plot the alpha divided by the num_glow_lines
# I have a lower alpha_pass_line value as there is a slight overlap in
# the pass comet lines when using capstyle='round'
   ALPHA_PITCH_LINE = 0.2
   ALPHA_PASS_LINE = 1

   flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['#064534','#e88013' ,'white'], N=100)
   PASS_COLOR = 'w'#"pink" #'#89103F'   
   LINE_COLOR =  'w'#"#0FF4FF" #'#BF7117'  #'#FE53BB' 
   DIVISION_LINES='#800080'
   back='black'#'#73737
   pitch = Pitch(line_color=LINE_COLOR, pitch_color=back,line_zorder=2, linestyle='-',half=False)
   fig, axs= pitch.grid(grid_height=0.6, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
   fig.set_facecolor(back)
    
   pitch.scatter(df.x,df.y, color="red",s=500,edgecolor="w",marker="X",alpha=.5,ax=axs['pitch'])
   axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['endnote'].text(0.26, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
   axs['title'].text(0.5, 0.6,'Ball Loss', color='#F5F5DC',fontsize=25,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)

   return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)
def final_third_entries(df):
      df=df[df["x"]>= 80]
      robotto_regular = FontManager()
      path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
      DIFF_LINEWIDTH = 2.2  # amount the glow linewidth increases each loop
      NUM_GLOW_LINES = 3  # the amount of loops, if you increase the glow will be wider
      LINEWIDTH = 0.3
      ALPHA_PITCH_LINE = 0.2
      ALPHA_PASS_LINE = 1
      text_color='#F5F5DC'
      flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['black','#394a13' ,'#a4e610','white'], N=100)
    
      back='black'#'#73737
      pitch = VerticalPitch(line_color="w", pitch_color=back,line_zorder=2, linestyle='-',half=True)
      fig, axs= pitch.grid(grid_height=0.6, title_height=0.05,  axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0,grid_width=0.88,figheight= 10)
      fig.set_facecolor(back)
      bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins=(25, 25))
      bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
      pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'], cmap='hot', edgecolors='#22312b',label=f' entries')
      axs['endnote'].text(1, 0.3, 'Created by Sara Bentelli', va='center', ha='right', fontsize=10,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
      axs['endnote'].text(0.26, 0.3, 'Analyst Bashar Ziab', va='center', ha='right', fontsize=15,
                    fontproperties=robotto_regular.prop, color='#F5F5DC')
      axs['title'].text(0.5, 0.6,'Final Third Heatmap Actions', color='#F5F5DC',fontsize=25,va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop)
      #pitch.scatter(df.x,df.y, ax=axs['pitch'][1],s=450,c='w',edgecolor='green',salpha=.7)
      return st.pyplot(fig, dpi=100, facecolor= back ,bbox_inches=None)

def passing_network(df):
      import numpy as np
      import matplotlib.pyplot as plt
      from mplsoccer import Pitch
      from matplotlib.colors import to_rgba
      import pandas as pd

      passes=df[(df['tag_name']=='successful pass')]
      # Créer un dictionnaire {player_name: position}
      player_position_dict = passes.set_index("players")["players position"].to_dict()

      # Remplacer les noms des receivers par leur position
      passes["receiver"] = passes["receiver"].map(player_position_dict)
      average_locs_and_count = passes.groupby('players position').agg({'x': 'mean', 'y': 'mean', 'players position': 'count'}).rename(columns={'players position': 'count'})
      passes_between = passes.groupby(['players position', 'receiver']).size().reset_index(name='pass_count')
      passes_between = passes_between.merge(average_locs_and_count, left_on='players position', right_index=True)
      passes_between = passes_between.merge(average_locs_and_count, left_on='receiver', right_index=True, suffixes=['', '_end'])
      MAX_LINE_WIDTH = 18
      MAX_MARKER_SIZE = 3000
      MIN_TRANSPARENCY = 0.3
      # Normaliser l'épaisseur des lignes
      passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() * MAX_LINE_WIDTH)
      # Normaliser la taille des points (joueurs)
      average_locs_and_count['marker_size'] = (average_locs_and_count['count']
                                         / average_locs_and_count['count'].max() * MAX_MARKER_SIZE)
      # Transparence des passes
      color = np.array(to_rgba('white'))
      color = np.tile(color, (len(passes_between), 1))
      c_transparency = passes_between.pass_count / passes_between.pass_count.max()
      c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
      color[:, 3] = c_transparency  # Appliquer transparence
      # Création du terrain
      pitch = Pitch(pitch_type='statsbomb', pitch_color='black', line_color='white')
      fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
      fig.set_facecolor("black")
      # Tracer les passes
      pitch.lines(passes_between.x, passes_between.y,
            passes_between.x_end, passes_between.y_end, lw=passes_between.width,
            color=color, zorder=1, ax=ax)

      # Tracer les joueurs
      pitch.scatter(average_locs_and_count.x, average_locs_and_count.y,
              s=average_locs_and_count.marker_size, color='red', edgecolors='black', linewidth=1, ax=ax)

      # Ajouter les noms des joueurs
      for index, row in average_locs_and_count.iterrows():
            pitch.annotate(row.name, xy=(row.x, row.y), c='white', va='center',
                   ha='center', size=16, weight='bold', ax=ax)
  
                             
      return st.pyplot(fig, dpi=100, facecolor= "black" ,bbox_inches=None)






















      





    
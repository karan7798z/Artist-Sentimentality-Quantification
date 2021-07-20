from bokeh.plotting import figure, show
from bokeh.models.tools import HoverTool
from bokeh.io import curdoc
from bokeh.models import Select, CustomJS, ColumnDataSource, FactorRange, SingleIntervalTicker, LinearAxis
from bokeh.layouts import column, row
from bokeh.themes import theme
import numpy as np
import pandas as pd
from math import pi

df = pd.read_excel("track_data.xlsx")
df.drop(df[df.name == 'Theme from "The Search for Everything"'].index, inplace=True)

df['si'] = ((1 - df['valence']) + ((df['neg_per'] / 100) * (df['word_count'] * 1000 / df['length']))) / 2
df['max_sadness_index'] = df.groupby('artist')['si'].transform('max')
df['max_acousticness'] = df.groupby('artist')['acousticness'].transform('max')
df['max_danceability'] = df.groupby('artist')['danceability'].transform('max')

df['sadness_index'] = df['si'] / df['max_sadness_index']
df['acousticity'] = df['acousticness']/df['max_acousticness']
df['dance_index'] = df['danceability']/df['max_danceability']

filtered_df = df[['artist', 'name', 'album', 'sadness_index', 'acousticity', 'dance_index', 'album_img_small', 'album_img_med', 'release_date']]
filtered_df['album_avg_si'] = filtered_df.groupby(['artist', 'album'])['sadness_index'].transform(np.mean)
filtered_df['album_avg_ac'] = filtered_df.groupby(['artist',  'album'])['acousticity'].transform(np.mean)
filtered_df['album_avg_dc'] = filtered_df.groupby(['artist',  'album'])['dance_index'].transform(np.mean)


avg_si_df = filtered_df[['artist', 'album', 'album_avg_si', 'album_avg_ac', 'album_avg_dc', 'album_img_small', 'album_img_med', 'release_date']].drop_duplicates()

source = ColumnDataSource(filtered_df)
curr = ColumnDataSource(filtered_df[filtered_df.artist == 'Radiohead'].sort_values(by='release_date'))
avg_curr = ColumnDataSource(avg_si_df[avg_si_df.artist == 'Radiohead'].sort_values(by='release_date'))

def create_figure():
    x_range = df[df.artist == select_artist.value].sort_values(by='release_date').album.unique()
    curr = ColumnDataSource(filtered_df[filtered_df.artist == select_artist.value].sort_values(by='release_date'))
    avg_curr = ColumnDataSource(avg_si_df[avg_si_df.artist == select_artist.value].sort_values(by='release_date'))

    curdoc().theme = "contrast"

    y_name_track_wise = axis_map[y_axis.value]['track_wise']
    y_name_album_avg = axis_map[y_axis.value]['album_avg']

    p = figure(sizing_mode='scale_both', x_range=x_range,
               x_axis_label="Albums", y_axis_label=y_axis.value)

    p.title.text = '{} Track Sentimentality Distribution'.format(select_artist.value)
    p.title.text_font_size = "25px"
    p.title.text_font = "DejaVu Sans"
    p.title.align = 'center'
    c1 = p.circle('album', y_name_track_wise, source=curr, size=18, fill_alpha=0.5, line_color='white', hover_fill_color='white')
    c2 = p.circle(x='album', y=y_name_album_avg, source=avg_curr, color='white', size=10)
    p.line(x='album', y=y_name_album_avg, source=avg_curr, color='white', line_width=0.5)
    p.toolbar.autohide = True
    p.yaxis[0].ticker.desired_num_ticks = 10
    p.xaxis.major_label_orientation = pi/4
    p.xaxis.major_label_text_font_size = '8pt'

    hover1 = HoverTool(tooltips="""
      <div class="block" style="overflow: hidden; display: flex;">
          <div>
              <img
               src="@album_img_small" alt="@album_img_small"
               margin: 0px 15px 15px 0px;"
               border="2">
              </img>
          </div>
          <div style="margin-left: 0.5rem;">
              <div>
                  <span style="font-size: 15px; font-weight: bold;">
                  @name</span> 
              </div>
              <div>
                  <span style="font-size: 10px; color: "black";">Album: <strong>@album</strong></span><br>
                  <span style="font-size: 10px; color: "black";">"""+y_axis.value+""": <strong>@"""+y_name_track_wise+"""</strong></span><br>
                  <span style="font-size: 10px; color: "black";">Album avg.""" + y_axis.value+""": <strong>@"""+y_name_album_avg+"""</strong></span>
              </div>
          </div>
      </div>
      <hr></hr>
      """, renderers=[c1])

    hover2 = HoverTool(tooltips="""
      <div>
          <div>
              <img
               src="@album_img_med" alt="@album_img_med"
               margin: 0px 15px 15px 0px;"
               border="2">
              </img>
          </div>
          <div>
              <div>
                  <span style="font-size: 10px; color: 'black';">Album: <strong>@album</strong></span><br>
                  <span style="font-size: 10px; color: "black";">Album avg.""" + y_axis.value+""": <strong>@"""+y_name_album_avg+"""</strong></span>
              </div>
          </div>
      </div>
      """, renderers=[c2])

    p.add_tools(hover1, hover2)

    return p


def update(attr, new, old):
    layout.children[1] = create_figure()


select_artist = Select(title='Select your favorite artist:', options=list(filtered_df.artist.unique()), value='Radiohead', width=320)

axis_map = {
    "Gloom Index": {'track_wise': 'sadness_index', 'album_avg': 'album_avg_si'},
    "Acousticity": {'track_wise': 'acousticity', 'album_avg': 'album_avg_ac'},
    "Dance Index": {'track_wise': 'dance_index', 'album_avg': 'album_avg_dc'}
}
y_axis = Select(title='Y Axis', options=sorted(axis_map.keys()), value="Gloom Index")

controls = [select_artist, y_axis]
for control in controls:
    control.on_change('value', update)

inputs = column(*controls)
layout = row(inputs, create_figure())
layout.sizing_mode = 'scale_both'
curdoc().add_root(layout)

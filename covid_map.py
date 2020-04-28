import pandas as pd
import geopandas as gpd
import numpy as np
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, DateSlider, HoverTool, BoxZoomTool, ResetTool
from bokeh.layouts import widgetbox, row, column
from datetime import date

import pandas as pd
import geopandas as gpd
import numpy as np
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, DateSlider, HoverTool, BoxZoomTool, ResetTool
from bokeh.layouts import widgetbox, row, column
from datetime import date
from read_data import read_all_data


def json_data(selectedDate):
    df_date = merged[merged["Date"]==str(selectedDate)]
    json_data = json.dumps(json.loads(df_date.to_json()))
    return df_date.to_json()

def update_date(attr, old, new):
    yr = date_slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'covid 19 deaths, %s' %yr

def update_color(attr, old, new):
    color_mapper.high = color_slider.value

if __name__=="__main__":
    merged = read_all_data()
    geosource = GeoJSONDataSource(geojson = json_data(str(date(2020, 4,25))))
    palette = brewer['YlGnBu'][8]
    palette = palette[::-1]
    color_cap_deaths = round(np.nanmax(merged["Deaths"]) + 500, -3)
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = color_cap_deaths, nan_color = '#d9d9d9')
    hover = HoverTool(tooltips = [ ('Country/region','@country'),('deaths', '@Deaths')])
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 900, height = 20, border_line_color=None,location = (0,0), orientation = 'horizontal')
    p = figure(title = 'Covid 19 deaths', plot_height = 900 , plot_width = 1600, tools = [BoxZoomTool(), ResetTool(), hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.patches('xs','ys', source = geosource,fill_color = {'field' :'Deaths', 'transform' : color_mapper}, line_color = 'black', line_width = 0.25, fill_alpha = 1)
    p.add_layout(color_bar, 'below')

    date_slider = DateSlider(title="Date Range: ", start=date(2020, 1, 31), end=date(2020, 4, 25), value=date(2020, 4, 25), step=1)
    date_slider.on_change('value', update_date)
    color_slider = Slider(title="Max value", start=0, end=color_cap_deaths, value=color_cap_deaths, step=100)
    color_slider.on_change('value', update_color)
    layout = column(p,widgetbox(date_slider), widgetbox(color_slider))
    curdoc().add_root(layout)
    show(layout)

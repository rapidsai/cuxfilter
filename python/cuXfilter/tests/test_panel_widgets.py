from cuXfilter import charts
import cuXfilter
from bokeh import palettes
from cuXfilter.layouts import layout_1

layout_1.num_chart_per_row = 1

cux_df = cuXfilter.DataFrame.from_arrow('/home/ajay/data/146M_predictions_v2.arrow')

chart0 = charts.bokeh.choropleth(x='zip', y='delinquency_12_prediction', aggregate_fn='mean', 
                                  geo_color_palette=palettes.Inferno256,
                                  geoJSONSource = 'https://raw.githubusercontent.com/rapidsai/cuxfilter/master/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json',
                                  data_points=1000, width=1100, x_range=(-126, -66), y_range=(23, 50))

chart1 = charts.panel_widgets.range_slider('dti', width=400, height=400)
chart2 = charts.panel_widgets.range_slider('delinquency_12_prediction',data_points=50, width=400, height=400)
chart3 = charts.panel_widgets.range_slider('borrower_credit_score',data_points=50, width=400, height=400)

d = cux_df.dashboard([chart0, chart1], layout=layout_1)

d.add_charts([chart2, chart3])

d.show()
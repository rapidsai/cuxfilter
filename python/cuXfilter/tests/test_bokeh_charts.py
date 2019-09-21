from cuXfilter import charts
import cuXfilter
from bokeh import palettes
from cuXfilter.layouts import layout_1, layout_2, layout_5

cux_df = cuXfilter.DataFrame.from_arrow('/home/ajay/data/146M_predictions_v2.arrow')

# cux_df.data = cux_df.data.query('zip > 400')

chart0 = charts.bokeh.choropleth(x='zip', y='delinquency_12_prediction', aggregate_fn='mean', 
                                  geo_color_palette=palettes.Inferno256,
                                  geoJSONSource = 'https://raw.githubusercontent.com/rapidsai/cuxfilter/master/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json',
                                  data_points=1000, x_range=(-126, -66), y_range=(23, 50),
                                  nan_color='white')
chart1 = charts.bokeh.bar('dti')
chart2 = charts.bokeh.bar('delinquency_12_prediction')
# chart3 = charts.bokeh.line('borrower_credit_score',step_size=1, width=400, height=400)

d = cux_df.dashboard([chart0,chart1, chart2], layout=layout_5, title="Custom Dashboard")

# d.add_charts([chart2, chart3])

d.show()
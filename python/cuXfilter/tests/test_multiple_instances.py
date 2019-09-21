from cuXfilter import charts
import cuXfilter
from bokeh import palettes
from cuXfilter.layouts import layout_1


cux_df = cuXfilter.DataFrame.from_arrow('/home/ajay/data/146M_predictions_v2.arrow')

chart0 = charts.bokeh.choropleth(x='zip', y='delinquency_12_prediction', aggregate_fn='mean', 
                                  geo_color_palette=palettes.Inferno256,
                                  geoJSONSource = 'https://raw.githubusercontent.com/rapidsai/cuxfilter/master/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json',
                                  data_points=1000, width=1100, x_range=(-126, -66), y_range=(23, 50))
chart1 = charts.bokeh.bar('dti', width=400, height=400)
chart2 = charts.bokeh.bar('delinquency_12_prediction',data_points=50, width=400, height=400)
chart3 = charts.bokeh.bar('borrower_credit_score',data_points=50, width=400, height=400)

d = cux_df.dashboard([chart0, chart1], layout=layout_1)

assert list(d.charts.values()) == [chart0, chart1]

d1 = cux_df.dashboard([chart2, chart3], layout=layout_1)

assert list(d1.charts.values())  == [chart2, chart3]
from cuXfilter import charts
import cuXfilter
from bokeh import palettes
from cuXfilter.layouts import layout_1


cux_df = cuXfilter.DataFrame.from_arrow('/home/ajay/data/146M_predictions_v2.arrow')

mapper1 = {}
mapper2 = {}

for val in cux_df.data.dti.unique().to_pandas().tolist():
    mapper1[int(val)] = 'l_'+str(val)

for val in cux_df.data.borrower_credit_score.unique().to_pandas().tolist():
    if int(val) <500:
        mapper2[int(val)] = 'less'
    elif int(val)>=500 and int(val)<600:
        mapper2[int(val)] = 'medium'
    elif int(val)>=600 and int(val)<750:
        mapper2[int(val)] = 'good'
    else:
        mapper2[int(val)] = 'great'

chart0 = charts.bokeh.choropleth(x='zip', y='delinquency_12_prediction', aggregate_fn='mean', 
                                  geo_color_palette=palettes.Inferno256,
                                  geoJSONSource = 'https://raw.githubusercontent.com/rapidsai/cuxfilter/master/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json',
                                  data_points=1000, width=1100, x_range=(-126, -66), y_range=(23, 50))

# chart1 = charts.bokeh.bar('dti',dasta_points=50, width=400, height=400, x_label_map=mapper1)

# chart1 = charts.bokeh.bar('delinquency_12_prediction',y='borrower_credit_score',aggregate_fn='mean', data_points=50, width=400, height=400, y_label_map=mapper2)
chart2 = charts.panel_widgets.multi_select('dti',data_points=50, width=400, height=400, label_map=mapper1)

chart3 = charts.bokeh.bar('borrower_credit_score',data_points=50, width=400, height=400)
d = cux_df.dashboard([chart0, chart2, chart3], layout=layout_1)

# d.add_charts([chart0])

d.show()
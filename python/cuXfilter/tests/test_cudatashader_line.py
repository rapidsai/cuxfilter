# import cudatashader as ds
# import cudatashader.transfer_functions as tf
# from collections import OrderedDict
# import cudf
# from cuXfilter import charts, DataFrame
# import random

# cux_df = DataFrame.from_dataframe(cudf.DataFrame({'states': [float(i) for i in range(57_000)], 'val':[float(i*10) for i in range(57_000)]}))
# line_chart_1 = charts.cudatashader.line(x='states',
#                                          y='val')

# d = cux_df.dashboard([line_chart_1])

# d.show()


from cuXfilter import charts
import cuXfilter
from bokeh import palettes
from cuXfilter.layouts import layout_2
import numpy as np

cux_df = cuXfilter.DataFrame.from_arrow('/home/ajay/data/146M_predictions_v2.arrow')

cux_df.data['borrower_credit_score'] = cux_df.data['borrower_credit_score'].astype(np.float64)
cux_df.data['delinquency_12_prediction'] = cux_df.data['delinquency_12_prediction'].astype(np.float64)

cux_df.data = cux_df.data.sort_values('borrower_credit_score')
# cux_df.data = cux_df.data.query('zip > 400')

chart0 = charts.bokeh.choropleth(x='zip', y='delinquency_12_prediction', aggregate_fn='mean', 
                                  geo_color_palette=palettes.Inferno256,
                                  geoJSONSource = 'https://raw.githubusercontent.com/rapidsai/cuxfilter/master/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json',
                                  data_points=1000, width=1100, x_range=(-126, -66), y_range=(23, 50),
                                  nan_color='white')
chart1 = charts.bokeh.bar('dti', width=400, height=400)
chart2 = charts.bokeh.bar('delinquency_12_prediction', width=400, height=400)
chart3 = charts.cudatashader.line('borrower_credit_score','delinquency_12_prediction', width=1200)

d = cux_df.dashboard([chart1, chart3], layout=layout_2, title="Custom Dashboard")

# d.add_charts([chart2, chart3])

d.show()
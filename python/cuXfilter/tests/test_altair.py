from cuXfilter import charts
import cuXfilter
from bokeh import palettes


cux_df1 = cuXfilter.DataFrame.from_arrow('/home/ajay/data/nyc_taxi_1.arrow')

chart4 = charts.cudatashader.scatter_geo(x='dropoff_x',
                                         y='dropoff_y',
                                         aggregate_fn='count',
                                         x_range=(-8239910.23,-8229529.24),
                                         y_range=(4968481.34,4983152.92))

chart5 = charts.altair.bar('passenger_count', data_points=9)


d1 = cux_df1.dashboard([chart4, chart5])

d1.show()
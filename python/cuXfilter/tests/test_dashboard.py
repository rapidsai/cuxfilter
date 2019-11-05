import pytest

from cuXfilter.dashboard import DashBoard
import cuXfilter
import cudf

class TestDataFrame():

    df = cudf.DataFrame(
            {'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}
            )
    cux_df = cuXfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title='test_title')

    def test_variables(self):
        assert self.dashboard._data.to_string() == self.df.to_string()
        assert self.dashboard.title == 'test_title'
        assert self.dashboard._dashboard.__class__ == cuXfilter.layouts.single_feature
        assert self.dashboard._theme == cuXfilter.themes.light
        assert self.dashboard.data_size_widget == True
        assert list(self.dashboard._charts.keys()) == ['_datasize_indicator']
        assert self.dashboard._data_tiles == {}
        assert self.dashboard._query_str_dict == {}
        assert self.dashboard._active_view == ''

    
    def test_add_charts(self):
        bac = cuXfilter.charts.bokeh.bar('key')
        bac.chart_type = 'chart_1'
        for _ in range(3):
            bac = cuXfilter.charts.bokeh.bar('key')
            bac.chart_type = 'chart_'+str(_+1)
            self.dashboard.add_charts([bac])

        assert list(self.dashboard._charts.keys()) == ['_datasize_indicator', 'key_chart_1',
                                                 'key_chart_2', 'key_chart_3']

    @pytest.mark.parametrize('query, inplace, result1, result2',[
        ('key<3', True, None, '   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0'),
        ('key<3', False, '   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0', None)
    ])
    def test__query(self, query, inplace, result1, result2):
        df = cudf.DataFrame(
            {'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}
            )
        cux_df = cuXfilter.DataFrame.from_dataframe(df.copy())
        dashboard = cux_df.dashboard(charts=[], title='test_title')
        query_res = dashboard._query(query_str=query, inplace=inplace)

        if query_res is not None:
            assert query_res.to_string() == result1
        else:
            assert query_res == result1

        if result2 is not None:
            assert dashboard._data.to_string() == result2
        else:
            assert dashboard._data.to_string() == df.to_string()


    @pytest.mark.parametrize('query_dict, query_str',[
        ({'col_1_chart': '6<=col_1<=9'}, '6<=col_1<=9'),
        ({}, '')
    ])
    def test__generate_query_str(self, query_dict, query_str):
        self.dashboard._query_str_dict = query_dict
        assert self.dashboard._generate_query_str() == query_str


    @pytest.mark.parametrize('active_view, result',[
        ('', '   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0\n3    3  13.0\n4    4  14.0'),
        ('key_chart_1', '   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0\n3    3  13.0')
    ])
    def test_export(self, active_view, result):
        bac = cuXfilter.charts.bokeh.bar('key')
        bac.chart_type = 'chart_1'
        self.dashboard.add_charts([bac])
        self.dashboard._query_str_dict = {'key_chart_1': '0<=key<=3'}
        self.dashboard._active_view = active_view
        
        assert self.dashboard.export().to_string() == result

    #unit tests for datatile and query functions are already present in core_aggregate and core_non_aggregate test files

    #integrated tests

    def test_calc_data_tiles(self):
        df = cudf.DataFrame(
            {'key': [0, 1, 2, 2, 2], 'val':[float(i + 10) for i in range(5)]}
            )
        cux_df = cuXfilter.DataFrame.from_dataframe(df)
        bac = cuXfilter.charts.bokeh.bar('key')
        bac1 = cuXfilter.charts.bokeh.bar('val')
        dashboard = cux_df.dashboard(charts=[bac, bac1], title='test_title', layout=cuXfilter.layouts.double_feature)



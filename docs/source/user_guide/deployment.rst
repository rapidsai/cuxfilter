Deploying a multi-user Dashboard
================================


cuXfilter dashboard when run from a jupyter/jupyterlab notebook, can be run as a single session temporary dashboard within the context of the notebook session.
Since it is a Bokeh web application, it is also possible to run it as a multi-instance, multi-user dashboard behind a load balancer (e.g: nginx load balancer).


Example
-------

Running the auto_accidents dashboard behind a local load balancer:

main.py
~~~~~~~

.. code-block:: python

    from bokeh.server.server import Server
    import cuxfilter
    import sys

    DATA_DIR = './data'

    cux_df = cuxfilter.DataFrame.from_arrow(DATA_DIR+'/auto_accidents.arrow')
    cux_df.data['ST_CASE'] = cux_df.data['ST_CASE'].astype('float64')

    def bkapp(doc):
        global cux_df
        label_map = {1: 'Sunday',    2: 'Monday',    3: 'Tuesday',    4: 'Wednesday',   5: 'Thursday',    6: 'Friday',    7: 'Saturday',    9: 'Unknown'}
        gtc_demo_red_blue_palette = [ (49,130,189), (107,174,214), (123, 142, 216), (226,103,152), (255,0,104) , (50,50,50) ]

        # declare charts
        chart1 = cuxfilter.charts.scatter(x='dropoff_x', y='dropoff_y', aggregate_col='ST_CASE',
                                                color_palette=gtc_demo_red_blue_palette)
        chart2 = cuxfilter.charts.multi_select('YEAR')
        chart3 = cuxfilter.charts.bar('DAY_WEEK', x_label_map=label_map)
        chart4 = cuxfilter.charts.bar('MONTH')

        # declare dashboard
        d = cux_df.dashboard([chart1, chart2, chart3, chart4], layout=cuxfilter.layouts.feature_and_double_base,theme = cuxfilter.themes.light, title='Auto Accident Dataset')

        # run the dashboard as a webapp:
        d._dashboard.generate_dashboard(
            d.title, d._charts, d._theme
        ).server_doc(doc)


    if __name__ == '__main__':
        server = Server({'/custom_dashboard': bkapp}, num_procs=1, allow_websocket_origin=["127.0.0.1:80"])
        server.start()

        print('running server on port '+str(port))
        server.io_loop.start()

Load balancing
~~~~~~~~~~~~~~

Based on Bokeh deployment documentation mentioned `here <https://docs.bokeh.org/en/latest/docs/user_guide/server.html#basic-reverse-proxy-setup)>`_, we can setup load balancing with nginx reverse proxying setup.

Example nginx.conf

.. code-block:: yaml

    upstream demos {
        least_conn;
        server 127.0.0.1:5001;
        server 127.0.0.1:5000;
    }

    server {
        listen 80 default_server;
        server_name _;

        location / {
            proxy_pass http://demos;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_http_version 1.1;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host:$server_port;
            proxy_buffering off;
        }

    }


Run the above as a python script:

.. code-block:: bash

    python main.py 5000
    python main.py 5001
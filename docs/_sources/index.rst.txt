Welcome to cuXfilter's documentation!
=====================================

cuXfilter solves the issues by leveraging the power of the rapids.ai stack, mainly cudf. The data is maintained in a gpu as a GPU DataFrame and operations like groupby aggregations, sorting and querying are done on the gpu itself, only returning the result as the output to the charts.

cuXfilter acts as a connector library, which provides the connections between different visualization libraries and a GPU dataframe without much hassle. This also allows the user to use charts from different libraries in a single dashboard, while also providing the interaction.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

    
   ./installation.rst
   ./dataframe.rst
   ./10 minutes to cuXfilter.ipynb
   ./charts/charts.rst
   ./layouts/Layouts.ipynb
   ./examples/examples.rst
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

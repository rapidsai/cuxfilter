import panel as pn
from IPython import display


def load_notebook_assets():
    print("loading cuxfilter notebook assets ... ")
    pn.extension()
    display.clear_output()
    print("cuxfilter notebook assets successfully loaded.")

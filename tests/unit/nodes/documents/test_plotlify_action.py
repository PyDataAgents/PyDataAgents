import os
import time
from pydag.buffers.signals.SampledSine import SampledSine
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.utils.FileUtils import FileUtils


def test_000():
    ss = SampledSine(sample_rate=100)
    
    ssa = SampledSignalAction(signal=ss, n=1000)
    ssa.install()
    ssa.execute()
    
    data = [{"x": "timestamps", "y": "values", "type": "scatter", "mode": "lines+markers"}]
    layout = {
        "title": {
            "text" : "plotlify action test_000"
        },
        "xaxis": {
            "title": {
                "text": "time [s]"
            }
        }
    }
    
    pa = PlotlifyAction(plot_path=FileUtils.parent_folder(__file__) + os.sep + "plotly_test_000.html", data=data, layout=layout)
    pa.set_buffer(ssa.get_buffer())
    pa.add_parent(ssa)
    pa.install()
    
    pa.execute()
    
def test_010():
    ss = SampledSine(sample_rate=100)    
    
    ssa = SampledSignalAction(signal=ss, n=1000)
    ssa.install()    
    ssa.execute()    
    
    layout = {
        "title": {
            "text" : "plotlify action test_010"
        },
        "xaxis": {
            "title": {
                "text": "time [s]"
            }
        }
    }
    
    pa = PlotlifyAction(plot_path=FileUtils.parent_folder(__file__) + os.sep + "plotly_test_010.html", layout=layout, input_keys=["values"])
    pa.set_buffer(ssa.get_buffer())
    pa.add_parent(ssa)
    pa.install()
    
    pa.execute()
    
def test_011():
    ss = SampledSine(sample_rate=100)    
    
    ssa = SampledSignalAction(signal=ss, n=1000)
    ssa.install()    
    ssa.execute()    
    
    layout = {
        "title": {
            "text" : "plotlify action test_011"
        },
        "xaxis": {
            "title": {
                "text": "time [s]"
            }
        }
    }
    
    pa = PlotlifyAction(plot_path=FileUtils.parent_folder(__file__) + os.sep + "plotly_test_011.html", layout=layout)
    pa.set_buffer(ssa.get_buffer())
    pa.add_parent(ssa)
    pa.install()
    
    pa.execute()
    

def test_020():
    ss = SampledSine(sample_rate=100)    
    
    ssa = SampledSignalAction(signal=ss, n=437)
    ssa.install()    
    ssa.execute()    
    
    layout = {
        "title": {
            "text" : "plotlify action test_020"
        },
        "xaxis": {
            "title": {
                "text": "samples [-]"
            }
        }
    }
    
    pa = PlotlifyAction(plot_path=FileUtils.parent_folder(__file__) + os.sep + "plotly_test_020.html", layout=layout, open_in_browser=True, auto_refresh=1, input_keys=["values"])
    pa.set_buffer(ssa.get_buffer())
    pa.add_parent(ssa)
    pa.install()
    
    pa.execute()
    
    pa.open_in_browser = False
    
    for i in range(0, 10):
        time.sleep(1)
        ssa.execute()
        pa.execute()
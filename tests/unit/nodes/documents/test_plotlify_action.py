import os
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
    pa._buffer = ssa._buffer
    pa.install()
    pa.add_parent(ssa)
    
    pa.execute()
     
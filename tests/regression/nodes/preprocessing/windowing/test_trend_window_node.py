import os
import time

from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.preprocessing.windowing.TrendWindowNode import TrendWindowNode
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.services.plot.PlotlyElements import ColorGradient
from pydag.utils.FileUtils import FileUtils


def test_000():
    
    s = Sine(f = 2.0, a = 1.0, p = 0.0, n = 0.25)
    sb = SignalBuffer(signal = s, capacity=150, sampling_period=10)
    sb.install()
    
    time.sleep(2)
    
    lba = LinkBufferAction()
    lba.set_buffer(sb)
    
    buf = DictBuffer(timestamps_enabled=False, index_enabled=False)
    twn = TrendWindowNode(max_windows=10, input_keys=["values"], n=50)
    twn.set_buffer(buf)
    twn.add_parent(lba)
    twn.install()
    
    layout = {
        "title": {
            "text" : "plotlify action test_000"
        },
        "xaxis": {
            "title": {
                "text": "samples [-]"
            }
        }
    }
    
    colors = ColorGradient.red(twn.max_windows)
    pa = PlotlifyAction(plot_path=FileUtils.parent_folder(__file__) + os.sep + "plotly_test_000.html", layout=layout, open_in_browser=True, auto_refresh=2, colors=colors)
    pa.add_parent(twn)
    pa.install()
    
    twn.execute()
    pa.execute()
    
    pa.open_in_browser = False
    
    while True:
        time.sleep(2)
        twn.execute()
        pa.execute()
        
        
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.HuggingFaceAction import HuggingFaceAction
from pydag.buffers.ListBuffer import ListBuffer

def test_hf_task_list():
    print(HuggingFaceAction.task_list())
    
    
def test_sentiment_analysis():
    
    buf = ListBuffer(id="LB1", capacity=3)
    buf.install()
    
    buf.push("I love you")
    buf.push("Today after riding a roller coaster, i feel sick!")
    buf.push("""
             I really wanted to love this product. At first glance, the design is sleek
             and the build quality feels premium, which made a great first impression.
             However, after using it for a few days, I started noticing several frustrating
             issues. The battery life is inconsistent, sometimes lasting all day
             and other times barely making it through a few hours. The software also feels
             unfinished, with occasional glitches that interrupt the experience.
             That said, customer support was surprisingly responsive and helpful,
             which partially made up for the inconvenience. If the bugs get fixed
             in future updates, this could easily become one of the best products
             in its category—but in its current state, it's hard to fully recommend it.
             """
            )
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hfn = HuggingFaceAction(task="sentiment-analysis", output_keys=["sentiment"])
    hfn.add_parent(lba)
    hfn.install()
    
    hfn.execute()
    
    print(hfn.get_buffer().data())
    
    assert hfn.get_buffer().size() == buf.size(), "buffer size of hugging face node does not conform with size of listbuffer"
    
def test_sentiment_analysis_1key():    
    buf = ListBuffer(id="LB1", capacity=3)
    buf.install()
    
    buf.push("I love you")
    buf.push("Today after riding a roller coaster, i feel sick!")
    buf.push("""
             I really wanted to love this product. At first glance, the design is sleek
             and the build quality feels premium, which made a great first impression.
             However, after using it for a few days, I started noticing several frustrating
             issues. The battery life is inconsistent, sometimes lasting all day
             and other times barely making it through a few hours. The software also feels
             unfinished, with occasional glitches that interrupt the experience.
             That said, customer support was surprisingly responsive and helpful,
             which partially made up for the inconvenience. If the bugs get fixed
             in future updates, this could easily become one of the best products
             in its category—but in its current state, it's hard to fully recommend it.
             """
            )
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hfn = HuggingFaceAction(task="sentiment-analysis")
    hfn.add_parent(lba)
    hfn.install()
    
    hfn.execute()
    
    print(hfn.get_buffer().data())
    
    assert hfn.get_buffer().size() == buf.size(), "buffer size of hugging face node does not conform with size of listbuffer"
    
def test_translation():
    
    buf = ListBuffer(id="LB1", capacity=3)
    buf.install()    
    buf.push("I'm a rock'n-roll teddy bear riding a harley davidson")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hfn = HuggingFaceAction(task="translation_en_to_de", output_keys=["translation"])
    hfn.add_parent(lba)
    hfn.install()
    
    hfn.execute()
    
    print(hfn.get_buffer().data())
    
    assert hfn.get_buffer().size() == buf.size(), "buffer size of hugging face node does not conform with size of listbuffer"
    
def test_translation_with_model():
    
    buf = ListBuffer(id="LB1", capacity=3)
    buf.install()    
    buf.push("I'm a rock'n-roll teddy bear riding a harley davidson")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hfn = HuggingFaceAction(task="translation_en_to_de", model="google-t5/t5-base", output_keys=["translation"])
    hfn.add_parent(lba)
    hfn.install()
    
    hfn.execute()
    
    print(hfn.get_buffer().data())
    
    assert hfn.get_buffer().size() == buf.size(), "buffer size of hugging face node does not conform with size of listbuffer"
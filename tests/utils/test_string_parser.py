from PyDataGrabber.src.utils.StringParser import StringParser


def test_000():
    s = "topic=this/is/a/topic;id=topic1"
    d = StringParser.string_to_dict(s)
    print(d)
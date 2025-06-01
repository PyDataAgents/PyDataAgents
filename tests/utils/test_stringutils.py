from pydatagrabber.utils.StringUtils import StringUtils


def test_000():
    s = "topic=this/is/a/topic;id=topic1"
    d = StringUtils.string_to_dict(s)
    print(d)
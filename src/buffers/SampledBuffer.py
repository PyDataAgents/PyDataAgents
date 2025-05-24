from PyDataGrabber.src.buffers.TimedBuffer import TimedBuffer


class SampledBuffer(TimedBuffer):
    """
    A buffer that samples a signal at a specified interval.
    """

    def __init__(self):
        """
        Initializes the SampledBuffer with a sample interval.

        :param sample_interval: The time interval between samples in seconds.
        """
        super().__init__()
        

    
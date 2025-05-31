from ..buffers.Buffer import Buffer

class BufferUtils:
        
    @staticmethod    
    def to_dict(buffer : Buffer):
        d = {}
        d[buffer.id] = buffer
        return d
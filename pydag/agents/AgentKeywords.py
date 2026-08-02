import os

class AgentKeywords:
    """
    Configuration class for the agent application.
    """
          
    # Agent Keywords   
    AGENT = "agent"
    BUFFER = "buffer"
    BUFFERS = "buffers"
    SERVICE = "service"
    SERVICES = "services"
    
    TYPE = "type"
    ID = "id"
    DESCRIPTION = "description"
    VALUE = "value"
    
    # Service Keywords    
    ADDRESS = "address"
    ADDRESSES = "addresses"
    

    # Buffer Keywords    
    DATA_TYPE = "data_type"
    CAPACITY = "capacity"
    UNIT = "unit"
    INITIAL_VALUES = "initial_values"    
    DATA = "data"
    META = "meta"    
    VALUES = "values"
    TIMESTAMPS = "timestamps"   
    INDEX = "index" 
    INFINITE_CAPACITY = -1  
    
    # Node Config Keywords  
    FEATURE = "feature"
    FEATURES = "features"
    Y_HAT = "y_hat"
    
    # Service Config Keywords
    MAX_EXPONENTIAL_SECONDS = 60 * 60 * 24 * 3 # 3 days in seconds

    # resource folder
    RESOURCE_FOLDER = "." + os.sep + "resources"  + os.sep
    MODEL_RESOURCE_FOLDER = RESOURCE_FOLDER + "models" + os.sep
    EMBEDDINGS_RESOURCE_FOLDER = RESOURCE_FOLDER + "embeddings" + os.sep
    SAVE_FOLDER = ".save" + os.sep
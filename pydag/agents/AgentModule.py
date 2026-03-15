class AgentModule:
    
    @staticmethod
    def load_core_modules():
        # adapters
        
        # services
        import pydag.services.rest.RestService
        import pydag.services.ObserverService
        import pydag.services.mappings.MappingService
        import pydag.services.statemachine.SimpleActionService
        import pydag.services.statemachine.SimpleStatemachine
        import pydag.services.statemachine.SFCService
        import pydag.services.plot.PlotlifyService
        
        # nodes
        import pydag.nodes.script.ScriptAction
        import pydag.nodes.utils.MailAction
        # TODO include all util nodes here
        
        AgentModule.load_buffer_modules()
        
        return
    
    @staticmethod
    def load_iiot_modules(skip_ads : bool = False):
        # adapters
        if not skip_ads:
            import pydag.adapters.ads.AdsAdapter
        import pydag.adapters.mqtt.MQTTAdapter
        import pydag.adapters.audio.AudioAdapter
        import pydag.adapters.opcua.OpcUaAdapter
        import pydag.adapters.s7.S7Adapter
        import pydag.adapters.socket.SerialAdapter
        import pydag.adapters.socket.TCPClientAdapter
        import pydag.adapters.socket.WebSocketAdapter
        import pydag.adapters.socket.ifmvse.VSEAdapter
        
        # services
        import pydag.services.office.MSGraphService
        
        # nodes
        import pydag.nodes.http.HttpGetAction
        import pydag.nodes.http.HttpPostAction
        
        return
    
    @staticmethod
    def load_database_modules():
        # adapters
        
        # services
        
        # nodes
        
        return
    
    @staticmethod
    def load_document_modules():
        # adapters
        
        # services
        
        # nodes
        
        return
    
    @staticmethod
    def load_llm_modules():
        # adapters
        
        # services
        import pydag.services.llm.LLMService
        import pydag.services.llm.LLMRestService
        import pydag.services.llm.LLMSQLService
        import pydag.services.llm.RAGService
        
        # nodes
        import pydag.nodes.llm.LLMChatAction
        import pydag.nodes.llm.LLMOCRAction
        import pydag.nodes.llm.LLMScriptElement
        import pydag.nodes.llm.LLMImageAnalysisAction
        
        return
    
    @staticmethod
    def load_vision_modules():
        # adapters
        import pydag.adapters.vision.WebcamAdapter
        
        # services
        import pydag.services.vision.WebcamVideoRollbackService
        
        # nodes
        import pydag.nodes.documents.OCRAction
        
        return
    
    @staticmethod
    def load_buffer_modules():
        import pydag.buffers.DictBuffer
        import pydag.buffers.ListBuffer
        import pydag.buffers.TimedBuffer
        import pydag.buffers.SignalBuffer
        import pydag.buffers.SampledBuffer
        import pydag.buffers.DatasetBuffer
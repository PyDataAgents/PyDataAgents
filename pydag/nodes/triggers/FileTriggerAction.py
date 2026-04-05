from dataclasses import dataclass, field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from pydag.agents.Agent import Agent
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.triggers.ObserverTriggerAction import ObserverTriggerAction


@dataclass
class FileTriggerAction(BufferNode, ObserverTriggerAction):
    
    folder : str = field(default=None, metadata={"description": "folder to wach for file events"})
    recursive : bool = field(default=False, metadata={"description": "listen to events in subfolders as well"})
    create_events : bool = field(default=True, metadata={"description": "listen to create events"})
    modified_events : bool = field(default=False, metadata={"description": "listen to modified events"})
    moved_events : bool = field(default=False, metadata={"description": "listen to moved events"})
    delete_events : bool = field(default=False, metadata={"description": "listen to delete events"})
    output_keys : list[str] = field(default_factory=lambda:["filepaths"], metadata={"description": "default output key"})
    
    def __post_init__(self):
        super().__post_init__()
        self._file_observer : Observer = None
    
    def _on_install(self, agent : Agent = None):
        BufferNode._on_install(self, agent)
        ObserverTriggerAction._on_install(self, agent)
        
    def start_trigger(self):
        self._file_observer = Observer()
        self._file_observer.schedule(_FolderHandler(self), path=self.folder, recursive=self.recursive)
        self._file_observer.start()

   
class _FolderHandler(FileSystemEventHandler):
    
    def __init__(self, trigger_action : FileTriggerAction):
        self._trigger_action = trigger_action
    
    def on_created(self, event):
        if self._trigger_action.create_events:
            self._trigger_action.get_buffer().push({self._trigger_action.output_keys[0]: event.src_path})
            self._trigger_action.trigger()

    def on_modified(self, event):
        if self._trigger_action.modified_events:
            self._trigger_action.get_buffer().push({self._trigger_action.output_keys[0]: event.src_path})
            self._trigger_action.trigger()
            
    def on_deleted(self, event):
        if self._trigger_action.delete_events:
            self._trigger_action.get_buffer().push({self._trigger_action.output_keys[0]: event.src_path})
            self._trigger_action.trigger()

    def on_moved(self, event):
        if self._trigger_action.moved_events:
            self._trigger_action.get_buffer().push({self._trigger_action.output_keys[0]: event.src_path})
            self._trigger_action.trigger()
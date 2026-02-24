from dataclasses import dataclass, field
from docxtpl import DocxTemplate

from ...agents.Agent import Agent
from ...utils.FileUtils import FileUtils
from ...nodes.NodeException import NodeException
from ...nodes.BufferNode import BufferNode
from ...nodes.Action import Action


@dataclass
class DocxTemplateAction(BufferNode, Action):    
    """ `Action` for writing data to DOCX template document.
    
    buffers of parent elements can be used to populate the docx file, if `buffer_id` or `set_buffer(...)` is specified then only this buffer is used
    """
    output_path: str = field(default="output.docx", metadata={"description": "output path for the template to be saved to"})
    template_path: str = field(default=None, metadata={"description": "template file path"})
    
    def _on_install(self, agent : Agent = None):
        if self._buffer is None:
            if agent is not None:
                buf = agent.get_buffer(self.buffer_id)                
                if buf:
                    self._buffer = buf
    
    def _on_execute(self):
        if FileUtils.exists_file(self.template_path):
            doc = DocxTemplate(self.template_path)
            context = {}
            if self._buffer is not None:
                data = self._buffer.data(self.n, self.persistent)
                context.update(data)
            else:
                context = self.get_parent_data()            
            if len(context) > 0:
                doc.render(context)
                FileUtils.create_dir(FileUtils.parent_folder(self.output_path))
                doc.save(self.output_path)
            else:
                raise NodeException("No context was specified or found in specified buffers/parents")
        else:
            raise NodeException(f"{self.cname()} template file does not exist: {self.template_path}")
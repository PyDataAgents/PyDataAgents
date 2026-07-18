from dataclasses import dataclass, field


from ..ServiceException import ServiceException
from ...agents.Agent import Agent
from ...utils.FileUtils import FileUtils
from ..WriteService import WriteService


@dataclass
class DocxService(WriteService):
    """ `MappingService` for writing data to DOCX documents.
    
    The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.
    If no addresses are specified all buffer keys are directly mapped to the context of the word template
    """
    output_path: str = field(default="output.docx")
    template_path: str = field(default=None)

    def __post_init__(self):
        super().__post_init__()
        self._doc = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if FileUtils.exists_file(self.template_path):
            from docxtpl import DocxTemplate
            self._doc = DocxTemplate(self.template_path)
        else:
            raise ServiceException(f"{self.__class__.__name__} template file does not exist: {self.template_path}")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)

    def write_to_sink(self):
        """ Write data from buffers to the document.
        Args:
            buffers (dict[str, Buffer]): Dictionary mapping addresses to buffers
            addresses (list[str]): List of addresses to write
            n (int): Number of samples to write
            persistent (bool): If False, removes written values from buffer
        """
        context = {}
        if len(self.addresses) > 0:
            pass
        else:
            for buffer in self.get_buffers().values():
                data = buffer.data(self.n, self.persistent)
                context.update(data)
        self._doc.render(context)
        FileUtils.create_dir(FileUtils.parent_folder(self.output_path))
        self._doc.save(self.output_path)

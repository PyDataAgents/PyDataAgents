from dataclasses import dataclass, field

from loguru import logger


from ...agents.Agent import Agent
from ...utils.FileUtils import FileUtils
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer

@dataclass
class DocxAdapter(WriteAdapter):
    """ `Adapter` for writing data to DOCX documents.
    
    The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.
    If no addresses are specified all buffer keys are directly mapped to the context of the word template
    """
    output_path: str = field(default="output.docx")
    template_path: str = field(default=None)

    def __post_init__(self):
        self._doc = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
    
    def _on_connect(self) -> bool:
        """Connect to the document by creating or loading it from template.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if FileUtils.exists_file(self.template_path):
            from docxtpl import DocxTemplate

            self._doc = DocxTemplate(self.template_path)
            return True
        else:
            logger.error(f"DocxAdapter template file does not exist: {self.template_path}")
            return False

    def _on_disconnect(self) -> bool:
        return True

    def _on_write(self, buffers: dict[str, Buffer], addresses: list[str], n: int, persistent: bool):
        """ Write data from buffers to the document.
        Args:
            buffers (dict[str, Buffer]): Dictionary mapping addresses to buffers
            addresses (list[str]): List of addresses to write
            n (int): Number of samples to write
            persistent (bool): If False, removes written values from buffer
        """
        context = {}
        if len(addresses) > 0:
            pass
        else:
            for buffer in buffers.values():
                data = buffer.data(n, persistent)
                context.update(data)
            
        self._doc.render(context)
        FileUtils.create_dir(FileUtils.parent_folder(self.output_path))
        self._doc.save(self.output_path)

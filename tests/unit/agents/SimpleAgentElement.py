from pydag.agents.Agent import Agent
from pydag.agents.AgentElement import AgentElement


class SimpleAgentElement(AgentElement):
    """
    A simple implementation of the AgentElement class for testing purposes.
    This class can be used to test the functionality of the AgentElement class
    and its interactions with other components of the DataGrabber application.
    """

    def _on_install(self, agent : Agent = None):
        """
        Installation logic for the SimpleAgentElement.
        This method can be used to perform any necessary setup or initialization
        when the element is installed in an agent.

        Args:
            agent (Agent, optional): The agent in which the element is being installed. Defaults to None.
        """
        print(f"Installing {self.name()} in agent {agent.name() if agent else 'None'}")

    def _on_uninstall(self, agent : Agent = None):
        """
        Uninstallation logic for the SimpleAgentElement.
        This method can be used to perform any necessary cleanup when the element
        is uninstalled from an agent.

        Args:
            agent (Agent, optional): The agent from which the element is being uninstalled. Defaults to None.
        """
        print(f"Uninstalling {self.name()} from agent {agent.name() if agent else 'None'}")
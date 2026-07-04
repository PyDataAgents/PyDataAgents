from __future__ import annotations
from functools import wraps
from nicegui import app, ui
from typing import TYPE_CHECKING

from ..auth.Auth import AuthManager, TokenManager
from .UIElements import UIPage

if TYPE_CHECKING:
    from ..AgentStore import AgentStore
    
def requires_role(*roles, login_url="/login"):
    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = app.storage.user.get("user", None)
            
            if not user:
                ui.navigate.to(login_url)
                return
            
            user_roles = set(user.get("roles", []))

            if not user_roles.intersection(roles):
                ui.label("Access denied")
                return

            return await func(*args, **kwargs)

        return wrapper

    return decorator

class UIAgentStoreLoginPage(UIPage):
    
    path = "/agentstore/login"
    
    def _render(self):
        username = ui.input("Username")
        password = ui.input("Password", password=True)

        def do_login():

            user = AuthManager(None).authenticate(
                username.value,
                password.value,
            )

            if not user:
                ui.notify("Invalid credentials")
                return

            token = TokenManager.create_token(user)
            
            # store per-user session (server-side)
            app.storage.user["access_token"] = token
            app.storage.user["user"] = user

            ui.navigate.to("/agentstore")

        ui.button("Login", on_click=do_login)
            

class UIAgentStorePage(UIPage):
    """ `UIPage` for interacting with `AgentStore` """
    
    path = "/agentstore"
    
    def __init__(self, agent_store : AgentStore):
        super().__init__(None)
        self._agent_store = agent_store
        self._agent_column : ui.column = None
        self._template_column : ui.column = None
    
    def register(self):
        
        @ui.page(self.path)
        @requires_role("member", "admin", login_url="/agentstore/login")
        async def page():
            self._ui_components.clear()
            self._render()
            # check all ui components if timer is required
            requires_update : bool = False
            for component in self._ui_components:
                if component.requires_update:
                    requires_update = True
                    break                    
            if requires_update:
                self._timer = ui.timer(self._refresh_interval, lambda: [
                    component.update() for component in self._ui_components if component.requires_update 
                ])
    
    def logout(self):
        app.storage.user.clear("access_token")
        app.storage.user.clear("user")
        ui.navigate.to(self.path)
    
    def _render(self):
        self.create_header("Agent Store - Dashboard")
        with ui.grid().classes("w-full h-screen").style("grid-template-columns: 3fr 2fr;"):
            # column for instantiated agents of this user            
            self._agent_column = ui.column()
            # column for available templates
            self._template_column = ui.column()
            self._refresh_dashboard()

    def _refresh_dashboard(self):        
        user = get_current_user()
        user_id = user.get("id")
        self._agent_column.clear()
        self._template_column.clear()
        with self._agent_column:
            user_agents = self._agent_store.get_user_agents(user_id)
            if len(user_agents) > 0:
                for agent in user_agents:
                    with ui.card():
                                                
                        def release(aid=agent.id):
                            self._agent_store.release_agent(user_id, aid)
                            self._refresh_dashboard()  # Refresh the dashboard after releasing an agent
                        
                        def reconfigure(aid=agent.id):
                            self._agent_store.configure_agent(user_id, aid)
                            self._refresh_dashboard()  # Refresh the dashboard after reconfiguring an agent
                        
                        def terminate(aid=agent.id):
                                self._agent_store.terminate_agent(user_id, aid)
                                self._refresh_dashboard()  # Refresh the dashboard after terminating an agent       
                        
                        ui.markdown(f"**{agent.id}**")
                        ui.label(agent.description or "")
                        if agent.is_running():
                            ui.label("RUNNING").style("bg-green-500 text-white p-2 rounded")
                            ui.button("Terminate", on_click=terminate)                                
                            ui.button("Reconfigure", on_click=reconfigure)                                
                        else:
                            ui.label("STOPPED").style("bg-gray-500 text-white p-2 rounded")                                                         
                            ui.button("Release", on_click=release)                            
                            ui.button("Reconfigure", on_click=reconfigure)
                            
        with self._template_column:
            agent_configs = self._agent_store.get_templates()
            if len(agent_configs) > 0:
                for agent_id, agent_config in agent_configs.items():
                    with ui.card().classes("w-full mb-2"):
                        ui.markdown(f"**{agent_id}**")
                        ui.label(agent_config.to_dict().get("description", ""))
                        
                        def create_agent_from_template(aid=agent_id):
                            self._agent_store.add_agent_from_template(user_id, aid)
                            self._refresh_dashboard()  # Refresh the dashboard after creating a new agent
                        
                        ui.button("Create Agent", on_click=create_agent_from_template)
        
def get_current_user() -> dict:
    user = app.storage.user.get("user")
    return user
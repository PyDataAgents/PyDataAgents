from __future__ import annotations
from dataclasses import dataclass, field
from functools import wraps
import json
from nicegui import app, ui
from typing import TYPE_CHECKING


from ..Agent import Agent
from ..AgentKeywords import AgentKeywords
from ..app.AgentApp import AgentApp
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

@dataclass
class UIAgentStoreLoginPage(UIPage):
    
    path : str = field(default="/store/login")
    
    def _render(self):
        self.create_header("AgentStore - Login", self.path)
        with ui.column().classes("w-full h-screen flex items-center justify-center"):
            with ui.card().classes("w-[350px] p-6 shadow-lg"):

                ui.label("Login").classes("text-h6 mb-4 text-center")
                username = ui.input("Username").classes("w-full")
                password = ui.input("Password", password=True).classes("w-full")

                def do_login():
                    user = AuthManager(None).authenticate(username.value, password.value)
                    if not user:
                        ui.notify("Invalid credentials")
                        return

                    token = TokenManager.create_token(user)
                    
                    # store per-user session (server-side)
                    app.storage.user["access_token"] = token
                    app.storage.user["user"] = user

                    ui.navigate.to("/store")

                ui.button("Login", on_click=do_login).classes("w-full mt-4")
            
@dataclass
class UIAgentStorePage(UIPage):
    """ `UIPage` for interacting with `AgentStore` """
    
    path : str = field(default="/store")
    
    def __post_init__(self):
        super().__post_init__()
        self._agent_store : AgentStore = None
        self._agent_column : ui.column = None
        self._template_column : ui.column = None
    
    def register(self, agent_app : AgentApp):
        
        self._agent_app = agent_app
        
        @ui.page(self.path)
        @requires_role("member", "admin", login_url="/store/login")
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
                self._timer = ui.timer(self.refresh_interval, lambda: [
                    component.update() for component in self._ui_components if component.requires_update 
                ])
    
    def logout(self):
        app.storage.user.clear("access_token")
        app.storage.user.clear("user")
        ui.navigate.to(self.path)
    
    def _render(self):
        self.create_header("Agent Store - Dashboard", self.path + "/login")
        with ui.grid().classes("w-full").style("grid-template-columns: 3fr 2fr;"):
            self._agent_column = ui.column().classes("w-full")
            self._template_column = ui.column().classes("w-full")
            self._refresh()
        
    def _refresh(self):
        user = app.storage.user.get("user")
        user_id = user.get("id")
        self._agent_column.clear()
        self._template_column.clear()
        with self._agent_column:
            user_agents = self._agent_store.get_user_agents(user_id)
            if len(user_agents) > 0:
                ui.label(f"My {Agent.__name__}s").classes("text-h4")
                for agent_app in user_agents:
                    with ui.card().classes("w-full mb-2"):                                                        
                        with ui.row().classes("items-center justify-between w-full p-1"):
                            ui.markdown(f"**{agent_app.get_agent().__class__.__name__} - {agent_app.get_agent().id}**")                                
                            if agent_app.get_agent().is_running():
                                ui.label("RUNNING").classes("bg-green-500 text-white p-2 rounded")                                                    
                            else:
                                ui.label("STOPPED").classes("bg-gray-500 text-white p-2 rounded")
                            
                            def remove_agent(aid : str = agent_app.get_agent().id):
                                self._agent_store.remove_agent(user_id, aid)
                                self._refresh()  # Refresh the dashboard after releasing an agent
                                                        
                            ui.button("X", on_click=remove_agent).tooltip("Remove Agent")  
                        
                        def release_agent(aid : str = agent_app.get_agent().id):
                            self._agent_store.release_agent(user_id, aid)
                            self._refresh()  # Refresh the dashboard after releasing an agent
                        
                        def reconfigure_agent(aid: str = agent_app.get_agent().id):
                            with ui.dialog() as dialog:
                                with ui.card():
                                    ui.label("Configure Agent")
                                    # get agent config
                                    agent_config : dict = self._agent_store.get_agent(user_id, aid).config_options()
                                    editor = ui.codemirror(value=json.dumps(agent_config, indent=2), language="json").classes("w-full h-64")
                                    
                                    def save_config():
                                        try:
                                            new_config = json.loads(editor.value)
                                            self._agent_store.configure_agent(user_id, aid, new_config)
                                            ui.notify(f"Updated config: {new_config}", color="green")
                                        except Exception as e:
                                            ui.notify(f"Invalid JSON: {e}", color="red")

                                    ui.button("Save", on_click=save_config)
                                    
                                    def close_dialog():
                                        dialog.close()
                                        self._refresh()  # Refresh the dashboard after reconfiguring an agent
                                                                                
                                    ui.button('Close', on_click=close_dialog)
                                    
                            dialog.open()
                        
                        def terminate_agent(aid: str = agent_app.get_agent().id):
                            self._agent_store.terminate_agent(user_id, aid)
                            self._refresh()  # Refresh the dashboard after terminating an agent                                                                      
                        
                        ui.label(agent_app.get_agent().description or "")
                        if agent_app.get_agent().is_running():
                            with ui.row():
                                ui.button("Terminate", on_click=terminate_agent).tooltip("Terminate Agent")                    
                                ui.button("Reconfigure", on_click=reconfigure_agent).tooltip("Reconfigure Agent")
                        else:                                                                    
                            with ui.row():
                                ui.button("Release", on_click=release_agent).tooltip("Terminate Agent") 
                                ui.button("Reconfigure", on_click=reconfigure_agent).tooltip("Reconfigure Agent")
                                
        with self._template_column:
            app_configs = self._agent_store.get_templates()
            if len(app_configs) > 0:                    
                ui.label("Agent Templates").classes("text-h4")
                for agent_id, app_config in app_configs.items():
                    with ui.card().classes("w-full mb-2 bg-secondary"):
                        # 🔹 Dialog (centered by default)
                        with ui.dialog() as dialog:
                            with ui.card().classes("w-[600px] max-w-[90vw]"):
                                ui.label("Agent Template Configuration").classes("text-h6 mb-2")
                                ui.code(json.dumps(app_config, indent=2), language="json").classes("w-full h-64")
                                ui.button("Close", on_click=dialog.close).classes("mt-2")

                        # 🔹 Top-right help button
                        ui.button("?", on_click=dialog.open).props("flat round dense").classes("absolute top-2 right-2").tooltip("show configuration")
                        
                        ui.markdown(f"**{agent_id}**")
                        ui.label(app_config.get(AgentKeywords.AGENT, {}).get(AgentKeywords.DESCRIPTION, ""))
                        
                        def create_agent_from_template(aid : str = agent_id):
                            self._agent_store.add_agent_from_template(user_id, aid)
                            self._refresh()  # Refresh the dashboard after creating a new agent
        
                        ui.button("Create Agent", on_click=create_agent_from_template).tooltip("create agent from template")
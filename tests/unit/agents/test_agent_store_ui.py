from nicegui import ui, run
import copy
import uuid

from pydag.agents.AgentStore import AgentStore
from pydag.agents.Agent import Agent


store = AgentStore()
# try loading templates from configured paths (if any)
try:
    store.load_templates()
except Exception:
    # ignore template loading errors for now
    pass

# ensure some demo data so the UI is usable out of the box
if len(store.get_users()) == 0:
    store.add_user('demo')
    store.add_user('alice')

if len(store.get_templates()) == 0:
    # create simple example templates
    t1 = Agent(description='Example template A')
    t2 = Agent(description='Example template B')
    store.add_template(t1)
    store.add_template(t2)


session_state: dict = {'user': None}


def refresh_dashboard(containers: dict):
    user = session_state.get('user')
    if not user:
        return

    # refresh user agents
    agents_container = containers['agents']
    agents_container.clear()
    user_agents = store.get_user_agents(user)
    if len(user_agents) == 0:
        with agents_container:
            ui.label('No agents for user')
    for ag in user_agents:
        with agents_container.row():
            ui.markdown(f'**{ag.id}**')
            ui.label(ag.description or '')
            state = 'running' if ag.is_running() else 'stopped'
            ui.label(state)
            if ag.is_running():
                def terminate(aid=ag.id):
                    store.terminate_agent(user, aid)
                    refresh_dashboard(containers)

                ui.button('Terminate', on_click=terminate)
            else:
                def release(aid=ag.id):
                    store.release_agent(user, aid)
                    refresh_dashboard(containers)

                ui.button('Release', on_click=release)

    # refresh templates
    templates_container = containers['templates']
    templates_container.clear()
    templates = store.get_templates()
    if len(templates) == 0:
        with templates_container:
            ui.label('No templates available')
    for tid, desc in templates:
        with templates_container:
            with ui.row():
                ui.markdown(f'**{tid}**')
                ui.label(desc or '')

                def create_from_template(tid_local=tid):
                    tmpl = None
                    try:
                        tmpl = store._templates.get(tid_local)
                    except Exception:
                        tmpl = None
                    if tmpl is None:
                        ui.notify('Template not found', color='negative')
                        return
                    new_agent = copy.deepcopy(tmpl)
                    new_agent.id = str(uuid.uuid4())
                    store.add_agent(session_state['user'], new_agent)
                    ui.notify(f'Created agent {new_agent.id}', color='positive')
                    refresh_dashboard(containers)

                ui.button('Create', on_click=create_from_template)


def main_page():
    containers = {}

    global login_card
    # capture login card reference
    # (nicegui context manager returned reference stored above)
    # hack: access first card on page as login_card
        
    login_card = ui.card().style('max-width:600px;margin:auto;margin-top:50px')
    with login_card:
        ui.label('Login to Agent Store').style('font-weight:600')
        user_input = ui.input('User ID')

        def try_login():
            uid = user_input.value.strip() if user_input.value else ''
            if uid == '':
                ui.notify('Please provide a user id', color='negative')
                return
            if uid not in store.get_users():
                ui.notify('User id not found', color='negative')
                return
            session_state['user'] = uid
            ui.notify(f'Logged in as {uid}', color='positive')
            login_card.visible = False
            dashboard_card.visible = True
            refresh_dashboard(containers)

        ui.button('Login', on_click=try_login)

    # dashboard (hidden until login)
    dashboard_card = ui.card().style('max-width:900px;margin:auto;margin-top:30px')
    with dashboard_card:
        ui.label('Agent Dashboard').style('font-weight:600')
        with ui.row():
            with ui.column().style('flex:1;margin-right:10px') as agents_col:
                ui.label('Your Agents')
            with ui.column().style('flex:1;margin-left:10px') as templates_col:
                ui.label('Templates')

        containers['agents'] = agents_col
        containers['templates'] = templates_col

    # initially hide dashboard
    dashboard_card.visible = False

    
if __name__ in {"__main__", "__mp_main__"}:
    main_page()
    ui.run(title='Agent Store UI', host="localhost", port=10001, reload=True)

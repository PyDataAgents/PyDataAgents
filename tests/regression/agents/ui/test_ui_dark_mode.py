from nicegui import ui
from nicegui.testing import User

def setup_app():

    ui.colors(
        primary='#005B95',
        secondary='#A8A8A9',
        accent='#C43726',
    )

    ui.dark_mode().enable()

    @ui.page('/')
    def home():
        ui.label('Home')

    @ui.page('/dashboard')
    def dashboard():
        ui.label('Dashboard')

def test_ui():
    user = User(setup_app)
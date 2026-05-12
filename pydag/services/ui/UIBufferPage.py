from nicegui import ui

from pydag.services.ui.UIElements import PlotCard, UIPage


class UIBufferPage(UIPage):
    """ `UIPage` for diplaying all `Buffer` data from connected `Agent` """
    
    path = "/buffers"
    
    def _render(self):
        with ui.header().classes('bg-primary text-white'):
            ui.label('Buffer Store - Dashboard').classes('font-bold text-lg')
        
        def toggle_timer():
            self._timer.active = not self._timer.active
            button.set_text('Pause' if self._timer.active else 'Start')
        button = ui.button('Pause', on_click=toggle_timer)
        
        with ui.grid(columns=2).classes("w-full gap-4"):
            for k, b in self._service.get_agent().buffer_store.items():
                plot_card = PlotCard(self, b)
                self.add_ui_component(plot_card)
                #self._service.get_update_routines().append(plot_card.update)
                
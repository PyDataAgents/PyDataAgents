
from __future__ import annotations

import asyncio
import math
from pathlib import Path
from typing import Mapping

import yaml

from pydag.services.datamodel.formula_engine import FormulaEngine
from pydag.services.datamodel.formula_models import SymbolInput
from pydag.services.datamodel.formula_registries import FormulaRegistry


"""Generate NiceGUI calculation forms from a YAML layout.

Example::

    from nicegui import ui
    from modelify.mechcp.ui import FormulaUI

    page = FormulaUI('modelify/mechcp/ui/fugenpressung_ui.yaml')
    page.register('/')
    ui.run()

Each tab is an independent solve request. All its inputs are required and use
the units declared by the formula set. Widget state is local to each client.
"""


def _apply_theme() -> None:
    """Apply the shared palette to the current client's formula pages."""
    from nicegui import ui

    ui.colors(primary='#0A224F', secondary='#429FCA', accent='#F28701',
              negative='#CE0F0C', warning='#FEC703', info='#A2DCEC')
    ui.context.client.content.classes('formula-theme')
    ui.add_css('''
        .formula-theme {
            color: #0A224F;
            background: #E8E8E8;
            min-height: 100vh;
            padding: 24px;
        }
        .formula-theme .q-card {
            border: 1px solid #429FCA;
            border-top: 4px solid #429FCA;
            border-radius: 12px;
            color: #0A224F;
            background: white;
        }
        .formula-theme a { color: #0A224F; }
        .formula-theme a:hover { text-decoration-thickness: 3px; }
        .formula-theme a:focus-visible {
            outline: 3px solid #F28701;
            outline-offset: 4px;
        }
        .formula-theme .formula-muted { color: #0A224F; opacity: 0.8; }
        .formula-theme .formula-tag {
            background: #FEC703;
            color: #0A224F;
            border-radius: 6px;
        }
        .formula-theme .q-field { background: white; border-radius: 4px; }
        .formula-theme .q-field__native,
        .formula-theme .q-field__label { color: #0A224F; }
        .formula-theme .q-tabs {
            background: #0A224F;
            color: #A2DCEC;
            border-radius: 8px;
        }
        .formula-theme .q-tab--active { color: #FEC703; }
        .formula-theme .q-tab__indicator { background: #F28701; }
        .formula-theme .q-tab-panels { color: #0A224F; border-radius: 8px; }
        .formula-theme .formula-action {
            background: #F28701 !important;
            color: #0A224F !important;
            font-weight: 600;
        }
    ''')


def _render_logo() -> None:
    """Show the shared logo using a path independent of the launch directory."""
    from nicegui import ui

    logo_path = Path(__file__).resolve().parents[2] / 'docs' / 'logo.png'
    ui.image(logo_path).props('fit=contain alt="Modelify logo"').classes('w-64 max-w-full')


class HomeUi:
    """Registry overview linking to the available YAML calculation forms."""

    def __init__(self, registry: FormulaRegistry | None = None,
                 layout_dir: str | Path | None = None):
        self.registry = registry or FormulaRegistry()
        self.layout_dir = Path(layout_dir) if layout_dir is not None else Path(__file__).parent / 'ui'
        self._routes: dict[str, str] = {}

    def register(self, path: str = '/') -> None:
        """Register a route; invoke before ui.run()."""
        from nicegui import ui

        for layout_path in sorted(self.layout_dir.glob('*.yaml')):
            page = FormulaUI(layout_path, registry=self.registry)
            formula_set = page.formula_set
            if formula_set.id not in self._routes:
                route = f'{path.rstrip("/")}/{formula_set.id}'

                def make_renderer(form):
                    def render_formula():
                        ui.link('Zurück zur Übersicht', path)
                        form.render()
                    return render_formula

                ui.page(route)(make_renderer(page))
                self._routes[formula_set.id] = route
        ui.page(path)(self.render)

    def render(self) -> None:
        """Build fresh widgets in the current NiceGUI client context."""
        from nicegui import ui

        _apply_theme()
        _render_logo()
        ui.label('Formelmodelle').classes('text-2xl font-bold')
        formula_sets = list(self.registry.formula_sets().values())
        count = ui.label(f'{len(formula_sets)} Modelle in der Formula Registry')
        cards = []

        def filter_cards(event):
            query = (event.value or '').strip().casefold()
            visible_count = 0
            for card, searchable_text in cards:
                visible = query in searchable_text
                card.set_visibility(visible)
                visible_count += visible
            count.set_text(f'{visible_count} von {len(formula_sets)} Modellen')
            empty.set_visibility(visible_count == 0)

        ui.input('Formelmodelle suchen',
                 placeholder='Titel, Beschreibung, Kategorie oder Tag',
                 on_change=filter_cards).props('outlined clearable').classes('w-full')
        empty = ui.label('Keine Formelmodelle gefunden.').classes('formula-muted')
        empty.set_visibility(not formula_sets)
        with ui.grid(columns=4).classes('w-full gap-4 items-stretch'):
            for formula_set in formula_sets:
                searchable_text = ' '.join([
                    formula_set.name or '',
                    formula_set.description_de or '',
                    formula_set.description_en or '',
                    *formula_set.categories,
                    *(formula_set.tags or []),
                ]).casefold()
                with ui.card().classes('w-full min-w-0 h-full') as card:
                    cards.append((card, searchable_text))
                    if formula_set.id in self._routes:
                        ui.link('Berechnung öffnen', self._routes[formula_set.id])
                    image_path = self.layout_dir / f'{formula_set.id}.png'
                    if image_path.is_file():
                        image = ui.image(image_path).props('fit=contain').classes('w-full h-30 rounded')
                        image.props['alt'] = formula_set.name or formula_set.id
                    ui.label(formula_set.name).classes('text-lg font-bold')
                    if formula_set.description_de:
                        ui.label(formula_set.description_de)
                    ui.label(' / '.join(formula_set.categories)).classes('formula-muted')
                    if formula_set.tags:
                        with ui.row().classes('gap-1 flex-wrap'):
                            for tag in formula_set.tags:
                                ui.badge(tag, color=None).classes('text-xs formula-tag')
                    if formula_set.id not in self._routes:
                        ui.label('Für dieses Modell ist noch kein Formular vorhanden.').classes('formula-muted')

class FormulaUI:
    """Load a layout, validate symbol references and render independent tabs.

    ``render()`` embeds the form in an existing NiceGUI page; ``register(path)``
    creates a standalone route. NiceGUI is only imported when rendering.
    """

    def __init__(self, yaml_path: str | Path, registry: FormulaRegistry | None = None):
        with Path(yaml_path).open(encoding='utf-8') as stream:
            layout = yaml.safe_load(stream)
        if isinstance(layout, dict) and 'formula_set_id' not in layout:
            ids = layout.get('formula_set_ids')
            if isinstance(ids, list) and len(ids) == 1:
                layout['formula_set_id'] = ids[0]
        if not isinstance(layout, dict) or not isinstance(layout.get('formula_set_id'), str):
            raise ValueError('The layout requires a formula_set_id.')
        self.formula_set = (registry or FormulaRegistry()).formula(layout['formula_set_id'])
        self.tabs = layout.get('tabs')
        if not isinstance(self.tabs, list) or not self.tabs:
            raise ValueError('The layout requires a non-empty tabs list.')
        names = set()
        for tab in self.tabs:
            if not isinstance(tab, dict) or not isinstance(tab.get('name'), str) or not tab['name'].strip():
                raise ValueError('Each tab requires a non-empty name.')
            if tab['name'] in names:
                raise ValueError(f"Duplicate tab name: {tab['name']}")
            names.add(tab['name'])
            for role in ('inputs', 'outputs'):
                symbols = tab.get(role)
                if not isinstance(symbols, list) or not symbols or not all(isinstance(s, str) for s in symbols):
                    raise ValueError(f"{tab['name']}: {role} must be a non-empty list of symbols.")
                if len(set(symbols)) != len(symbols):
                    raise ValueError(f"{tab['name']}: duplicate {role}.")
                unknown = set(symbols) - self.formula_set.symbols.keys()
                if unknown:
                    raise ValueError(f"{tab['name']}: unknown symbols: {', '.join(sorted(unknown))}")
            if set(tab['inputs']) & set(tab['outputs']):
                raise ValueError(f"{tab['name']}: a symbol cannot be both input and output.")

    def solve_tab(self, index: int, values: Mapping[str, float]) -> dict:
        """Validate and submit every input of one tab to FormulaEngine.solve."""
        tab = self.tabs[index]
        if set(values) != set(tab['inputs']):
            raise ValueError('Provide exactly the inputs declared for this tab.')
        inputs = {}
        for symbol in tab['inputs']:
            meta = self.formula_set.symbols[symbol]
            raw = values[symbol]
            try:
                value = float(raw)
            except (TypeError, ValueError):
                raise ValueError(f'{meta.label_de or symbol}: enter a number.') from None
            if isinstance(raw, bool) or not math.isfinite(value):
                raise ValueError(f'{meta.label_de or symbol}: enter a finite number.')
            if meta.options and value not in [option.value for option in meta.options]:
                raise ValueError(f'{meta.label_de or symbol}: select a listed option.')
            inputs[symbol] = SymbolInput(value=value, unit=meta.unit)
        targets = {symbol: self.formula_set.symbols[symbol].unit for symbol in tab['outputs']}
        result = FormulaEngine.solve(self.formula_set, inputs, targets)
        if not result or any(symbol not in result for symbol in targets):
            raise ValueError('No complete solution. Check the inputs and the formula model.')
        for symbol in targets:
            if not math.isfinite(float(result[symbol]['value'])):
                raise ValueError(f'{symbol}: the calculation returned no finite result.')
        return result

    def register(self, path: str = '/') -> None:
        """Register a route; invoke before ui.run()."""
        from nicegui import ui

        ui.page(path)(self.render)

    def render(self) -> None:
        """Build fresh widgets in the current NiceGUI client context."""
        from nicegui import ui

        _apply_theme()
        _render_logo()
        ui.label(self.formula_set.name).classes('text-2xl font-bold')
        if self.formula_set.description_de:
            ui.label(self.formula_set.description_de)
        image_path = Path(__file__).resolve().parent / 'ui' / f'{self.formula_set.id}.png'
        if image_path.is_file():
            image = ui.image(image_path).props('fit=contain').classes('rounded').style('width: 100px; height: 100px')
            image.props['alt'] = self.formula_set.name or self.formula_set.id
        with ui.tabs().classes('w-full') as tabs:
            for index, tab in enumerate(self.tabs):
                ui.tab(str(index), label=tab['name'])
        with ui.tab_panels(tabs, value='0').classes('w-full'):
            for index, tab in enumerate(self.tabs):
                with ui.tab_panel(str(index)):
                    self._render_tab(index, tab)

    def _render_tab(self, index: int, tab: dict) -> None:
        from nicegui import ui

        inputs, outputs = {}, {}
        if tab.get('description_de'):
            ui.label(tab['description_de'])
        with ui.row().classes('w-full items-start'):
            for role, fields in (('inputs', inputs), ('outputs', outputs)):
                with ui.column().classes('flex-1 min-w-64'):
                    ui.label('Eingaben' if role == 'inputs' else 'Ergebnisse').classes('text-lg font-bold')
                    for symbol in tab[role]:
                        meta = self.formula_set.symbols[symbol]
                        label = f'{meta.label_de or symbol} [{meta.unit}]'
                        if role == 'inputs' and meta.options:
                            widget = ui.select({o.value: o.name for o in meta.options}, label=label)
                        else:
                            widget = ui.number(label=label, value=None)
                        widget.classes('w-full')
                        if meta.description_de:
                            widget.tooltip(meta.description_de)
                        if role == 'outputs':
                            widget.props('readonly')
                        fields[symbol] = widget
        error = ui.label('').classes('text-negative').props('role=alert')

        def invalidate():
            for widget in outputs.values():
                widget.set_value(None)
            error.set_text('')

        for widget in inputs.values():
            widget.on_value_change(invalidate)

        async def calculate():
            invalidate()
            button.disable()
            for widget in inputs.values():
                widget.disable()
            try:
                values = {symbol: widget.value for symbol, widget in inputs.items()}
                result = await asyncio.to_thread(self.solve_tab, index, values)
                for symbol, widget in outputs.items():
                    widget.set_value(result[symbol]['value'])
            except Exception as exc:
                error.set_text(f'Berechnung fehlgeschlagen: {exc}')
            finally:
                button.enable()
                for widget in inputs.values():
                    widget.enable()

        button = ui.button('Berechnen', on_click=calculate).classes('formula-action')

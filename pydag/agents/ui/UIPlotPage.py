from dataclasses import dataclass, field
from typing import Any

import numpy as np
import plotly.graph_objects as go
from nicegui import ui

from loguru import logger

from .UIElements import UIComponent, UIPage


PLOT_TYPES = {
    "line": "Line (2D)",
    "scatter": "Scatter (2D)",
    "line3d": "Line (3D)",
    "scatter3d": "Scatter (3D)",
    "surface": "Surface (3D)",
    "mesh3d": "Mesh (3D)",
}


@dataclass
class _AxisSelection:
    buffer_id: str | None = None
    key: str | None = None
    label_mode: str = "key"


@dataclass
class _PlotTrace:
    x: _AxisSelection = field(default_factory=_AxisSelection)
    y: _AxisSelection = field(default_factory=_AxisSelection)
    z: _AxisSelection = field(default_factory=_AxisSelection)


@dataclass
class _PlotDefinition:
    title: str = "Plot"
    plot_type: str = "line"
    traces: list[_PlotTrace] = field(default_factory=lambda: [_PlotTrace()])
    surface_rows: int = 10
    surface_columns: int = 10


class _AxisSelector:
    def __init__(
        self,
        page: "UIPlotPage",
        panel: "_PlotEditor",
        axis: _AxisSelection,
        label: str,
    ):
        self._page = page
        self._panel = panel
        self._axis = axis
        self._keys: tuple[str, ...] = ()
        buffers = page.get_agent().buffer_store
        buffer_options = {buffer_id: buffer_id for buffer_id in buffers}
        if axis.buffer_id not in buffers:
            axis.buffer_id = next(iter(buffers), None)

        self._buffer_select = ui.select(
            buffer_options,
            value=axis.buffer_id,
            label=f"{label} buffer",
        ).props("dark").classes("w-full")
        self._key_select = ui.select(
            [],
            value=None,
            label=f"{label} key",
        ).props("dark").classes("w-full")
        self._label_select = ui.select(
            {"key": "Key name", "unit": "Buffer unit"},
            value=axis.label_mode,
            label=f"{label} label",
        ).props("dark").classes("w-full")

        self._buffer_select.on_value_change(self._on_buffer_change)
        self._key_select.on_value_change(self._on_key_change)
        self._label_select.on_value_change(self._on_label_change)
        self.sync_options()

    def _on_buffer_change(self, event):
        self._axis.buffer_id = event.value
        self._axis.key = None
        self.sync_options()
        self._panel.update()

    def _on_key_change(self, event):
        self._axis.key = event.value
        self._panel.update()

    def _on_label_change(self, event):
        self._axis.label_mode = event.value
        self._panel.update()

    def sync_options(self):
        buffer = self._page.get_agent().buffer_store.get(self._axis.buffer_id)
        keys = tuple(buffer.data(n=1, persistent=True).keys()) if buffer else ()
        if keys != self._keys:
            self._keys = keys
            self._key_select.set_options(list(keys))
        if self._axis.key not in keys:
            self._axis.key = keys[0] if keys else None
        if self._key_select.value != self._axis.key:
            self._key_select.set_value(self._axis.key)

    def label(self) -> str:
        buffer = self._page.get_agent().buffer_store.get(self._axis.buffer_id)
        key = self._axis.key
        if buffer is None or key is None:
            return ""
        if self._axis.label_mode == "unit":
            unit = buffer.unit
            if isinstance(unit, dict):
                unit = unit.get(key)
            elif isinstance(unit, (list, tuple)):
                keys = list(buffer.data(n=1, persistent=True).keys())
                unit = unit[keys.index(key)] if key in keys and keys.index(key) < len(unit) else None
            if unit is not None and str(unit).strip():
                return str(unit)
        return str(key)

class _PlotEditor(UIComponent):
    def __init__(self, page: "UIPlotPage", definition: _PlotDefinition):
        super().__init__(page)
        self._page = page
        self._definition = definition
        self._axis_selectors: list[_AxisSelector] = []
        self._data_cache: dict[str, dict[str, Any]] = {}
        self._last_error: str | None = None
        self._card = ui.card().classes("w-full")
        self.add_element(self._card)
        with self._card:
            with ui.dialog() as self._config_dialog:
                with ui.card().classes(
                    "w-[800px] max-w-[95vw] max-h-[90vh] overflow-y-auto"
                ):
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Plot settings").classes("font-bold text-lg")
                        ui.button(
                            icon="close",
                            on_click=self._config_dialog.close,
                        ).props("flat round dense").tooltip("Close settings")
                    self._title_input = ui.input(
                        "Plot title", value=definition.title
                    ).classes("w-full")
                    self._type_select = ui.select(
                        PLOT_TYPES,
                        value=definition.plot_type,
                        label="Plot type",
                    ).classes("w-full")
                    self._title_input.on_value_change(self._on_title_change)
                    self._type_select.on_value_change(self._on_type_change)

                    self._surface_dimensions = ui.row().classes("items-center")
                    with self._surface_dimensions:
                        self._rows_input = ui.number(
                            "Surface rows", value=definition.surface_rows, min=1, step=1
                        ).classes("w-40")
                        self._columns_input = ui.number(
                            "Surface columns",
                            value=definition.surface_columns,
                            min=1,
                            step=1,
                        ).classes("w-40")
                        self._rows_input.on_value_change(self._on_surface_dimensions_change)
                        self._columns_input.on_value_change(self._on_surface_dimensions_change)

                    self._traces_container = ui.column().classes("w-full")
                    ui.button(
                        "Add trace", icon="add", on_click=self.add_trace
                    ).props("outline")
                    with ui.row().classes("w-full justify-end"):
                        ui.button(
                            "Done", on_click=self._config_dialog.close
                        ).props("color=primary")

            with ui.row().classes("w-full items-center justify-end gap-1"):
                ui.button(
                    icon="more_vert",
                    on_click=self._config_dialog.open,
                ).props("flat round dense").tooltip("Plot settings")
                ui.button(
                    icon="close",
                    on_click=lambda: page.remove_plot(definition),
                ).props("flat round dense color=negative").tooltip("Delete plot")

            self._status = ui.label().classes("text-negative")
            self._figure = go.Figure()
            self._plot = ui.plotly(self._figure).classes("w-full")
            self._render_traces()
            self._update_surface_controls()
            self.update()

    def _on_title_change(self, event):
        self._definition.title = event.value or "Plot"
        self.update()

    def _on_type_change(self, event):
        self._definition.plot_type = event.value
        self._render_traces()
        self._update_surface_controls()
        self.update()

    def _on_surface_dimensions_change(self, _event):
        self._definition.surface_rows = int(self._rows_input.value or 1)
        self._definition.surface_columns = int(self._columns_input.value or 1)
        self.update()

    def _update_surface_controls(self):
        self._surface_dimensions.set_visibility(
            self._definition.plot_type == "surface"
        )

    def _render_traces(self):
        self._traces_container.clear()
        self._axis_selectors.clear()
        is_3d = self._definition.plot_type in {
            "line3d", "scatter3d", "surface", "mesh3d"
        }
        with self._traces_container:
            for index, trace in enumerate(self._definition.traces):
                with ui.expansion(f"Trace {index + 1}").classes(
                    "w-full bg-gray-800 text-white"
                ):
                    with ui.row().classes("w-full items-center"):
                        if len(self._definition.traces) > 1:
                            ui.button(
                                "Remove",
                                icon="delete",
                                on_click=lambda selected=trace: self.remove_trace(selected),
                            ).props("flat dense")
                    with ui.grid(columns=3).classes("w-full gap-3"):
                        for axis_name in (("X", trace.x), ("Y", trace.y), ("Z", trace.z)):
                            if axis_name[0] == "Z" and not is_3d:
                                continue
                            selector = _AxisSelector(
                                self._page, self, axis_name[1], axis_name[0]
                            )
                            self._axis_selectors.append(selector)

    def add_trace(self):
        self._definition.traces.append(_PlotTrace())
        self._render_traces()
        self.update()

    def remove_trace(self, trace: _PlotTrace):
        self._definition.traces.remove(trace)
        self._render_traces()
        self.update()

    def update(self):
        for selector in self._axis_selectors:
            selector.sync_options()
        self._data_cache.clear()
        try:
            figure = self._build_figure()
        except ValueError as exc:
            error = str(exc)
            self._status.text = error
            if error != self._last_error:
                logger.warning("Unable to render plot '{}': {}", self._definition.title, error)
                self._last_error = error
            figure = go.Figure(layout={"title": self._definition.title})
        else:
            self._last_error = None
            self._status.text = ""
        self._plot.figure = figure
        self._plot.update()

    def _build_figure(self) -> go.Figure:
        definition = self._definition
        plot_type = definition.plot_type
        is_3d = plot_type in {"line3d", "scatter3d", "surface", "mesh3d"}
        figure = go.Figure()
        figure.update_layout(
            title=definition.title,
            uirevision="constant",
            margin={"l": 60, "r": 60, "t": 50, "b": 50},
        )
        y_axis_labels: list[str] = []
        x_axis_label = "Index"
        scene_labels: dict[str, str] = {}

        for trace in definition.traces:
            x = self._axis_value(trace.x)
            y = self._axis_value(trace.y)
            z = self._axis_value(trace.z) if is_3d else None
            if y is None or (is_3d and (x is None or z is None)):
                continue
            x_values, x_label = x if x is not None else (list(range(len(y[0]))), "Index")
            y_values, y_label = y
            if len(x_values) != len(y_values) and not is_3d:
                raise ValueError("X and Y selections must contain the same number of samples")

            if not is_3d:
                if not y_axis_labels:
                    x_axis_label = x_label
                y_axis_labels.append(y_label)
                axis_number = len(y_axis_labels)
                axis_id = "y" if axis_number == 1 else f"y{axis_number}"
                mode = "lines" if plot_type == "line" else "markers"
                figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode=mode,
                        name=y_label,
                        yaxis=axis_id,
                    )
                )
            elif plot_type == "surface":
                z_values, z_label = z
                rows = definition.surface_rows
                columns = definition.surface_columns
                z_array = np.asarray(z_values)
                if z_array.size != rows * columns:
                    raise ValueError(
                        f"Surface Z data has {z_array.size} values; "
                        f"expected {rows * columns} for {rows} rows by {columns} columns"
                    )
                if len(x_values) != columns or len(y_values) != rows:
                    raise ValueError(
                        "Surface X and Y selections must match the configured column and row counts"
                    )
                figure.add_trace(
                    go.Surface(
                        x=x_values,
                        y=y_values,
                        z=z_array.reshape(rows, columns).tolist(),
                        name=z_label,
                    )
                )
                if not scene_labels:
                    scene_labels = {
                        "xaxis_title": x_label,
                        "yaxis_title": y_label,
                        "zaxis_title": z_label,
                    }
            else:
                z_values, z_label = z
                if len(x_values) != len(y_values) or len(x_values) != len(z_values):
                    raise ValueError("X, Y, and Z selections must contain the same number of samples")
                if plot_type == "mesh3d":
                    figure.add_trace(
                        go.Mesh3d(x=x_values, y=y_values, z=z_values, name=z_label)
                    )
                else:
                    mode = "lines" if plot_type == "line3d" else "markers"
                    figure.add_trace(
                        go.Scatter3d(
                            x=x_values,
                            y=y_values,
                            z=z_values,
                            mode=mode,
                            name=z_label,
                        )
                    )
                if not scene_labels:
                    scene_labels = {
                        "xaxis_title": x_label,
                        "yaxis_title": y_label,
                        "zaxis_title": z_label,
                    }

        if not is_3d:
            figure.update_layout(xaxis={"title": x_axis_label})
            for index, label in enumerate(y_axis_labels, start=1):
                key = "yaxis" if index == 1 else f"yaxis{index}"
                if index == 1:
                    figure.update_layout(**{key: {"title": label}})
                else:
                    is_right = index % 2 == 0
                    distance = ((index + 1) // 2) * 0.06
                    figure.update_layout(
                        **{
                            key: {
                                "title": label,
                                "overlaying": "y",
                                "side": "right" if is_right else "left",
                                "anchor": "free",
                                "position": 1 - distance if is_right else distance,
                            }
                        }
                    )
        else:
            figure.update_layout(scene=scene_labels)
        return figure

    def _axis_value(self, axis: _AxisSelection) -> tuple[list[Any], str] | None:
        buffer = self._page.get_agent().buffer_store.get(axis.buffer_id)
        if buffer is None or axis.key is None:
            return None
        if buffer.id not in self._data_cache:
            self._data_cache[buffer.id] = buffer.data(
                n=0,
                persistent=True,
            )
        data = self._data_cache[buffer.id]
        values = data.get(axis.key)
        if values is None:
            return None
        array = np.asarray(values)
        if array.ndim != 1:
            raise ValueError(
                f"Buffer '{buffer.id}' key '{axis.key}' must contain one-dimensional data"
            )
        if array.size > self._page.samples:
            array = array[-self._page.samples :]
        selector = next(
            (
                item
                for item in self._axis_selectors
                if item._axis is axis
            ),
            None,
        )
        label = selector.label() if selector else axis.key
        return array.tolist(), label


@dataclass
class UIPlotPage(UIPage):
    """Interactive Plotly plot composer for data in an Agent's buffers."""

    path: str = field(default="/plots")
    columns: int = field(default=2, metadata={"description": "number of plot columns (1 to 3)"})
    samples: int = field(default=1000, metadata={"description": "maximum recent samples to display per buffer"})

    def __post_init__(self):
        super().__post_init__()
        if not 1 <= self.columns <= 3:
            raise ValueError("columns must be between 1 and 3")
        if self.samples < 1:
            raise ValueError("samples must be greater than zero")
        self._plot_definitions = [_PlotDefinition()]
        self._plot_grid = None

    def _render(self):
        self.create_header("Plot Composer")
        with ui.row().classes("w-full items-center"):
            self._columns_select = ui.select(
                {1: "1 column", 2: "2 columns", 3: "3 columns"},
                value=min(max(self.columns, 1), 3),
                label="Columns",
            ).classes("w-48")
            self._columns_select.on_value_change(self._on_columns_change)
            ui.button("Add plot", icon="add", on_click=self.add_plot)
        self._plot_grid = ui.grid(columns=self.columns).classes("w-full gap-4")
        self._render_plots()

    def _on_columns_change(self, event):
        self.columns = int(event.value)
        self._render_plots()

    def add_plot(self):
        self._plot_definitions.append(
            _PlotDefinition(title=f"Plot {len(self._plot_definitions) + 1}")
        )
        self._render_plots()

    def remove_plot(self, definition: _PlotDefinition):
        self._plot_definitions.remove(definition)
        self._render_plots()

    def _render_plots(self):
        if self._plot_grid is None:
            return
        self._ui_components.clear()
        self._plot_grid.clear()
        self._plot_grid.style(
            f"grid-template-columns: repeat({self.columns}, minmax(0, 1fr))"
        )
        with self._plot_grid:
            for definition in self._plot_definitions:
                self.add_ui_component(_PlotEditor(self, definition))

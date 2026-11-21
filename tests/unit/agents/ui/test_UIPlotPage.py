from types import SimpleNamespace

import pytest

from pydag.agents.ui.UIPlotPage import (
    _AxisSelection,
    _AxisSelector,
    _PlotDefinition,
    _PlotEditor,
    _PlotTrace,
    UIPlotPage,
)


class _Buffer:
    def __init__(self, values, unit=None):
        self.id = "buffer"
        self.unit = unit
        self._values = values

    def data(self, n=0, persistent=True):
        return {
            key: values[:n] if n else values
            for key, values in self._values.items()
        }

    def push(self, data):
        for key, values in data.items():
            self._values[key].extend(values)


def _editor(definition, values, samples=1000):
    buffer = _Buffer(values)
    page = SimpleNamespace(
        samples=samples,
        get_agent=lambda: SimpleNamespace(buffer_store={"buffer": buffer}),
    )
    editor = object.__new__(_PlotEditor)
    editor._definition = definition
    editor._page = page
    editor._axis_selectors = []
    editor._data_cache = {}
    return editor, page


def _axis(key):
    return _AxisSelection(buffer_id="buffer", key=key)


def test_2d_plot_supports_multiple_y_axes():
    definition = _PlotDefinition(
        plot_type="line",
        traces=[
            _PlotTrace(x=_axis("time"), y=_axis("temperature")),
            _PlotTrace(x=_axis("time"), y=_axis("pressure")),
        ],
    )
    editor, _ = _editor(
        definition,
        {
            "time": [0, 1, 2],
            "temperature": [20, 21, 22],
            "pressure": [1.0, 1.1, 1.2],
        },
    )

    figure = editor._build_figure()

    assert len(figure.data) == 2
    assert figure.data[1].yaxis == "y2"
    assert figure.layout.yaxis2.overlaying == "y"
    assert figure.layout.xaxis.title.text == "time"
    assert figure.layout.yaxis.title.text == "temperature"
    assert figure.layout.yaxis2.title.text == "pressure"


def test_plot_refresh_uses_latest_samples_after_buffer_changes():
    definition = _PlotDefinition(
        plot_type="line",
        traces=[
            _PlotTrace(x=_axis("time"), y=_axis("temperature")),
        ],
    )
    editor, page = _editor(
        definition,
        {"time": [0, 1, 2], "temperature": [20, 21, 22]},
        samples=3,
    )
    editor._status = SimpleNamespace(text="")
    editor._last_error = None
    editor._plot = SimpleNamespace(figure=None, update=lambda: None)

    editor.update()
    page.get_agent().buffer_store["buffer"].push(
        {"time": [3], "temperature": [23]}
    )
    editor.update()

    assert list(editor._plot.figure.data[0].x) == [1, 2, 3]
    assert list(editor._plot.figure.data[0].y) == [21, 22, 23]


@pytest.mark.parametrize(
    ("plot_type", "trace_type"),
    [
        ("line3d", "scatter3d"),
        ("scatter3d", "scatter3d"),
        ("mesh3d", "mesh3d"),
    ],
)
def test_3d_plot_types_use_three_selected_axes(plot_type, trace_type):
    definition = _PlotDefinition(
        plot_type=plot_type,
        traces=[_PlotTrace(x=_axis("x"), y=_axis("y"), z=_axis("z"))],
    )
    editor, _ = _editor(
        definition,
        {"x": [0, 1], "y": [2, 3], "z": [4, 5]},
    )

    figure = editor._build_figure()

    assert figure.data[0].type == trace_type
    assert figure.layout.scene.xaxis.title.text == "x"
    assert figure.layout.scene.yaxis.title.text == "y"
    assert figure.layout.scene.zaxis.title.text == "z"


def test_surface_plot_reshapes_z_values_to_configured_grid():
    definition = _PlotDefinition(
        plot_type="surface",
        traces=[_PlotTrace(x=_axis("x"), y=_axis("y"), z=_axis("z"))],
        surface_rows=2,
        surface_columns=3,
    )
    editor, _ = _editor(
        definition,
        {
            "x": [0, 1, 2],
            "y": [0, 1],
            "z": [0, 1, 2, 3, 4, 5],
        },
    )

    figure = editor._build_figure()

    assert figure.data[0].type == "surface"
    assert figure.data[0].z == ([0, 1, 2], [3, 4, 5])


def test_axis_label_can_use_unit_metadata():
    axis = _AxisSelection(buffer_id="buffer", key="temperature", label_mode="unit")
    page = SimpleNamespace(
        get_agent=lambda: SimpleNamespace(
            buffer_store={
                "buffer": _Buffer(
                    {"temperature": [20]},
                    unit={"temperature": "°C"},
                )
            }
        )
    )
    selector = object.__new__(_AxisSelector)
    selector._page = page
    selector._axis = axis

    assert selector.label() == "°C"


def test_surface_rejects_mismatched_grid_dimensions():
    definition = _PlotDefinition(
        plot_type="surface",
        traces=[_PlotTrace(x=_axis("x"), y=_axis("y"), z=_axis("z"))],
        surface_rows=2,
        surface_columns=2,
    )
    editor, _ = _editor(
        definition,
        {"x": [0, 1], "y": [0, 1], "z": [0, 1, 2]},
    )

    with pytest.raises(ValueError, match="expected 4"):
        editor._build_figure()


def test_plot_page_adds_and_deletes_plot_definitions():
    page = UIPlotPage()
    initial_plot = page._plot_definitions[0]

    page.add_plot()
    assert len(page._plot_definitions) == 2

    page.remove_plot(initial_plot)
    assert len(page._plot_definitions) == 1
    assert page._plot_definitions[0].title == "Plot 2"


@pytest.mark.parametrize("columns", [0, 4])
def test_plot_page_rejects_invalid_column_count(columns):
    with pytest.raises(ValueError, match="columns"):
        UIPlotPage(columns=columns)

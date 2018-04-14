from collections import namedtuple
from functools import wraps
from itertools import chain
from typing import Callable

import numpy as np

from Orange.data import Table, Domain, StringVariable, ContinuousVariable, \
    DiscreteVariable, TimeVariable
from Orange.widgets.tests.base import WidgetTest
from Orange.widgets.tests.utils import simulate
from orangecontrib.prototypes.widgets.owfeaturestatistics import \
    OWFeatureStatistics

VarDataPair = namedtuple('VarDataPair', ['variable', 'data'])


# Continuous variable variations
continuous_full = VarDataPair(
    ContinuousVariable('continuous_full'),
    np.array([0, 1, 2, 3, 4], dtype=float),
)
continuous_missing = VarDataPair(
    ContinuousVariable('continuous_missing'),
    np.array([0, 1, 2, np.nan, 4], dtype=float),
)
continuous_all_missing = VarDataPair(
    ContinuousVariable('continuous_all_missing'),
    np.array([np.nan] * 5, dtype=float),
)
continuous_same = VarDataPair(
    ContinuousVariable('continuous_same'),
    np.array([3] * 5, dtype=float),
)
continuous = [
    continuous_full, continuous_missing, continuous_all_missing,
    continuous_same
]

# Unordered discrete variable variations
rgb_full = VarDataPair(
    DiscreteVariable('rgb_full', values=['r', 'g', 'b']),
    np.array([0, 1, 1, 1, 2], dtype=float),
)
rgb_missing = VarDataPair(
    DiscreteVariable('rgb_missing', values=['r', 'g', 'b']),
    np.array([0, 1, 1, np.nan, 2], dtype=float),
)
rgb_all_missing = VarDataPair(
    DiscreteVariable('rgb_all_missing', values=['r', 'g', 'b']),
    np.array([np.nan] * 5, dtype=float),
)
rgb_bins_missing = VarDataPair(
    DiscreteVariable('rgb_bins_missing', values=['r', 'g', 'b']),
    np.array([np.nan, 1, 1, 1, np.nan], dtype=float),
)
rgb_same = VarDataPair(
    DiscreteVariable('rgb_same', values=['r', 'g', 'b']),
    np.array([2] * 5, dtype=float),
)
rgb = [
    rgb_full, rgb_missing, rgb_all_missing, rgb_bins_missing, rgb_same
]

# Ordered discrete variable variations
ints_full = VarDataPair(
    DiscreteVariable('ints_full', values=['2', '3', '4'], ordered=True),
    np.array([0, 1, 1, 1, 2], dtype=float),
)
ints_missing = VarDataPair(
    DiscreteVariable('ints_missing', values=['2', '3', '4'], ordered=True),
    np.array([0, 1, 1, np.nan, 2], dtype=float),
)
ints_all_missing = VarDataPair(
    DiscreteVariable('ints_all_missing', values=['2', '3', '4'], ordered=True),
    np.array([np.nan] * 5, dtype=float),
)
ints_bins_missing = VarDataPair(
    DiscreteVariable('ints_bins_missing', values=['2', '3', '4'], ordered=True),
    np.array([np.nan, 1, 1, 1, np.nan], dtype=float),
)
ints_same = VarDataPair(
    DiscreteVariable('ints_same', values=['2', '3', '4'], ordered=True),
    np.array([0] * 5, dtype=float),
)
ints = [
    ints_full, ints_missing, ints_all_missing, ints_bins_missing, ints_same
]

discrete = list(chain(rgb, ints))

# Time variable variations
time_full = VarDataPair(
    TimeVariable('time_full'),
    np.array([0, 1, 2, 3, 4], dtype=float),
)
time_missing = VarDataPair(
    TimeVariable('time_missing'),
    np.array([0, np.nan, 2, 3, 4], dtype=float),
)
time_all_missing = VarDataPair(
    TimeVariable('time_all_missing'),
    np.array([np.nan] * 5, dtype=float),
)
time_same = VarDataPair(
    TimeVariable('time_same'),
    np.array([4] * 5, dtype=float),
)
time = [
    time_full, time_missing, time_all_missing, time_same
]

# String variable variations
string_full = VarDataPair(
    StringVariable('string_full'),
    np.array(['a', 'b', 'c', 'd', 'e'], dtype=object),
)
string_missing = VarDataPair(
    StringVariable('string_missing'),
    np.array(['a', 'b', 'c', StringVariable.Unknown, 'e'], dtype=object),
)
string_all_missing = VarDataPair(
    StringVariable('string_all_missing'),
    np.array([StringVariable.Unknown] * 5, dtype=object),
)
string_same = VarDataPair(
    StringVariable('string_same'),
    np.array(['a'] * 5, dtype=object),
)
string = [
    string_full, string_missing, string_all_missing, string_same
]


def make_table(attributes, target=None, metas=None):
    """Build an instance of a table given various variables.

    Parameters
    ----------
    attributes : Iterable[Tuple[Variable, np.array]
    target : Optional[Iterable[Tuple[Variable, np.array]]
    metas : Optional[Iterable[Tuple[Variable, np.array]]

    Returns
    -------
    Table

    """
    attribute_vars, attribute_vals = list(zip(*attributes))
    attribute_vals = np.array(attribute_vals).T

    target_vars, target_vals = None, None
    if target is not None:
        target_vars, target_vals = list(zip(*target))
        target_vals = np.array(target_vals).T

    meta_vars, meta_vals = None, None
    if metas is not None:
        meta_vars, meta_vals = list(zip(*metas))
        meta_vals = np.array(meta_vals).T

    return Table.from_numpy(
        Domain(attribute_vars, class_vars=target_vars, metas=meta_vars),
        X=attribute_vals, Y=target_vals, metas=meta_vals,
    )


def table_dense_sparse(test_case):
    # type: (Callable) -> Callable
    """Run a single test case on both dense and sparse Orange tables."""

    @wraps(test_case)
    def _wrapper(self):
        test_case(self, lambda table: table.to_dense())
        test_case(self, lambda table: table.to_sparse())

    return _wrapper


class TestOWFeatureStatisticsTableTypes(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(
            OWFeatureStatistics, stored_settings={'auto_commit': False}
        )

    @table_dense_sparse
    def test_runs_on_iris(self, prepare_table):
        self.send_signal('Data', prepare_table(Table('iris')))

    def test_does_not_crash_on_data_removal(self):
        self.send_signal('Data', make_table(discrete))
        self.send_signal('Data', None)

    # Only discrete variables
    @table_dense_sparse
    def test_runs_on_discrete_with_no_target(self, prepare_table):
        data = make_table(discrete)
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_discrete_with_discrete_target(self, prepare_table):
        data = make_table(discrete, target=[ints_full])
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_discrete_with_continuous_target(self, prepare_table):
        data = make_table(discrete, target=[continuous_full])
        self.send_signal('Data', prepare_table(data))

    # Only continuous variables
    @table_dense_sparse
    def test_runs_on_continuous_with_no_target(self, prepare_table):
        data = make_table(continuous)
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_continuous_with_discrete_target(self, prepare_table):
        data = make_table(continuous, target=[ints_full])
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_continuous_with_continuous_target(self, prepare_table):
        data = make_table(continuous, target=[continuous_full])
        self.send_signal('Data', prepare_table(data))

    # Only time variables
    @table_dense_sparse
    def test_runs_on_time_with_no_target(self, prepare_table):
        data = make_table(time)
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_time_with_discrete_target(self, prepare_table):
        data = make_table(time, target=[ints_full])
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_on_time_with_continuous_target(self, prepare_table):
        data = make_table(time, target=[continuous_full])
        self.send_signal('Data', prepare_table(data))

    # With various metas
    @table_dense_sparse
    def test_runs_with_no_target_and_metas(self, prepare_table):
        data = make_table(chain(continuous, discrete, time), metas=[
            ints_missing,
            rgb_same,
            string_missing,
            string_all_missing,
            time_full,
        ])
        self.send_signal('Data', prepare_table(data))

    @table_dense_sparse
    def test_runs_with_target_and_metas(self, prepare_table):
        data = make_table(chain(continuous, discrete, time), target=[
            ints_same
        ], metas=[
            ints_missing,
            rgb_same,
            string_missing,
            string_all_missing,
            time_full,
        ])
        self.send_signal('Data', prepare_table(data))

    # Various other convoluted input tables
    @table_dense_sparse
    def test_runs_with_multiple_targets(self, prepare_table):
        data = make_table(chain(continuous, discrete, time), target=[
            continuous_full,
            rgb_full,
            ints_full,
        ], metas=[
            ints_missing,
            rgb_same,
            string_missing,
            string_all_missing,
            time_full,
        ])
        self.send_signal('Data', prepare_table(data))
        simulate.combobox_run_through_all(self.widget.cb_color_var)

    @table_dense_sparse
    def test_runs_with_missing_target_values(self, prepare_table):
        data = make_table(chain(continuous, discrete, time), target=[
            continuous_missing,
            rgb_missing,
            ints_missing,
        ], metas=[
            ints_missing,
            rgb_same,
            string_missing,
            string_all_missing,
            time_full,
        ])
        self.send_signal('Data', prepare_table(data))
        # TODO: This does not actually test the crash because the histogram
        # code only runs when visible
        simulate.combobox_run_through_all(self.widget.cb_color_var)

    @table_dense_sparse
    def test_runs_with_all_missing_target_values(self, prepare_table):
        data = make_table(chain(continuous, discrete, time), target=[
            continuous_all_missing,
            rgb_all_missing,
            ints_all_missing,
        ], metas=[
            ints_missing,
            rgb_same,
            string_missing,
            string_all_missing,
            time_full,
        ])
        self.send_signal('Data', prepare_table(data))
        # TODO: This does not actually test the crash because the histogram
        # code only runs when visible
        simulate.combobox_run_through_all(self.widget.cb_color_var)


class TestFeatureStatisticsOutputs(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(
            OWFeatureStatistics, stored_settings={'auto_commit': False}
        )
        self.data = make_table(
            [continuous_full, continuous_missing],
            target=[rgb_full, rgb_missing], metas=[ints_full, ints_missing]
        )
        self.send_signal('Data', self.data)

    def test_sends_single_attribute_table_to_output(self):
        # Check if selecting a single attribute row
        self.widget.table_view.selectRow(0)
        self.widget.unconditional_commit()

        desired_domain = Domain(attributes=[continuous_full.variable])
        output = self.get_output(self.widget.Outputs.reduced_data)
        self.assertEqual(output.domain, desired_domain)

    def test_sends_multiple_attribute_table_to_output(self):
        # Check if selecting a single attribute row
        self.widget.table_view.selectRow(0)
        self.widget.table_view.selectRow(1)
        self.widget.unconditional_commit()

        desired_domain = Domain(attributes=[
            continuous_full.variable, continuous_missing.variable,
        ])
        output = self.get_output(self.widget.Outputs.reduced_data)
        self.assertEqual(output.domain, desired_domain)

    def test_sends_single_class_var_table_to_output(self):
        self.widget.table_view.selectRow(2)
        self.widget.unconditional_commit()

        desired_domain = Domain(attributes=[], class_vars=[rgb_full.variable])
        output = self.get_output(self.widget.Outputs.reduced_data)
        self.assertEqual(output.domain, desired_domain)

    def test_sends_single_meta_table_to_output(self):
        self.widget.table_view.selectRow(4)
        self.widget.unconditional_commit()

        desired_domain = Domain(attributes=[], metas=[ints_full.variable])
        output = self.get_output(self.widget.Outputs.reduced_data)
        self.assertEqual(output.domain, desired_domain)

    def test_sends_multiple_var_types_table_to_output(self):
        self.widget.table_view.selectRow(0)
        self.widget.table_view.selectRow(2)
        self.widget.table_view.selectRow(4)
        self.widget.unconditional_commit()

        desired_domain = Domain(
            attributes=[continuous_full.variable],
            class_vars=[rgb_full.variable],
            metas=[ints_full.variable],
        )
        output = self.get_output(self.widget.Outputs.reduced_data)
        self.assertEqual(output.domain, desired_domain)

    def test_sends_all_samples_to_output(self):
        """All rows should be sent to output for selected column."""
        self.widget.table_view.selectRow(0)
        self.widget.table_view.selectRow(2)
        self.widget.unconditional_commit()

        selected_vars = Domain(
            attributes=[continuous_full.variable],
            class_vars=[rgb_full.variable],
        )

        output = self.get_output(self.widget.Outputs.reduced_data)
        np.testing.assert_equal(output.X, self.data[:, selected_vars].X)
        np.testing.assert_equal(output.Y, self.data[:, selected_vars].Y)

    def test_clearing_selection_sends_none_to_output(self):
        """Clearing all the selected rows should send `None` to output."""
        self.widget.table_view.selectRow(0)
        self.widget.unconditional_commit()
        self.assertIsNotNone(self.get_output(self.widget.Outputs.reduced_data))
        self.assertIsNotNone(self.get_output(self.widget.Outputs.statistics))

        self.widget.table_view.clearSelection()
        self.widget.unconditional_commit()
        self.assertIsNone(self.get_output(self.widget.Outputs.reduced_data))
        self.assertIsNone(self.get_output(self.widget.Outputs.statistics))


class TestFeatureStatisticsUI(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(
            OWFeatureStatistics, stored_settings={'auto_commit': False}
        )
        self.data1 = Table('iris')
        self.data2 = Table('zoo')

    def test_restores_previous_selection(self):
        """Widget should remember selection with domain context handler."""
        # Send data and select rows
        self.send_signal(self.widget.Inputs.data, self.data1)
        self.widget.table_view.selectRow(0)
        self.widget.table_view.selectRow(2)
        self.assertEqual(len(self.widget.selected_rows), 2)

        # Sending new data clears selection
        self.send_signal(self.widget.Inputs.data, self.data2)
        self.assertEqual(len(self.widget.selected_rows), 0)

        # Sending back the old data restores the selection
        self.send_signal(self.widget.Inputs.data, self.data1)
        self.assertEqual(len(self.widget.selected_rows), 2)


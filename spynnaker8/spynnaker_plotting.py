# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Plotting tools to be used together with
https://github.com/NeuralEnsemble/PyNN/blob/master/pyNN/utility/plotting.py
"""

from neo import SpikeTrain, Block, Segment, AnalogSignal
import numpy as np
from quantities import millisecond
try:
    from pyNN.utility.plotting import repeat
    import matplotlib.pyplot as plt
    _matplotlib_missing = False
except ImportError:
    _matplotlib_missing = True


def _handle_options(ax, options):
    """ Handles options that can not be passed to axes.plot

    Removes the ones it has handled

    axes.plot will throw an exception if it gets unwanted options

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param dict options: All options the plotter can be configured with
    """
    if "xticks" not in options or options.pop("xticks") is False:
        plt.setp(ax.get_xticklabels(), visible=False)
    if "xlabel" in options:
        ax.set_xlabel(options.pop("xlabel"))
    else:
        ax.set_xlabel("Time (ms)")
    if "yticks" not in options or options.pop("yticks") is False:
        plt.setp(ax.get_yticklabels(), visible=False)
    if "ylabel" in options:
        ax.set_ylabel(options.pop("ylabel"))
    else:
        ax.set_ylabel("Neuron index")
    if "ylim" in options:
        ax.set_ylim(options.pop("ylim"))
    if "xlim" in options:
        ax.set_xlim(options.pop("xlim"))


def _plot_spikes(ax, spike_times, neurons, label='', **options):
    """ Plots the spikes based on two lists

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param list(~neo.core.SpikeTrain) spike_times: List of Spiketimes
    :param neurons: List of Neuron Ids
    :param str label: Label for the graph
    :param options: plotting options
    """
    if len(neurons):
        max_index = max(neurons)
        min_index = min(neurons)
        ax.plot(spike_times, neurons, 'b.', **options)
        ax.set_ylim(-0.5 + min_index, max_index + 0.5)
    if label:
        plt.text(0.95, 0.95, label,
                 transform=ax.transAxes, ha='right', va='top',
                 bbox=dict(facecolor='white', alpha=1.0))


def plot_spiketrains(ax, spiketrains, label='', **options):
    """ Plot all spike trains in a Segment in a raster plot.

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param list(~neo.core.SpikeTrain) spiketrains: List of spiketimes
    :param str label: Label for the graph
    :param options: plotting options
    """
    ax.set_xlim(0, spiketrains[0].t_stop / millisecond)
    _handle_options(ax, options)
    neurons = np.concatenate(
        [np.repeat(x.annotations['source_index'], len(x))
         for x in spiketrains])
    spike_times = np.concatenate(spiketrains, axis=0)
    _plot_spikes(ax, spike_times, neurons, label=label, **options)


def plot_spikes_numpy(ax, spikes, label='', **options):
    """ Plot all spikes

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param ~numpy.ndarray spikes: spynakker7 format nparray of spikes
    :param str label: Label for the graph
    :param options: plotting options
    """
    _handle_options(ax, options)
    neurons = spikes[:, 0]
    spike_times = spikes[:, 1]
    _plot_spikes(ax, spike_times, neurons, label=label, **options)


def _heat_plot(ax, neurons, times, values, label='', **options):
    """ Plots three lists of neurons, times and values into a heatmap

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param neurons: List of neuron IDs
    :param times: List of times
    :param values: List of values to plot
    :param str label: Label for the graph
    :param options: plotting options
    """
    _handle_options(ax, options)
    info_array = np.empty((max(neurons)+1, max(times)+1))
    info_array[:] = np.nan
    info_array[neurons, times] = values
    heat_map = ax.imshow(info_array, cmap='hot', interpolation='none',
                         origin='lower', aspect='auto')
    ax.figure.colorbar(heat_map)
    if label:
        plt.text(0.95, 0.95, label,
                 transform=ax.transAxes, ha='right', va='top',
                 bbox=dict(facecolor='white', alpha=1.0))


def heat_plot_numpy(ax, data, label='', **options):
    """ Plots neurons, times and values into a heatmap

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param ~numpy.ndarray data: nparray of values in spynnaker7 format
    :param str label: Label for the graph
    :param options: plotting options
    """
    neurons = data[:, 0].astype(int)
    times = data[:, 1].astype(int)
    values = data[:, 2]
    _heat_plot(ax, neurons, times, values, label=label, **options)


def heat_plot_neo(ax, signal_array, label='', **options):
    """ Plots neurons, times and values into a heatmap

    :param ~matplotlib.axes.Axes ax: An Axes in a matplotlib figure
    :param ~neo.core.AnalogSignal signal_array: Neo Signal array Object
    :param str label: Label for the graph
    :param options: plotting options
    """
    if label is None:
        label = signal_array.name
    n_neurons = signal_array.shape[-1]
    xs = list(range(n_neurons))
    times = signal_array.times / signal_array.sampling_period
    times = np.rint(times.magnitude).astype(int)
    all_times = np.tile(times, n_neurons)
    neurons = np.repeat(xs, len(times))
    magnitude = signal_array.magnitude
    values = np.concatenate([magnitude[:, x] for x in xs])
    _heat_plot(ax, neurons, all_times, values, label=label, **options)


def plot_segment(axes, segment, label='', **options):
    """ Plots a segment into a plot of spikes or a heatmap

        If there is more than ode type of Data in the segment options must\
        include the name of the data to plot

    .. note::
        method signature defined by pynn plotting.\
        This allows mixing of this plotting tool and pynn's

    :param ~matplotlib.axes.Axes axes: An Axes in a matplotlib figure
    :param ~neo.core.Segment segment: Data for one run to plot
    :param str label: Label for the graph
    :param options: plotting options
    """
    analogsignals = segment.analogsignals
    if "name" in options:
        name = options.pop("name")
        if name == 'spikes':
            plot_spiketrains(axes, segment.spiketrains, label=label, **options)
        else:
            heat_plot_neo(
                axes, segment.filter(name=name)[0], label=label, **options)
    elif segment.spiketrains:
        if len(analogsignals) > 1:
            raise Exception("Block.segment[0] has spikes and "
                            "other data; please specify one to plot")
        plot_spiketrains(axes, segment.spiketrains, label=label, **options)
    elif len(analogsignals) == 1:
        heat_plot_neo(axes, analogsignals[0], label=label, **options)
    elif len(analogsignals) > 1:
        raise Exception("Block.segment[0] has {} types of data; "
                        "please specify one to plot using name="
                        "".format(len(analogsignals)))
    else:
        raise Exception("Block does not appear to hold any data")


class SpynnakerPanel(object):
    """ Represents a single panel in a multi-panel figure.

    Compatible with :py:class:`pyNN.utility.plotting.Frame` and\
        can be mixed with :py:class:`pyNN.utility.plotting.Panel`

    Unlike :py:class:`pyNN.utility.plotting.Panel`,\
        Spikes are plotted faster,\
        other data is plotted as a heatmap

    A panel is a Matplotlib Axes or Subplot instance. A data item may be an\
    :py:class:`~neo.core.AnalogSignal`, or a list of \
    :py:class:`~neo.core.SpikeTrain`\\ s. The Panel will\
    automatically choose an appropriate representation. Multiple data items\
    may be plotted in the same panel.

    Valid options are any valid Matplotlib formatting options that should be\
    applied to the Axes/Subplot, plus in addition:

        `data_labels`:
            a list of strings of the same length as the number of data items.
        `line_properties`:
            a list of dicts containing Matplotlib formatting options, of the\
            same length as the number of data items.

    Whole Neo Objects can be passed in as long as they\
        contain a single Segment/run\
        and only contain one type of data
    Whole Segments can be passed in only if they only contain one type of data
    """

    def __init__(self, *data, **options):
        """
        :param data: One or more data series to be plotted.
        :type data: list(~neo.core.SpikeTrain) or ~neo.core.AnalogSignal \
            or ~numpy.ndarray or ~neo.core.Block or ~neo.core.Segment
        :param options: Any additional information.
        """
        if _matplotlib_missing:
            raise Exception("No matplotlib module found")
        self.data = list(data)
        self.options = options
        self.data_labels = options.pop("data_labels", repeat(None))
        self.line_properties = options.pop("line_properties", repeat({}))

    def plot(self, axes):
        """ Plot the Panel's data in the provided Axes/Subplot instance.

        :param ~matplotlib.axes.Axes axes: An Axes in a matplotlib figure
        """
        for datum, label, properties in zip(self.data, self.data_labels,
                                            self.line_properties):
            properties.update(self.options)

            # Support lists length one
            # for example result of segments[0].filter(name='v')
            if isinstance(datum, list):
                if not datum:
                    raise Exception("Can't handle empty list")
                if len(datum) == 1 and not isinstance(datum[0], SpikeTrain):
                    datum = datum[0]

            if isinstance(datum, list):
                self.__plot_list(axes, datum, label, properties)
            # AnalogSignal is also a ndarray, but data format different!
            # We import them as a single name here
            elif isinstance(datum, AnalogSignal):
                heat_plot_neo(axes, datum, label=label, **properties)
            elif isinstance(datum, np.ndarray):
                self.__plot_array(axes, datum, label, properties)
            elif isinstance(datum, Block):
                self.__plot_block(axes, datum, label, properties)
            elif isinstance(datum, Segment):
                plot_segment(axes, datum, label=label, **properties)
            else:
                raise Exception("Can't handle type {}; consider using "
                                "pyNN.utility.plotting".format(type(datum)))

    @staticmethod
    def __plot_list(axes, datum, label, properties):
        if not isinstance(datum[0], SpikeTrain):
            raise Exception("Can't handle lists of type {}"
                            "".format(type(datum)))
        plot_spiketrains(axes, datum, label=label, **properties)

    @staticmethod
    def __plot_array(axes, datum, label, properties):
        if len(datum[0]) == 2:
            plot_spikes_numpy(axes, datum, label=label, **properties)
        elif len(datum[0]) == 3:
            heat_plot_numpy(axes, datum, label=label, **properties)
        else:
            raise Exception("Can't handle ndarray with {} columns".format(
                len(datum[0])))

    @staticmethod
    def __plot_block(axes, datum, label, properties):
        if "run" in properties:
            run = int(properties.pop("run"))
            if len(datum.segments) <= run:
                raise Exception("Block only has {} segments".format(
                    len(datum.segments)))
            segment = datum.segments[run]
        elif len(datum.segments) != 1:
            raise Exception(
                "Block has {} segments please specify one to plot using run="
                .format(len(datum.segments)))
        else:
            segment = datum.segments[0]
        plot_segment(axes, segment, label=label, **properties)

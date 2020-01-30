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
Synfirechain-like example
"""
import spynnaker8 as p
from p8_integration_tests.base_test_case import BaseTestCase


def read_spikefile(file_name, n_neurons):
    """
    helper method for reading in spike data
    :param file_name:
    :param n_neurons:
    :return:
    """
    spike_array = [[] for _ in range(n_neurons)]
    with open(file_name) as f_spike:
        for line in f_spike:
            cut_index = line.find(';')
            time_stamp = int(line[0:cut_index])
            neuron_list = line[cut_index+1:-1].split(',')
            for neuron in neuron_list:
                neuron_id = int(neuron)
                spike_array[neuron_id].append(time_stamp)
    return spike_array


def do_run():
    """
    test that tests the printing of v from a pre determined recording
    :return:
    """
    p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
    n_neurons = 128 * 128  # number of neurons in each population
    p.set_number_of_neurons_per_core(p.IF_cond_exp, 256)

    cell_params_lif = {'cm': 0.25,
                       'i_offset': 0.0,
                       'tau_m': 20.0,
                       'tau_refrac': 2.0,
                       'tau_syn_E': 5.0,
                       'tau_syn_I': 5.0,
                       'v_reset': -70.0,
                       'v_rest': -65.0,
                       'v_thresh': -50.0,
                       'e_rev_E': 0.,
                       'e_rev_I': -80.
                       }

    populations = list()
    projections = list()

    weight_to_spike = 0.035
    delay = 17

    spikes = read_spikefile('test.spikes', n_neurons)
    spike_array = {'spike_times': spikes}

    populations.append(p.Population(
        n_neurons, p.SpikeSourceArray, spike_array,
        label='inputSpikes_1'))
    populations.append(p.Population(
        n_neurons, p.IF_cond_exp, cell_params_lif, label='pop_1'))
    projections.append(p.Projection(
        populations[0], populations[1], p.OneToOneConnector(),
        synapse_type=p.StaticSynapse(weight=weight_to_spike, delay=delay)))
    populations[1].record("spikes")

    p.run(1000)

    spikes = populations[1].spinnaker_get_data('spikes')

    p.end()

    return spikes


def plot(spikes):
    if spikes is None:
        print("No spikes received")
        return
    import pylab  # deferred so unittest are not dependent on it
    print(spikes)
    pylab.figure()
    pylab.plot([i[1] for i in spikes],
               [i[0] for i in spikes], ".")
    pylab.xlabel('Time/ms')
    pylab.ylabel('spikes')
    pylab.title('spikes')
    pylab.show()


class TestReadingSpikeArrayDataAndBigSlices(BaseTestCase):
    """
    tests the printing of print v given a simulation
    """

    def test_script(self):
        """
        test that tests the printing of v from a pre determined recording
        :return:
        """
        self.assert_not_spin_three()
        spikes = do_run()
        self.assertLessEqual(8570, len(spikes))
        self.assertGreaterEqual(8600, len(spikes))


if __name__ == '__main__':
    spikes = do_run()
    print(len(spikes))
    plot(spikes)

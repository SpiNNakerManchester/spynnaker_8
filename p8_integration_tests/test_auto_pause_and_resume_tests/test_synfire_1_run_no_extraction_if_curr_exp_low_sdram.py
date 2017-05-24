"""
Synfirechain-like example
"""
from p8_integration_tests.base_test_case import BaseTestCase
from p8_integration_tests.scripts.synfire_run import TestRun
import spynnaker.plot_utils as plot_utils
import spynnaker.spike_checker as spike_checker

n_neurons = 200  # number of neurons in each population
runtime = 3000
neurons_per_core = n_neurons / 2
synfire_run = TestRun()


class TestGsyn(BaseTestCase):
    """
    tests the printing of get gsyn given a simulation
    """

    def test_get_gsyn(self):
        synfire_run.do_run(n_neurons, neurons_per_core=neurons_per_core,
                           run_times=[runtime])
        spikes = synfire_run.get_output_pop_spikes()

        self.assertEquals(158, len(spikes))
        spike_checker.synfire_spike_checker(spikes, n_neurons)


if __name__ == '__main__':
    synfire_run.do_run(n_neurons, neurons_per_core=neurons_per_core,
                       run_times=[runtime])
    gsyn = synfire_run.get_output_pop_gsyn()
    v = synfire_run.get_output_pop_voltage()
    spikes = synfire_run.get_output_pop_spikes()

    print len(spikes)
    plot_utils.plot_spikes(spikes)
    plot_utils.heat_plot(v)
    plot_utils.heat_plot(gsyn)

import unittest
import spynnaker8 as p
from p8_integration_tests.base_test_case import BaseTestCase


class TestMultiBoardSpikeOutput(BaseTestCase):

    counts = None

    @staticmethod
    def spike_receiver(label, time, neuron_ids):
        TestMultiBoardSpikeOutput.counts[label] += len(neuron_ids)

    def multi_board_spike_output(self):
        self.assert_not_spin_three()
        TestMultiBoardSpikeOutput.counts = dict()
        p.setup(1.0, n_chips_required=((48 * 2) + 1))
        machine = p.get_machine()

        labels = list()
        pops = list()
        for chip in machine.ethernet_connected_chips:
            # print("Adding population on {}, {}".format(chip.x, chip.y))
            label = "{}, {}".format(chip.x, chip.y)
            spike_cells = {"spike_times": [i for i in range(100)]}
            pop = p.Population(10, p.SpikeSourceArray(**spike_cells),
                               label=label)
            pop.add_placement_constraint(chip.x, chip.y)
            labels.append(label)
            pops.append(pop)
            TestMultiBoardSpikeOutput.counts[label] = 0

        live_output = p.external_devices.SpynnakerLiveSpikesConnection(
            receive_labels=labels, local_port=None)
        for label, pop in zip(labels, pops):
            p.external_devices.activate_live_output_for(
                pop, database_notify_port_num=live_output.local_port)
            live_output.add_receive_callback(
                label, TestMultiBoardSpikeOutput.spike_receiver)

        p.run(1000)
        p.end()

        for label in labels:
            # print("Received {} of 1000 spikes from {}".format(
            #     TestMultiBoardSpikeOutput.counts[label], label))
            self.assertEquals(TestMultiBoardSpikeOutput.counts[label], 1000)

    def test_multi_board_spike_output(self):
        self.runsafe(self.multi_board_spike_output)


if __name__ == '__main__':
    unittest.main()

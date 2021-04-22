import unittest, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import StatusGenerator

class TestStatusGenerator(unittest.TestCase):

    results_folder = f"{os.path.dirname(os.path.abspath(__file__))}/test_results_dir"

    def test_status_report_pass(self):
        _st_generator = StatusGenerator.StatusGenerator(
            [TestStatusGenerator.results_folder],
            passing_quality_gate=0,
            executed_quality_gate=0
        )
        _st_report = _st_generator.generate_status()
        self.assertEqual(_st_report, 0)


    def test_status_report_fail(self):
        _st_generator = StatusGenerator.StatusGenerator(
            [TestStatusGenerator.results_folder],
            passing_quality_gate=100,
            executed_quality_gate=100
        )
        _st_report = _st_generator.generate_status()
        self.assertEqual(_st_report, 1)
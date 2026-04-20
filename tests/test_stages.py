import unittest

from stages.concept_stage import concept_stage
from stages.compliance_stage import compliance_stage
from stages.output_stage import output_stage

class StageTests(unittest.TestCase):

    def test_concept_stage(self):
        ctx = {"input": "school design"}
        result = concept_stage(ctx)
        self.assertIn("Concept", result)

    def test_compliance_stage(self):
        ctx = {"input": "school design"}
        result = compliance_stage(ctx)
        self.assertIn("Checked", result)

    def test_output_stage(self):
        ctx = {"input": "school design"}
        result = output_stage(ctx)
        self.assertIn("Final", result)

if __name__ == "__main__":
    unittest.main()

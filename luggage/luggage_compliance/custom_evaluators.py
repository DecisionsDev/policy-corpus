import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
import numpy as np
import pandas as pd

from luggage import Luggage


def cargo_items_evaluator(data, results_transposed):
    def compare_luggage(true_lug, pred_lug):
        """Compare two Luggage objects based on various attributes."""
        score = 0
        if true_lug.storage == pred_lug.storage:
            score += 0.2

        # Weight
        score += max(0, 0.3 - abs(true_lug.weight - pred_lug.weight))

        if true_lug.dim == pred_lug.dim:
            score += 0.2
        if true_lug.excess == pred_lug.excess:
            score += 0.1
        if true_lug.special == pred_lug.special:
            score += 0.1
        if true_lug.compliance == pred_lug.compliance:
            score += 0.1
        return round(score, 6)  # Max score is 1

    def compare_luggage_lists(true_list, pred_list):
        """Compare two lists of Luggage objects."""
        if len(true_list) != len(pred_list):
            return 0.0  # Different lengths = complete mismatch

        similarities = [compare_luggage(t, p) for t, p in zip(true_list, pred_list)]
        return sum(similarities) / len(true_list) if true_list else 1  # Avoid division by zero

    y_true = data["cargo_items"]
    y_pred = results_transposed[2]

    luggage_matches = [compare_luggage_lists(t, p) for t, p in zip(y_true, y_pred)]

    accuracy = np.mean(luggage_matches)  # Average match score

    float_matches = [m for m in luggage_matches if isinstance(m, float)]
    precision = sum(float_matches) / len(float_matches) if float_matches else 1
    recall = sum(luggage_matches) / len(luggage_matches)  # Average confidence score

    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

    print(f"Cargo Items - Accuracy: {accuracy}, F1: {f1}, Recall: {recall}, Precision: {precision},"
          f"\nLuggage Matches Scores: {luggage_matches}")

    return {"accuracy": accuracy, "f1": f1, "recall": recall, "precision": precision}


class TestCargoItemsEvaluator(unittest.TestCase):

    def setUp(self):
        """Set up sample data for testing with fully defined Luggage objects."""
        self.data = pd.DataFrame({
            "cargo_items": [
                [Luggage(storage="carry-on", weight=10.0, excess=False, special=False, compliance=True,
                         dim={"height": 55.0, "width": 35.0, "depth": 20.0, "unit": "cm"})],
                [Luggage(storage="checked", weight=20.0, excess=True, special=False, compliance=False,
                         dim={"height": 75.0, "width": 50.0, "depth": 30.0, "unit": "cm"})],
                [],
                [Luggage(storage="special", weight=30.0, excess=False, special=True, compliance=True,
                         dim={"height": 90.0, "width": 60.0, "depth": 40.0, "unit": "cm"})]
            ]
        })

        self.results_transposed = [
            None, None,
            [
                [Luggage(storage="carry-on", weight=10.0, excess=False, special=False, compliance=True,
                         dim={"height": 55.0, "width": 35.0, "depth": 20.0, "unit": "cm"})],  # Perfect match
                [Luggage(storage="checked", weight=21.0, excess=True, special=False, compliance=False,
                         dim={"height": 75.0, "width": 50.0, "depth": 30.0, "unit": "cm"})],  # Slight weight diff
                [],  # Empty list (should be a perfect match)
                [Luggage(storage="special", weight=32.0, excess=False, special=True, compliance=True,
                         dim={"height": 90.0, "width": 60.0, "depth": 40.0, "unit": "cm"})]  # Slight weight diff
            ]
        ]

    def convert_to_dicts(self, data):
        """Convert Luggage objects to dictionaries for proper comparison."""
        return [[lug.to_dict() for lug in sublist] for sublist in data]

    def convert_to_luggage(self, data):
        """Convert dictionaries back to Luggage objects for evaluation."""
        return [[Luggage.from_dict(lug) for lug in sublist] for sublist in data]

    def test_perfect_match(self):
        """Test case where all predictions match exactly."""
        # Ensure results_transposed has exact matches
        self.results_transposed[2][1] = [Luggage(storage="checked", weight=20.0, excess=True, special=False, compliance=False,
                                                 dim={"height": 75.0, "width": 50.0, "depth": 30.0, "unit": "cm"})]
        self.results_transposed[2][3] = [Luggage(storage="special", weight=30.0, excess=False, special=True, compliance=True,
                                                 dim={"height": 90.0, "width": 60.0, "depth": 40.0, "unit": "cm"})]

        # Convert Luggage objects to dictionaries for passing to evaluator
        data_dicts = self.convert_to_dicts(self.data["cargo_items"])
        results_dicts = self.convert_to_dicts(self.results_transposed[2])

        # Convert back to Luggage inside the function
        metrics = cargo_items_evaluator({"cargo_items": self.convert_to_luggage(data_dicts)}, [None, None, self.convert_to_luggage(results_dicts)])

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["precision"], 1.0)

    def test_weight_difference(self):
        """Test case where there's a small weight difference in predictions."""
        data_dicts = self.convert_to_dicts(self.data["cargo_items"])
        results_dicts = self.convert_to_dicts(self.results_transposed[2])

        metrics = cargo_items_evaluator({"cargo_items": self.convert_to_luggage(data_dicts)}, [None, None, self.convert_to_luggage(results_dicts)])

        self.assertLess(metrics["accuracy"], 1.0)  # Slightly lower due to weight diff
        self.assertLess(metrics["f1"], 1.0)
        self.assertLess(metrics["recall"], 1.0)
        self.assertLess(metrics["precision"], 1.0)
        self.assertGreater(metrics["recall"], 0.84)  # Should still be fairly high

    def test_mismatch(self):
        """Test case where predictions mismatch true values, except for an empty one."""
        self.results_transposed[2] = [[], [], [], []]  # One correct predictions

        data_dicts = self.convert_to_dicts(self.data["cargo_items"])
        results_dicts = self.convert_to_dicts(self.results_transposed[2])

        metrics = cargo_items_evaluator({"cargo_items": self.convert_to_luggage(data_dicts)}, [None, None, self.convert_to_luggage(results_dicts)])

        self.assertEqual(metrics["accuracy"], 0.25)
        self.assertEqual(metrics["f1"], 0.0)
        self.assertEqual(metrics["recall"], 0.25)
        self.assertEqual(metrics["precision"], 0.0)

    def test_partial_match(self):
        """Test case where some predictions match and some do not."""
        self.results_transposed[2][0] = [Luggage(storage="carry-on", weight=11.0, excess=False, special=False, compliance=True,
                                                 dim={"height": 55.0, "width": 35.0, "depth": 20.0, "unit": "cm"})]
        self.results_transposed[2][1] = [Luggage(storage="checked", weight=19.5, excess=True, special=False, compliance=False,
                                                 dim={"height": 75.0, "width": 50.0, "depth": 30.0, "unit": "cm"})]

        data_dicts = self.convert_to_dicts(self.data["cargo_items"])
        results_dicts = self.convert_to_dicts(self.results_transposed[2])

        metrics = cargo_items_evaluator({"cargo_items": self.convert_to_luggage(data_dicts)}, [None, None, self.convert_to_luggage(results_dicts)])

        self.assertGreater(metrics["accuracy"], 0.5)
        self.assertLess(metrics["accuracy"], 1.0)
        self.assertGreater(metrics["f1"], 0.5)
        self.assertLess(metrics["f1"], 1.0)
        self.assertGreater(metrics["recall"], 0.5)
        self.assertLess(metrics["recall"], 1.0)
        self.assertGreater(metrics["precision"], 0.5)
        self.assertLess(metrics["precision"], 1.0)

    def test_empty_lists(self):
        """Test case with completely empty lists (should return perfect scores)."""
        data = pd.DataFrame({"cargo_items": [[]] * 5})
        results_transposed = [None, None, [[]] * 5]

        metrics = cargo_items_evaluator(data, results_transposed)

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["precision"], 1.0)


if __name__ == "__main__":
    unittest.main()


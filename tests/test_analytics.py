import unittest
import os
import sys
from typing import Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.query_engine import run_query
from data.database import get_db_session, Patient, LabResult, Diagnosis, Medication
from sqlalchemy import func

class TestAnalyticsWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = get_db_session()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _assert_analytics_result(self, query: str, expected_intent: str = "aggregation"):
        print(f"\n[TEST] Query: {query}")
        result = run_query(query)
        
        # 1. Basic Structure Check
        self.assertIn("result", result)
        self.assertIn("metadata", result)
        if "parsed_intent" in result:
             print(f"      Intent: {result['parsed_intent']['intents']} Filters: {result['parsed_intent']['filters']} Aggs: {result['parsed_intent']['aggregations']}")

        self.assertIn(expected_intent, result["metadata"]["intents"])
        
        # 2. Check for Errors
        if "error" in result:
            self.fail(f"Query failed with error: {result['error']}")
            
        return result

    def _get_metric(self, result_dict, prefix="count"):
        """Robustly extract a metric value (e.g. count_patients, count_age, etc)"""
        # If it's a list (group_by), this helper isn't for that
        if isinstance(result_dict, list):
            return result_dict
            
        # Try exact match first
        for k in [f"{prefix}_patients", f"{prefix}_age", f"{prefix}_patient_id"]:
            if k in result_dict: return result_dict[k]
            
        # Fallback: first key with the prefix
        for k in result_dict.keys():
            if k.startswith(prefix): return result_dict[k]
        
        raise KeyError(f"No metric with prefix '{prefix}' found in {result_dict}")

    def test_01_count_patients(self):
        """1. How many patients are in the database?"""
        res = self._assert_analytics_result("How many patients are in the database?")
        count = self._get_metric(res["result"]["aggregation"]["result"], "count")
        db_count = self.db.query(Patient).count()
        self.assertEqual(count, db_count)

    def test_02_average_age(self):
        """2. What is the average age of all patients?"""
        res = self._assert_analytics_result("What is the average age of all patients?")
        avg_age = self._get_metric(res["result"]["aggregation"]["result"], "avg")
        db_avg = self.db.query(func.avg(Patient.age)).scalar()
        self.assertAlmostEqual(avg_age, float(db_avg), places=1)

    def test_03_count_by_gender(self):
        """3. Give me a breakdown of patients by gender."""
        res = self._assert_analytics_result("Give me a breakdown of patients by gender.")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)
        self.assertTrue(len(agg_res) >= 2)

    def test_04_count_by_diagnosis(self):
        """4. How many patients have Heart Failure vs Angina?"""
        res = self._assert_analytics_result("How many patients have Heart Failure vs Angina?")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_05_average_age_by_outcome(self):
        """5. What is the average age of patients who were Discharged vs Deceased?"""
        res = self._assert_analytics_result("What is the average age of patients who were Discharged vs Deceased?")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_06_filter_aggregation(self):
        """6. How many female patients are over 70 years old?"""
        res = self._assert_analytics_result("How many female patients are over 70 years old?")
        count = self._get_metric(res["result"]["aggregation"]["result"], "count")
        # Match 'F' in database
        db_count = self.db.query(Patient).filter(Patient.gender == 'F', Patient.age > 70).count()
        self.assertEqual(count, db_count)

    def test_07_average_los(self):
        """7. What is the average length of stay for all patients?"""
        res = self._assert_analytics_result("What is the average length of stay for all patients?")
        agg_res = res["result"]["aggregation"]["result"]
        
        # Now that we support length_of_stay, we should check for the specific key
        los_val = self._get_metric(agg_res, "avg")
        self.assertGreater(los_val, 0)
        
        # Verify intent field is correct
        self.assertEqual(res["parsed_intent"]["aggregations"][0]["field"], "length_of_stay")

    def test_08_stemi_count(self):
        """8. How many STEMI patients are there?"""
        res = self._assert_analytics_result("How many STEMI patients are there?")
        count = self._get_metric(res["result"]["aggregation"]["result"], "count")
        # mi_type check should be exact to avoid matching NSTEMI
        db_count = self.db.query(Patient).filter(Patient.mi_type == 'STEMI').count()
        self.assertEqual(count, db_count)

    def test_09_diagnosis_outcome_breakdown(self):
        """9. Count patients with Heart Failure by their outcome."""
        res = self._assert_analytics_result("Count patients with Heart Failure by their outcome.")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_10_nationality_breakdown(self):
        """10. Break down the patient population by nationality."""
        res = self._assert_analytics_result("Break down the patient population by nationality.")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_11_bmi_category_count(self):
        """11. How many patients are in each BMI category?"""
        res = self._assert_analytics_result("How many patients are in each BMI category?")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_12_procedure_count(self):
        """12. How many patients underwent a procedure?"""
        res = self._assert_analytics_result("How many patients underwent a procedure?")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIn("result", res["result"]["aggregation"])

    def test_13_admission_trend(self):
        """13. How many patients were admitted in each year?"""
        res = self._assert_analytics_result("How many patients were admitted in each year?")
        agg_res = res["result"]["aggregation"]["result"]
        self.assertIsInstance(agg_res, list)

    def test_14_complex_filter_obese(self):
        """14. Count patients with Angina who are obese."""
        res = self._assert_analytics_result("Count patients with Angina who are obese.")
        count = self._get_metric(res["result"]["aggregation"]["result"], "count")
        db_count = self.db.query(Patient).filter(
            Patient.primary_diagnosis.ilike('%Angina%'),
            Patient.bmi_category.ilike('%Obese%')
        ).count()
        self.assertEqual(count, db_count)

    def test_15_lookup_p00001(self):
        """15. Get details for patient P00001."""
        res = self._assert_analytics_result("Get details for patient P00001.", expected_intent="lookup")
        lookup = res["result"]["lookup"]
        self.assertTrue(len(lookup) > 0)
        self.assertEqual(lookup[0]["patient_id"], "P00001")

if __name__ == "__main__":
    unittest.main()

"""
VYNTRIX Comprehensive Automated Test Suite
Validates all 12 Hackathon Track R5 core specifications.
"""

import unittest
import os
import io
import pandas as pd
from vyntrix.config import (
    CAT_SAFETY, CAT_HYGIENE, CAT_ALLERGEN, CAT_PRODUCT_QUALITY,
    CAT_STOCK, CAT_QUEUE, CAT_STAFF, CAT_OTHER,
    DEPARTMENT_MAPPING, SEV_HIGH, SEV_MEDIUM, SEV_LOW,
    MANDATORY_HIGH_CATEGORIES
)
from vyntrix.classifier import FeedbackClassifier
from vyntrix.text_cleaner import clean_text_for_nlp, process_feedback_dataframe
from vyntrix.trend_engine import TrendIntelligenceEngine
from vyntrix.report_generator import RegionalBriefGenerator
from vyntrix.data_manager import (
    validate_and_process_dataset,
    generate_sample_template_csv,
    load_demo_dataset
)


class TestVyntrixCore(unittest.TestCase):

    def setUp(self):
        self.classifier = FeedbackClassifier()
        self.trend_engine = TrendIntelligenceEngine(min_evidence_threshold=3)

    # 1. Application imports & modules start successfully
    def test_01_modules_initialization(self):
        self.assertIsNotNone(self.classifier)
        self.assertIsNotNone(self.trend_engine)
        self.assertTrue(len(DEPARTMENT_MAPPING) >= 8)

    # 2. Demonstration data loads cleanly and has valid structure
    def test_02_demo_data_loading(self):
        df = load_demo_dataset()
        self.assertFalse(df.empty, "Demo dataset should not be empty")
        self.assertGreaterEqual(len(df), 200, "Demo dataset should contain at least 200 records")
        expected_cols = ["feedback_id", "original_text", "store_id", "date", "category", "severity"]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing required column {col} in demo dataset")

    # 3. Filtering updates the relevant results accurately
    def test_03_filtering_functionality(self):
        df = load_demo_dataset()
        # Filter by store
        filtered_store = df[df["store_id"] == "STR-101"]
        self.assertGreater(len(filtered_store), 0)
        self.assertTrue((filtered_store["store_id"] == "STR-101").all())

        # Filter by severity
        filtered_sev = df[df["severity"] == SEV_HIGH]
        self.assertGreater(len(filtered_sev), 0)
        self.assertTrue((filtered_sev["severity"] == SEV_HIGH).all())

        # Multi-filter
        multi = df[(df["store_id"] == "STR-101") & (df["severity"] == SEV_HIGH)]
        self.assertTrue((multi["store_id"] == "STR-101").all())
        self.assertTrue((multi["severity"] == SEV_HIGH).all())

    # 4. Feedback analysis produces a complete, dynamic result for new input
    def test_04_feedback_analyzer_dynamic_output(self):
        test_input = "Cashier threw my change on the floor and was extremely rude and unhelpful!"
        res = self.classifier.classify_text(test_input)
        self.assertEqual(res["category"], CAT_STAFF)
        self.assertEqual(res["department"], "Customer Experience")
        self.assertIn(res["severity"], [SEV_HIGH, SEV_MEDIUM, SEV_LOW])
        self.assertIsInstance(res["escalation_required"], bool)
        self.assertGreater(len(res["explanation"]), 10)
        self.assertGreater(len(res["recommended_action"]), 10)

    # 5. Safety-related feedback ALWAYS receives High priority and escalation
    def test_05_safety_mandatory_high_and_escalation(self):
        safety_samples = [
            "Customer slipped on wet floor near produce, water puddle leaking from fridge ⚠️",
            "Broken glass shards scattered in aisle 4, child almost cut their foot",
            "Emergency fire exit is blocked by wooden pallets in back hallway hazard!",
            "Heavy box fell from overhead rack and hit customer on shoulder danger 🚨"
        ]
        for sample in safety_samples:
            res = self.classifier.classify_text(sample)
            self.assertEqual(res["category"], CAT_SAFETY, f"Failed category for: {sample}")
            self.assertEqual(res["severity"], SEV_HIGH, f"Safety must always be High: {sample}")
            self.assertTrue(res["escalation_required"], f"Safety must always escalate: {sample}")
            self.assertEqual(res["department"], "Store Safety Team")

    # 6. Hygiene-related feedback ALWAYS receives High priority and escalation
    def test_06_hygiene_mandatory_high_and_escalation(self):
        hygiene_samples = [
            "Saw a live rat crawling behind the bakery display case 🐀 disgusting",
            "Cockroach running across the salad bar counter today 🤢 health code violation",
            "Restroom was completely filthy with feces on toilet and no soap",
            "Rotten meat leaking foul odor fluid all over bottom shelf in aisle 2"
        ]
        for sample in hygiene_samples:
            res = self.classifier.classify_text(sample)
            self.assertEqual(res["category"], CAT_HYGIENE, f"Failed category for: {sample}")
            self.assertEqual(res["severity"], SEV_HIGH, f"Hygiene must always be High: {sample}")
            self.assertTrue(res["escalation_required"], f"Hygiene must always escalate: {sample}")
            self.assertEqual(res["department"], "Food Safety / Store Operations")

    # 7. Allergen-related feedback ALWAYS receives High priority and escalation
    def test_07_allergen_mandatory_high_and_escalation(self):
        allergen_samples = [
            "Bakery cookies contain undeclared peanuts, my son had severe allergic hives 🥜",
            "Cross contamination in gluten-free prep area, severe celiac reaction!",
            "Purchased almond milk labeled nut-free, child suffered anaphylactic shock!",
            "No allergen warning labels on bulk bin containing pecans and walnuts 🥜"
        ]
        for sample in allergen_samples:
            res = self.classifier.classify_text(sample)
            self.assertEqual(res["category"], CAT_ALLERGEN, f"Failed category for: {sample}")
            self.assertEqual(res["severity"], SEV_HIGH, f"Allergen must always be High: {sample}")
            self.assertTrue(res["escalation_required"], f"Allergen must always escalate: {sample}")
            self.assertEqual(res["department"], "Food Safety Team")

    # 8. Department ownership is assigned correctly across all categories
    def test_08_department_ownership_mappings(self):
        test_cases = [
            ("Out of stock on baby formula and 2% milk, empty shelves", CAT_STOCK, "Inventory Team"),
            ("Waited 45 minutes in line with only 1 cashier open on Saturday", CAT_QUEUE, "Store Operations"),
            ("Employee was rude, yelled at customer and threw receipt", CAT_STAFF, "Customer Experience"),
            ("Milk expired 4 days ago, smelled sour and curdled", CAT_PRODUCT_QUALITY, "Quality Team"),
            ("Spilled oil puddle in aisle 3 hazard ⚠️", CAT_SAFETY, "Store Safety Team"),
            ("Live roach spotted on deli prep counter 🪳", CAT_HYGIENE, "Food Safety / Store Operations"),
            ("Undeclared peanut allergy hazard in bakery 🥜", CAT_ALLERGEN, "Food Safety Team"),
            ("Random unrelated comment without keywords", CAT_OTHER, "Manual Review")
        ]
        for text, expected_cat, expected_dept in test_cases:
            res = self.classifier.classify_text(text)
            self.assertEqual(res["category"], expected_cat, f"Wrong category for '{text}': got {res['category']}")
            self.assertEqual(res["department"], expected_dept, f"Wrong dept for '{text}': got {res['department']}")

    # 9. Store trends handle insufficient historical data gracefully
    def test_09_store_trends_insufficient_history(self):
        # Store with only 1 week of data
        raw_data = [
            {"feedback_id": "T1", "original_text": "Queue was long", "store_id": "STR-NEW", "date": "2026-02-25", "category": CAT_QUEUE},
            {"feedback_id": "T2", "original_text": "Queue was long", "store_id": "STR-NEW", "date": "2026-02-26", "category": CAT_QUEUE},
            {"feedback_id": "T3", "original_text": "Out of milk", "store_id": "STR-NEW", "date": "2026-02-27", "category": CAT_STOCK},
            # Established store with 3 weeks
            {"feedback_id": "T4", "original_text": "Out of milk", "store_id": "STR-OLD", "date": "2026-01-10", "category": CAT_STOCK},
            {"feedback_id": "T5", "original_text": "Out of milk", "store_id": "STR-OLD", "date": "2026-01-18", "category": CAT_STOCK},
            {"feedback_id": "T6", "original_text": "Queue was long", "store_id": "STR-OLD", "date": "2026-02-25", "category": CAT_QUEUE},
            {"feedback_id": "T7", "original_id": "Queue was long", "store_id": "STR-OLD", "date": "2026-02-26", "category": CAT_QUEUE},
            {"feedback_id": "T8", "original_text": "Queue was long", "store_id": "STR-OLD", "date": "2026-02-27", "category": CAT_QUEUE}
        ]
        df = pd.DataFrame(raw_data)
        alerts = self.trend_engine.detect_emerging_issues(df)
        
        # Check that STR-NEW has INSUFFICIENT_BASELINE_DATA and is NOT falsely flagged as alert
        new_store_alerts = [a for a in alerts if a["store_id"] == "STR-NEW"]
        self.assertGreater(len(new_store_alerts), 0)
        self.assertEqual(new_store_alerts[0]["status"], "INSUFFICIENT_BASELINE_DATA")
        self.assertFalse(new_store_alerts[0]["is_alert"])
        self.assertIn("baseline week", new_store_alerts[0]["explanation"])

    # 10. CSV upload and validation work with alias mapping and error detection
    def test_10_csv_upload_and_validation(self):
        # CSV with alternative column headers
        csv_content = """comment,location,time,source
"Spilled oil on floor, slip hazard! ⚠️",STR-101,2026-02-10,Google
"Out of stock on eggs and bread",STR-102,2026-02-11,App
"""
        df_out, audit, msgs = validate_and_process_dataset(io.StringIO(csv_content), self.classifier)
        self.assertEqual(len(df_out), 2)
        self.assertIn("category", df_out.columns)
        self.assertIn("severity", df_out.columns)
        self.assertEqual(df_out.iloc[0]["category"], CAT_SAFETY)
        self.assertEqual(df_out.iloc[0]["store_id"], "STR-101")

        # Invalid CSV missing feedback text column
        invalid_csv = """date,store_code,count
2026-01-01,STR-101,10
"""
        df_inv, audit_inv, msgs_inv = validate_and_process_dataset(io.StringIO(invalid_csv))
        self.assertTrue(df_inv.empty)
        self.assertTrue(any("Missing feedback text column" in m for m in msgs_inv))

    # 11. Weekly reports and downloads work (Markdown & CSV)
    def test_11_weekly_regional_brief_generation(self):
        df = load_demo_dataset()
        alerts = self.trend_engine.detect_emerging_issues(df)
        
        # Markdown generation
        md_report = RegionalBriefGenerator.generate_markdown(df, alerts, region_title="Metro Test Region")
        self.assertIn("# VYNTRIX Voice-of-Store Weekly Regional Brief", md_report)
        self.assertIn("Executive Summary Metrics", md_report)
        self.assertIn("Top 5 Regional Issues Deep-Dive", md_report)
        self.assertIn("Prioritized Regional Action Plan", md_report)

        # CSV generation
        csv_report = RegionalBriefGenerator.generate_csv(df)
        self.assertIn("category,total_records", csv_report)
        self.assertIn("owning_department", csv_report)
        self.assertGreater(len(csv_report.splitlines()), 3)

    # 12. Empty or invalid input produces helpful messages without crashing
    def test_12_empty_and_invalid_input_handling(self):
        # Empty text
        res_empty = self.classifier.classify_text("")
        self.assertEqual(res_empty["category"], CAT_OTHER)
        self.assertEqual(res_empty["severity"], SEV_LOW)
        self.assertFalse(res_empty["escalation_required"])
        self.assertIn("No text provided", res_empty["explanation"])

        # None text
        res_none = self.classifier.classify_text(None)
        self.assertEqual(res_none["category"], CAT_OTHER)

        # Empty DataFrame to report generator
        empty_md = RegionalBriefGenerator.generate_markdown(pd.DataFrame())
        self.assertIn("No feedback records found", empty_md)

        # Empty CSV to data manager
        df_empty, audit_empty, msgs_empty = validate_and_process_dataset(io.StringIO(""))
        self.assertTrue(df_empty.empty)
        self.assertTrue(any("empty" in m.lower() for m in msgs_empty))


if __name__ == "__main__":
    unittest.main()

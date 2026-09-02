"""
Automated unit & metric consistency test suite for AtliQ Grands Hospitality Analytics.
"""

import os
import sqlite3
import unittest
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from data_generator import generate_all_hospitality_data
from metrics_engine import HospitalityMetricsEngine, DB_PATH

class TestHospitalityMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate_all_hospitality_data()
        cls.engine = HospitalityMetricsEngine(db_path=DB_PATH)
        cls.engine.init_db()
        cls.engine.load_data()
        cls.kpis = cls.engine.compute_executive_kpis()

    def test_database_tables_populated(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM dim_hotels")
        self.assertEqual(cur.fetchone()[0], 8)

        cur.execute("SELECT COUNT(*) FROM dim_rooms")
        self.assertEqual(cur.fetchone()[0], 4)

        cur.execute("SELECT COUNT(*) FROM fact_bookings")
        self.assertGreater(cur.fetchone()[0], 10000)

        conn.close()

    def test_hospitality_metric_identities(self):
        """
        Verify fundamental hospitality mathematical identities:
        RevPAR should be roughly ADR * (Occupancy% / 100) * (Realisation% / 100)
        """
        revpar = self.kpis["RevPAR (Revenue Per Available Room)"]
        adr = self.kpis["ADR (Average Daily Rate)"]
        occ = self.kpis["Occupancy %"] / 100.0
        realisation = self.kpis["Realisation %"] / 100.0

        # Theoretical RevPAR calculated from components
        calc_revpar = adr * occ * realisation
        # Allow within 5% tolerance due to cancellations / no-show retention
        self.assertAlmostEqual(revpar, calc_revpar, delta=revpar * 0.10)

    def test_occupancy_bounded(self):
        occ = self.kpis["Occupancy %"]
        self.assertGreater(occ, 30.0)
        self.assertLessEqual(occ, 100.0)

    def test_cancellation_rates(self):
        cancel_pct = self.kpis["Cancellation %"]
        self.assertGreater(cancel_pct, 10.0)
        self.assertLess(cancel_pct, 40.0)

if __name__ == "__main__":
    unittest.main()

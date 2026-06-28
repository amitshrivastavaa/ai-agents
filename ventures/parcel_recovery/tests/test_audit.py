import unittest
from datetime import date

from ventures.parcel_recovery.audit import (
    Shipment, audit, summarize, check_late_delivery, check_dim_weight,
    check_residential, check_address_correction, check_rate_mismatch, check_lost)
from ventures.parcel_recovery.claims import filing_pack
from ventures.parcel_recovery.sample_data import sample_shipments


def mk(**kw):
    base = dict(
        tracking="T1", carrier="FedEx", service="2Day",
        ship_date=date(2026, 3, 1), delivery_date=date(2026, 3, 3),
        committed_date=date(2026, 3, 3), zone=5, actual_weight=5.0,
        billed_weight=5.0, length_in=10, width_in=8, height_in=6,
        is_residential=True, charges={"base": 20.0, "fuel": 3.0},
        address_was_valid=True, contracted_base=None)
    base.update(kw)
    return Shipment(**base)


class TestRules(unittest.TestCase):
    def test_late_delivery_refunds_transport(self):
        c = check_late_delivery(mk(delivery_date=date(2026, 3, 5)))
        self.assertIsNotNone(c)
        self.assertEqual(c.category, "late_delivery")
        self.assertAlmostEqual(c.amount, 23.0)          # base + fuel
        self.assertEqual(c.file_within_days, 15)

    def test_on_time_no_claim(self):
        self.assertIsNone(check_late_delivery(mk(delivery_date=date(2026, 3, 3))))

    def test_dim_weight_overcharge(self):
        # actual 5, dim(10x8x6)=3.45->ceil 4 => expected 5; billed 15 => over 10 lb
        s = mk(actual_weight=5.0, billed_weight=15.0, charges={"base": 30.0, "fuel": 5.0})
        c = check_dim_weight(s)
        self.assertIsNotNone(c)
        self.assertAlmostEqual(c.amount, round(30.0 * 10 / 15, 2))

    def test_dim_weight_clean(self):
        self.assertIsNone(check_dim_weight(mk(actual_weight=5.0, billed_weight=5.0)))

    def test_invalid_residential(self):
        s = mk(is_residential=False, charges={"base": 20.0, "fuel": 3.0, "residential": 5.85})
        c = check_residential(s)
        self.assertIsNotNone(c)
        self.assertAlmostEqual(c.amount, 5.85)

    def test_valid_residential_no_claim(self):
        s = mk(is_residential=True, charges={"base": 20.0, "fuel": 3.0, "residential": 5.85})
        self.assertIsNone(check_residential(s))

    def test_invalid_address_correction(self):
        s = mk(address_was_valid=True,
               charges={"base": 20.0, "fuel": 3.0, "address_correction": 18.0})
        self.assertIsNotNone(check_address_correction(s))

    def test_address_correction_ok_when_address_bad(self):
        s = mk(address_was_valid=False,
               charges={"base": 20.0, "fuel": 3.0, "address_correction": 18.0})
        self.assertIsNone(check_address_correction(s))

    def test_rate_mismatch(self):
        c = check_rate_mismatch(mk(charges={"base": 41.0, "fuel": 6.6}, contracted_base=33.0))
        self.assertAlmostEqual(c.amount, 8.0)

    def test_rate_ok(self):
        self.assertIsNone(
            check_rate_mismatch(mk(charges={"base": 30.0, "fuel": 5.0}, contracted_base=33.0)))

    def test_lost(self):
        c = check_lost(mk(delivery_date=None, committed_date=None), date(2026, 3, 20))
        self.assertIsNotNone(c)
        self.assertEqual(c.category, "lost_in_transit")

    def test_not_lost_if_recent(self):
        s = mk(delivery_date=None, committed_date=None, ship_date=date(2026, 3, 18))
        self.assertIsNone(check_lost(s, date(2026, 3, 20)))


class TestAuditSet(unittest.TestCase):
    def setUp(self):
        self.shipments = sample_shipments()
        self.claims = audit(self.shipments)

    def test_finds_every_category(self):
        cats = {c.category for c in self.claims}
        for expected in ("late_delivery", "dim_weight", "invalid_residential",
                         "invalid_address_correction", "rate_mismatch",
                         "lost_in_transit", "duplicate_charge"):
            self.assertIn(expected, cats)

    def test_duplicate_counted_once(self):
        dups = [c for c in self.claims if c.category == "duplicate_charge"]
        self.assertEqual(len(dups), 1)

    def test_clean_shipment_yields_nothing(self):
        clean = mk(tracking="CLEAN", delivery_date=date(2026, 3, 3),
                   committed_date=date(2026, 3, 3))
        self.assertEqual(audit([clean]), [])

    def test_recovery_meaningful_but_bounded(self):
        s = summarize(self.shipments, self.claims)
        self.assertGreater(s["total_recoverable"], 200)
        self.assertLess(s["recovery_rate"], 0.15)        # realistic, not absurd
        self.assertAlmostEqual(s["your_fee"] + s["client_net"], s["total_recoverable"], places=2)

    def test_economics_split(self):
        s = summarize(self.shipments, self.claims, contingency=0.25)
        self.assertAlmostEqual(s["your_fee"], round(s["total_recoverable"] * 0.25, 2))

    def test_filing_pack_renders_both_carriers(self):
        txt = filing_pack(self.claims)
        self.assertIn("FedEx", txt)
        self.assertIn("UPS", txt)


if __name__ == "__main__":
    unittest.main()

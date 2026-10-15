# Copyright (c) 2026, Frappe Technologies and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestSiteVisitLog(FrappeTestCase):
	def make_log(self, **overrides):
		data = {
			"doctype": "Site Visit Log",
			"client_name": "Test Client",
			"visit_date": today(),
			"purpose": "Routine check",
			"follow_up_needed": 0,
		}
		data.update(overrides)
		return frappe.get_doc(data)

	def test_status_flips_with_follow_up_checkbox(self):
		log = self.make_log(follow_up_needed=1, follow_up_date=add_days(today(), 3))
		log.insert()
		self.assertEqual(log.status, "Follow-up Pending")

		log.follow_up_needed = 0
		log.follow_up_date = None
		log.save()
		self.assertEqual(log.status, "No Follow-up")

	def test_follow_up_date_required_when_needed(self):
		log = self.make_log(follow_up_needed=1)
		self.assertRaises(frappe.ValidationError, log.insert)

	def test_follow_up_date_cannot_be_before_visit_date(self):
		log = self.make_log(follow_up_needed=1, follow_up_date=add_days(today(), -1))
		self.assertRaises(frappe.ValidationError, log.insert)

	def test_follow_up_date_not_allowed_when_not_needed(self):
		log = self.make_log(follow_up_needed=0, follow_up_date=add_days(today(), 3))
		self.assertRaises(frappe.ValidationError, log.insert)
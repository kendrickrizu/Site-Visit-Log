import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class SiteVisitLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF


	# end: auto-generated types
	def validate(self):
		if self.follow_up_needed:
			self.status = "Follow-up Pending"
			if not self.follow_up_date:
				frappe.throw("Follow-up date is required when follow-up is needed.")
			if getdate(self.follow_up_date) < getdate(self.visit_date):
				frappe.throw("Follow-up date can not be before visit date.")
		else:
			if self.follow_up_date:
				frappe.throw("Follow-up date can not be set when follow-up is not needed.")
			self.status = "No Follow-up"

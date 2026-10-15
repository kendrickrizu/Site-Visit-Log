frappe.ui.form.on("Site Visit Log", {
	refresh(frm) {
		toggle_follow_up_date(frm)
	},

	follow_up_needed(frm) {
		toggle_follow_up_date(frm)
	},
})

function toggle_follow_up_date(frm) {
	const isNeeded = frm.doc.follow_up_needed ? true : false

	frm.toggle_display("follow_up_date", isNeeded)
	frm.toggle_reqd("follow_up_date", isNeeded)

	if (!isNeeded) {
		frm.set_value("follow_up_date", null)
	}
}
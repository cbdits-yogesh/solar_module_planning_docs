/**
 * DocType: Employee OT
 * Apply To: Form
 */

frappe.ui.form.on("Employee OT", {
    emp_id: function (frm) {
        run_day_salary_check(frm);
    },
    date: function (frm) {
        run_day_salary_check(frm);
    },
});

function run_day_salary_check(frm) {
    if (!frm.doc.emp_id || !frm.doc.date) {
        return;
    }

    const SALARY_LIMIT = 40000;
    const WEEKDAY_NAMES = [
        "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"
    ];

    const ot_date = frappe.datetime.str_to_obj(frm.doc.date);
    const weekday = WEEKDAY_NAMES[ot_date.getDay()];

    // Sunday: no restriction, skip check
    if (weekday === "Sunday") {
        return;
    }

    frappe.db.get_value(
        "Employee",
        frm.doc.emp_id,
        ["status", "ctc", "employee_name"]
    ).then((r) => {
        const emp = r.message;
        if (!emp) {
            frappe.msgprint({
                title: __("Employee Not Found"),
                message: __("Employee record for {0} not found.", [frm.doc.emp_id]),
                indicator: "red",
            });
            return;
        }

        const emp_status = emp.status;
        const emp_ctc = emp.ctc;
        const emp_name = emp.employee_name;

        // STEP 2 logic mirrored from server: status check
        if (emp_status !== "Active") {
            frappe.msgprint({
                title: __("Not Eligible"),
                message: __("Employee {0} is not Active. OT cannot be filed.", [emp_name]),
                indicator: "red",
            });
            return;
        }

        // STEP 2 logic mirrored from server: salary check
        if (emp_ctc && emp_ctc > SALARY_LIMIT) {
            frappe.msgprint({
                title: __("Not Eligible"),
                message: __("Employee {0} is not eligible for Overtime on {1}.", [emp_name, weekday]),
                indicator: "red",
            });
            frm.set_value("date", "");
            frm.set_value("in_time", "");
            frm.set_value("out_time", "");
        }
    });
}
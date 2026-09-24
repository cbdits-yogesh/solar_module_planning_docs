/**
 * DocType: Liaisoning And Synchronization
 * Apply To: Form
 */

frappe.ui.form.on('Liaisoning And Synchronization', {
    refresh: function(frm) {

        // Clickable link for Project field
        if (frm.doc.project) {
            frm.fields_dict['project'].$input_wrapper
                .find('.control-value, .like-disabled-input')
                .html(`<a href="/app/project/${encodeURIComponent(frm.doc.project)}" 
                    target="_blank" style="color: var(--primary)">
                    ${frm.doc.project}
                </a>`);
        }

        // Clickable link for Proposal field
        if (frm.doc.proposal) {
            frm.fields_dict['proposal'].$input_wrapper
                .find('.control-value, .like-disabled-input')
                .html(`<a href="/app/quotation/${encodeURIComponent(frm.doc.proposal)}" 
                    target="_blank" style="color: var(--primary)">
                    ${frm.doc.proposal}
                </a>`);
        }

        // Clickable link for Site Survey field
        if (frm.doc.site_survey) {
            frm.fields_dict['site_survey'].$input_wrapper
                .find('.control-value, .like-disabled-input')
                .html(`<a href="/app/site-survey/${encodeURIComponent(frm.doc.site_survey)}" 
                    target="_blank" style="color: var(--primary)">
                    ${frm.doc.site_survey}
                </a>`);
        }

    }
});

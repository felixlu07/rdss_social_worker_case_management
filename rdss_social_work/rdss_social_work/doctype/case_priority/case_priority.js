// Copyright (c) 2025, RDSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case Priority', {
    refresh: function(frm) {
        // Display a color swatch preview
        if (frm.doc.color_code) {
            frm.set_intro(`<div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="background-color: ${frm.doc.color_code}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
                <span>This priority will be displayed with ${frm.doc.color_code} color</span>
            </div>`);
        }
    },
    
    color_code: function(frm) {
        // Update the color preview when color changes
        if (frm.doc.color_code) {
            frm.set_intro(`<div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="background-color: ${frm.doc.color_code}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
                <span>This priority will be displayed with ${frm.doc.color_code} color</span>
            </div>`);
        }
    }
});

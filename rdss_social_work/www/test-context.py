import frappe

def get_context(context):
    context.title = "Context Test"
    context.test_message = "Context is working"
    context.current_user = frappe.session.user
    return context

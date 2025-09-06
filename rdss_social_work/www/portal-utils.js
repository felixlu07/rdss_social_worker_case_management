// Shared utilities for beneficiary portal pages
window.PortalUtils = {
    // Show loading state on buttons
    setButtonLoading: function(buttonId, loading = true, loadingText = 'Loading...') {
        const btn = document.getElementById(buttonId);
        if (!btn) return;
        
        if (loading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = `<i class="fa fa-spinner fa-spin"></i> ${loadingText}`;
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
            btn.disabled = false;
        }
    },
    
    // Show validation errors with proper styling
    showValidationErrors: function(errors, title = 'Validation Errors') {
        if (errors.length === 0) return true;
        
        const errorHtml = errors.map(error => `<li>${error}</li>`).join('');
        frappe.msgprint({
            title: title,
            message: `<ul style="margin: 0; padding-left: 20px;">${errorHtml}</ul>`,
            indicator: 'red'
        });
        return false;
    },
    
    // Add validation styling to form fields
    markFieldInvalid: function(fieldId, isInvalid = true) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        if (isInvalid) {
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    },
    
    // Validate required fields
    validateRequiredFields: function(fieldConfigs) {
        const errors = [];
        
        fieldConfigs.forEach(config => {
            const element = document.getElementById(config.id);
            if (!element) return;
            
            const value = element.type === 'checkbox' ? element.checked : element.value.trim();
            
            if (!value) {
                errors.push(`${config.name} is required`);
                this.markFieldInvalid(config.id, true);
            } else {
                this.markFieldInvalid(config.id, false);
            }
        });
        
        return errors;
    },
    
    // Validate email format
    validateEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Show success message with redirect
    showSuccessAndRedirect: function(message, redirectUrl, delay = 2000) {
        frappe.msgprint({
            title: 'Success',
            message: message,
            indicator: 'green'
        });
        
        if (redirectUrl) {
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, delay);
        }
    },
    
    // Show error message
    showError: function(message, title = 'Error') {
        frappe.msgprint({
            title: title,
            message: message,
            indicator: 'red'
        });
    },
    
    // Add loading overlay to forms
    addFormOverlay: function(formId, show = true) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        let overlay = form.querySelector('.form-overlay');
        
        if (show) {
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'form-overlay';
                overlay.innerHTML = `
                    <div class="overlay-content">
                        <i class="fa fa-spinner fa-spin fa-2x"></i>
                        <p>Processing...</p>
                    </div>
                `;
                form.style.position = 'relative';
                form.appendChild(overlay);
            }
            overlay.style.display = 'flex';
        } else {
            if (overlay) {
                overlay.style.display = 'none';
            }
        }
    },
    
    // Debounce function for input validation
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Check network connectivity
    checkConnectivity: function() {
        return navigator.onLine;
    },
    
    // Handle network errors
    handleNetworkError: function() {
        if (!this.checkConnectivity()) {
            this.showError('No internet connection. Please check your network and try again.', 'Connection Error');
        } else {
            this.showError('Network error occurred. Please try again.', 'Network Error');
        }
    }
};

// Add global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    if (window.PortalUtils) {
        PortalUtils.showError('An unexpected error occurred. Please refresh the page and try again.');
    }
});

// Add unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    if (window.PortalUtils) {
        PortalUtils.showError('An error occurred while processing your request. Please try again.');
    }
});

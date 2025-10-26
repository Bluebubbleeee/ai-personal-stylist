/**
 * AI Stylist - Main JavaScript
 * Handles common functionality across the application
 */

// Global application object
window.AIStylist = {
    // Configuration
    config: {
        apiBaseUrl: '/api/',
        csrfToken: null,
        userId: null,
    },
    
    // Utility functions
    utils: {},
    
    // API functions
    api: {},
    
    // UI functions
    ui: {},
    
    // Components
    components: {},
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    AIStylist.init();
});

/**
 * Initialize the application
 */
AIStylist.init = function() {
    // Get CSRF token
    this.config.csrfToken = this.utils.getCSRFToken();
    
    // Initialize components
    this.ui.initTooltips();
    this.ui.initAlerts();
    this.ui.initLoading();
    this.ui.initNavigation();
    
    console.log('AI Stylist initialized successfully');
};

/**
 * Utility Functions
 */
AIStylist.utils = {
    /**
     * Get CSRF token from cookies or meta tag
     */
    getCSRFToken: function() {
        // First try to get from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        // Fallback to cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        
        // Last resort: try to find in DOM
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfInput ? csrfInput.value : null;
    },
    
    /**
     * Format date to readable string
     */
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Date(date).toLocaleDateString(undefined, {...defaultOptions, ...options});
    },
    
    /**
     * Debounce function
     */
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
    
    /**
     * Generate random ID
     */
    generateId: function(prefix = 'id') {
        return prefix + '_' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Validate email format
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    /**
     * Check if string is empty or whitespace
     */
    isEmpty: function(str) {
        return !str || str.trim().length === 0;
    },
    
    /**
     * Capitalize first letter
     */
    capitalize: function(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

/**
 * API Functions
 */
AIStylist.api = {
    /**
     * Make API request
     */
    request: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AIStylist.config.csrfToken
            },
            credentials: 'same-origin'
        };
        
        return fetch(url, {...defaultOptions, ...options})
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API Request failed:', error);
                throw error;
            });
    },
    
    /**
     * GET request
     */
    get: function(endpoint) {
        return this.request(AIStylist.config.apiBaseUrl + endpoint);
    },
    
    /**
     * POST request
     */
    post: function(endpoint, data) {
        return this.request(AIStylist.config.apiBaseUrl + endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * PUT request
     */
    put: function(endpoint, data) {
        return this.request(AIStylist.config.apiBaseUrl + endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * DELETE request
     */
    delete: function(endpoint) {
        return this.request(AIStylist.config.apiBaseUrl + endpoint, {
            method: 'DELETE'
        });
    }
};

/**
 * UI Functions
 */
AIStylist.ui = {
    /**
     * Initialize Bootstrap tooltips
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    /**
     * Initialize alert auto-dismiss
     */
    initAlerts: function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000);
        });
    },
    
    /**
     * Initialize loading states
     */
    initLoading: function() {
        // Add loading overlay HTML to body if not exists
        if (!document.getElementById('loading-overlay')) {
            const loadingHTML = `
                <div id="loading-overlay" class="loading-overlay d-none">
                    <div class="loading-spinner"></div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', loadingHTML);
        }
    },
    
    /**
     * Initialize navigation
     */
    initNavigation: function() {
        // Highlight active nav item
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },
    
    /**
     * Show loading overlay
     */
    showLoading: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    },
    
    /**
     * Hide loading overlay
     */
    hideLoading: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    },
    
    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info', duration = 5000) {
        const toastId = AIStylist.utils.generateId('toast');
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Create toast container if not exists
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Add toast to container
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        // Show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },
    
    /**
     * Show confirmation modal
     */
    showConfirmModal: function(title, message, onConfirm, onCancel = null) {
        const modalId = AIStylist.utils.generateId('modal');
        const modalHTML = `
            <div id="${modalId}" class="modal fade" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="${modalId}Confirm">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        const modalElement = document.getElementById(modalId);
        const modal = new bootstrap.Modal(modalElement);
        
        // Handle confirm button
        document.getElementById(modalId + 'Confirm').addEventListener('click', () => {
            modal.hide();
            if (onConfirm) onConfirm();
        });
        
        // Handle cancel
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
            if (onCancel) onCancel();
        });
        
        modal.show();
    },
    
    /**
     * Animate number counter
     */
    animateCounter: function(element, target, duration = 1000) {
        const start = parseInt(element.textContent) || 0;
        const increment = (target - start) / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }
};

/**
 * Form handling utilities
 */
AIStylist.forms = {
    /**
     * Serialize form data to object
     */
    serialize: function(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                // Handle multiple values (e.g., checkboxes)
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    /**
     * Validate form using HTML5 validation
     */
    validate: function(form) {
        const isValid = form.checkValidity();
        form.classList.add('was-validated');
        return isValid;
    },
    
    /**
     * Reset form validation
     */
    resetValidation: function(form) {
        form.classList.remove('was-validated');
        const inputs = form.querySelectorAll('.form-control, .form-select, .form-check-input');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
    },
    
    /**
     * Show field error
     */
    showFieldError: function(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },
    
    /**
     * Clear field error
     */
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = '';
        }
    }
};

/**
 * Local storage utilities
 */
AIStylist.storage = {
    /**
     * Set item in localStorage with expiry
     */
    setItem: function(key, value, expiryMinutes = null) {
        const item = {
            value: value,
            timestamp: new Date().getTime()
        };
        
        if (expiryMinutes) {
            item.expiry = new Date().getTime() + (expiryMinutes * 60 * 1000);
        }
        
        localStorage.setItem(key, JSON.stringify(item));
    },
    
    /**
     * Get item from localStorage
     */
    getItem: function(key) {
        const itemStr = localStorage.getItem(key);
        
        if (!itemStr) {
            return null;
        }
        
        const item = JSON.parse(itemStr);
        
        // Check if expired
        if (item.expiry && new Date().getTime() > item.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        
        return item.value;
    },
    
    /**
     * Remove item from localStorage
     */
    removeItem: function(key) {
        localStorage.removeItem(key);
    },
    
    /**
     * Clear all localStorage items
     */
    clear: function() {
        localStorage.clear();
    }
};

/**
 * Error handling
 */
AIStylist.errorHandler = {
    /**
     * Handle API errors
     */
    handleApiError: function(error) {
        console.error('API Error:', error);
        
        let message = 'An unexpected error occurred. Please try again.';
        
        if (error.message) {
            message = error.message;
        }
        
        AIStylist.ui.showToast(message, 'danger');
    },
    
    /**
     * Handle form errors
     */
    handleFormErrors: function(form, errors) {
        // Clear existing errors
        AIStylist.forms.resetValidation(form);
        
        // Show field-specific errors
        for (let field in errors) {
            const fieldElement = form.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const errorMessage = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
                AIStylist.forms.showFieldError(fieldElement, errorMessage);
            } else {
                // Show general error if field not found
                AIStylist.ui.showToast(errors[field], 'danger');
            }
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIStylist;
}

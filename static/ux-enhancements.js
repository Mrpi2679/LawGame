// Enhanced UX Utilities for Law Game

class LawGameUX {
    constructor() {
        this.init();
    }

    init() {
        this.addEnhancedClass();
        this.setupBackButtonHandling();
        this.setupFormEnhancements();
        this.setupNotificationSystem();
        this.setupProgressAnimations();
        this.setupAccessibilityFeatures();
    }

    // Add JS enhanced class for CSS targeting
    addEnhancedClass() {
        document.documentElement.classList.add('js-enhanced');
    }

    // Enhanced back button functionality
    setupBackButtonHandling() {
        // Add smart back button handling
        const backButtons = document.querySelectorAll('[data-back]');
        backButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const fallback = button.getAttribute('href');
                
                // Try to go back in history if available
                if (window.history.length > 1) {
                    window.history.back();
                } else {
                    // Fallback to href
                    window.location.href = fallback;
                }
            });
        });
    }

    // Form enhancements
    setupFormEnhancements() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            this.enhanceForm(form);
        });
    }

    enhanceForm(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (!submitBtn) return;

        form.addEventListener('submit', (e) => {
            // Don't interfere with form submission for login and signup forms
            if (form.id === 'loginForm' || form.action.includes('/login') || form.action.includes('/signup')) {
                this.showFormLoading(submitBtn);
                return;
            }
            
            // Validate if needed
            if (!form.checkValidity()) {
                e.preventDefault();
                this.showFormErrors(form);
                return;
            }

            // Show loading state
            this.showFormLoading(submitBtn);
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    showFormLoading(button) {
        button.classList.add('btn-loading');
        button.disabled = true;
        
        // Store original text
        const originalText = button.textContent;
        button.setAttribute('data-original-text', originalText);
    }

    validateField(field) {
        if (field.validity.valid) {
            field.style.borderColor = 'var(--secondary-brass)';
            return true;
        } else {
            field.style.borderColor = '#f87171';
            field.classList.add('shake-error');
            setTimeout(() => field.classList.remove('shake-error'), 500);
            return false;
        }
    }

    clearFieldError(field) {
        if (field.style.borderColor === 'rgb(248, 113, 113)') {
            field.style.borderColor = '';
        }
    }

    showFormErrors(form) {
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) {
            firstInvalid.focus();
            this.validateField(firstInvalid);
        }
        
        this.showNotification('Please correct the errors in the form', 'error');
    }

    // Notification system
    setupNotificationSystem() {
        // Convert flash messages to toast notifications
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            const text = message.textContent.trim();
            const type = message.textContent.toLowerCase().includes('error') ? 'error' : 
                        message.textContent.toLowerCase().includes('success') ? 'success' : 'info';
            
            this.showNotification(text, type);
            message.style.display = 'none';
        });
    }

    showNotification(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `notification-toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    // Progress animations
    setupProgressAnimations() {
        // Animate progress bars on load
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-in-out';
                bar.style.width = width;
            }, 100);
        });

        // Animate step indicators
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            setTimeout(() => {
                step.style.animation = 'fadeIn 0.5s ease-out';
            }, index * 100);
        });
    }

    // Accessibility enhancements
    setupAccessibilityFeatures() {
        // Add ARIA labels where needed
        this.addAriaLabels();
        
        // Setup keyboard navigation
        this.setupKeyboardNavigation();
        
        // Announce dynamic content changes
        this.setupScreenReaderAnnouncements();
    }

    addAriaLabels() {
        // Add aria-label to interactive elements
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (!btn.getAttribute('aria-label')) {
                btn.setAttribute('aria-label', btn.textContent.trim());
            }
        });
    }

    setupKeyboardNavigation() {
        // Enable keyboard navigation for cards
        const cards = document.querySelectorAll('.mode-card, .level-card, .scenario-card');
        cards.forEach(card => {
            card.setAttribute('tabindex', '0');
            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const link = card.querySelector('a');
                    if (link) link.click();
                }
            });
        });
    }

    setupScreenReaderAnnouncements() {
        // Announce form submission status
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                this.announceToScreenReader('Form submitted successfully', 'polite');
            });
        });
    }

    announceToScreenReader(message, priority = 'polite') {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', priority);
        announcement.setAttribute('class', 'sr-only');
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        setTimeout(() => {
            if (announcement.parentNode) {
                announcement.parentNode.removeChild(announcement);
            }
        }, 1000);
    }

    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Enhanced loading states
    showGlobalLoading(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-overlay-content">
                <div class="loading-spinner-large"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
        return overlay;
    }

    hideGlobalLoading(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
        }
    }
}

// Initialize UX enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.lawGameUX = new LawGameUX();
});

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LawGameUX;
}
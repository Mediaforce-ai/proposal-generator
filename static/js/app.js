/**
 * Mediaforce Proposal Generator - Web App JavaScript
 */

// Alert dismissal
document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', function() {
        this.parentElement.remove();
    });
});

// Auto-dismiss alerts after 5 seconds
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.3s';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
});

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let valid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                valid = false;
                field.classList.add('error');
                field.addEventListener('input', () => field.classList.remove('error'), { once: true });
            }
        });

        if (!valid) {
            e.preventDefault();
            alert('Please fill in all required fields.');
        }
    });
});

// Service toggle functionality
document.querySelectorAll('.service-card input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const card = this.closest('.service-card');
        const inputs = card.querySelectorAll('.service-body input');

        inputs.forEach(input => {
            input.disabled = !this.checked;
            if (!this.checked) {
                input.value = input.type === 'number' ? '0' : '';
            }
        });
    });

    // Initialize state
    checkbox.dispatchEvent(new Event('change'));
});

// Number formatting
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value && !isNaN(this.value)) {
            this.value = parseInt(this.value, 10);
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    // Ctrl/Cmd + S to save/submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
});

// Loading state for buttons
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.type === 'submit' || this.classList.contains('btn-loading')) {
            this.classList.add('loading');
            this.disabled = true;

            // Re-enable after 10 seconds as fallback
            setTimeout(() => {
                this.classList.remove('loading');
                this.disabled = false;
            }, 10000);
        }
    });
});

console.log('Mediaforce Proposal Generator loaded');

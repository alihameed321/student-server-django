// Custom JavaScript for My University Services

// Global utilities
window.UniversityServices = {
    // CSRF token helper
    getCSRFToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
    },

    // API helper
    api: {
        get: async function(url) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });
                return await response.json();
            } catch (error) {
                console.error('API GET Error:', error);
                throw error;
            }
        },

        post: async function(url, data) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                console.error('API POST Error:', error);
                throw error;
            }
        }.bind(this)
    },

    // Notification system
    notify: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 bg-white border-l-4 p-4 shadow-lg rounded-r-lg max-w-sm toast`;
        
        const iconClass = {
            'success': 'fas fa-check-circle text-green-500',
            'error': 'fas fa-exclamation-circle text-red-500',
            'warning': 'fas fa-exclamation-triangle text-yellow-500',
            'info': 'fas fa-info-circle text-blue-500'
        }[type] || 'fas fa-info-circle text-blue-500';
        
        const borderClass = {
            'success': 'border-green-500',
            'error': 'border-red-500',
            'warning': 'border-yellow-500',
            'info': 'border-blue-500'
        }[type] || 'border-blue-500';
        
        notification.classList.add(borderClass);
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="${iconClass} mr-2"></i>
                <span class="text-gray-800">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },

    // File upload helper
    fileUpload: {
        setupDropZone: function(element, callback) {
            element.addEventListener('dragover', function(e) {
                e.preventDefault();
                element.classList.add('dragover');
            });
            
            element.addEventListener('dragleave', function(e) {
                e.preventDefault();
                element.classList.remove('dragover');
            });
            
            element.addEventListener('drop', function(e) {
                e.preventDefault();
                element.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (callback) callback(files);
            });
        },

        validateFile: function(file, maxSize = 5 * 1024 * 1024, allowedTypes = []) {
            if (file.size > maxSize) {
                return { valid: false, error: `File size must be less than ${maxSize / 1024 / 1024}MB` };
            }
            
            if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
                return { valid: false, error: `File type not allowed. Allowed types: ${allowedTypes.join(', ')}` };
            }
            
            return { valid: true };
        }
    },

    // Form helpers
    form: {
        serialize: function(form) {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            return data;
        },

        validate: function(form) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('border-red-500');
                    isValid = false;
                } else {
                    field.classList.remove('border-red-500');
                }
            });
            
            return isValid;
        }
    },

    // Date helpers
    date: {
        format: function(date, format = 'YYYY-MM-DD') {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day);
        },

        timeAgo: function(date) {
            const now = new Date();
            const diff = now - new Date(date);
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
            
            if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
            if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
            if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
            return 'Just now';
        }
    }
};

// Alpine.js data components
document.addEventListener('alpine:init', () => {
    // Notification center component
    Alpine.data('notificationCenter', () => ({
        notifications: [],
        unreadCount: 0,
        loading: false,

        async init() {
            await this.loadNotifications();
            this.updateUnreadCount();
        },

        async loadNotifications() {
            this.loading = true;
            try {
                const data = await UniversityServices.api.get('/notifications/ajax/recent-notifications/');
                this.notifications = data.notifications || [];
            } catch (error) {
                console.error('Failed to load notifications:', error);
            } finally {
                this.loading = false;
            }
        },

        async updateUnreadCount() {
            try {
                const data = await UniversityServices.api.get('/notifications/ajax/unread-count/');
                this.unreadCount = data.count || 0;
            } catch (error) {
                console.error('Failed to update unread count:', error);
            }
        },

        async markAsRead(notificationId) {
            try {
                await UniversityServices.api.post(`/notifications/${notificationId}/mark-read/`, {});
                const notification = this.notifications.find(n => n.id === notificationId);
                if (notification) {
                    notification.is_read = true;
                    this.unreadCount = Math.max(0, this.unreadCount - 1);
                }
            } catch (error) {
                console.error('Failed to mark notification as read:', error);
            }
        }
    }));

    // File upload component
    Alpine.data('fileUpload', (options = {}) => ({
        files: [],
        uploading: false,
        progress: 0,
        maxSize: options.maxSize || 5 * 1024 * 1024, // 5MB
        allowedTypes: options.allowedTypes || [],
        multiple: options.multiple || false,

        init() {
            const dropZone = this.$refs.dropZone;
            if (dropZone) {
                UniversityServices.fileUpload.setupDropZone(dropZone, (files) => {
                    this.handleFiles(files);
                });
            }
        },

        handleFiles(fileList) {
            const files = Array.from(fileList);
            
            if (!this.multiple) {
                this.files = [];
            }
            
            files.forEach(file => {
                const validation = UniversityServices.fileUpload.validateFile(
                    file, this.maxSize, this.allowedTypes
                );
                
                if (validation.valid) {
                    this.files.push({
                        file: file,
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        preview: this.getFilePreview(file)
                    });
                } else {
                    UniversityServices.notify(validation.error, 'error');
                }
            });
        },

        removeFile(index) {
            this.files.splice(index, 1);
        },

        getFilePreview(file) {
            if (file.type.startsWith('image/')) {
                return URL.createObjectURL(file);
            }
            return null;
        },

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    }));

    // Search component
    Alpine.data('searchComponent', (options = {}) => ({
        query: '',
        results: [],
        loading: false,
        debounceTimer: null,
        minLength: options.minLength || 2,
        searchUrl: options.searchUrl || '',

        search() {
            clearTimeout(this.debounceTimer);
            
            if (this.query.length < this.minLength) {
                this.results = [];
                return;
            }
            
            this.debounceTimer = setTimeout(async () => {
                this.loading = true;
                try {
                    const data = await UniversityServices.api.get(
                        `${this.searchUrl}?q=${encodeURIComponent(this.query)}`
                    );
                    this.results = data.results || [];
                } catch (error) {
                    console.error('Search failed:', error);
                    this.results = [];
                } finally {
                    this.loading = false;
                }
            }, 300);
        },

        selectResult(result) {
            this.$dispatch('result-selected', result);
            this.query = '';
            this.results = [];
        }
    }));

    // Dashboard stats component
    Alpine.data('dashboardStats', () => ({
        stats: {},
        loading: true,

        async init() {
            await this.loadStats();
        },

        async loadStats() {
            this.loading = true;
            try {
                const data = await UniversityServices.api.get('/staff-panel/ajax/dashboard-stats/');
                this.stats = data;
            } catch (error) {
                console.error('Failed to load dashboard stats:', error);
            } finally {
                this.loading = false;
            }
        },

        async refreshStats() {
            await this.loadStats();
            UniversityServices.notify('Stats refreshed', 'success');
        }
    }));
});

// Global event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!UniversityServices.form.validate(form)) {
                e.preventDefault();
                UniversityServices.notify('Please fill in all required fields', 'error');
            }
        });
    });

    // Confirm dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-refresh elements
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    autoRefreshElements.forEach(element => {
        const interval = parseInt(element.getAttribute('data-auto-refresh')) || 30000;
        const url = element.getAttribute('data-refresh-url');
        
        if (url) {
            setInterval(async () => {
                try {
                    const response = await fetch(url);
                    const html = await response.text();
                    element.innerHTML = html;
                } catch (error) {
                    console.error('Auto-refresh failed:', error);
                }
            }, interval);
        }
    });
});

// Export for global access
window.US = UniversityServices;
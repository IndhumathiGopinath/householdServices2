/**
 * Admin dashboard specific JavaScript
 * Handles functionality specific to the admin area
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin dashboard Vue app if it exists
    if (document.getElementById('admin-dashboard')) {
        new Vue({
            el: '#admin-dashboard',
            delimiters: ['${', '}'],
            data: {
                // Dashboard statistics
                stats: {
                    services: 0,
                    professionals: 0,
                    customers: 0,
                    requests: 0,
                    pendingRequests: 0,
                    completedRequests: 0
                },
                recentRequests: [],
                pendingVerifications: [],
                loading: false,
                refreshInterval: null
            },
            methods: {
                // Fetch dashboard statistics
                fetchStats() {
                    this.loading = true;
                    axios.get('/admin/api/stats')
                        .then(response => {
                            this.stats = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching admin stats:', error);
                            this.loading = false;
                        });
                },
                
                // Fetch recent service requests
                fetchRecentRequests() {
                    axios.get('/admin/api/recent-requests')
                        .then(response => {
                            this.recentRequests = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching recent requests:', error);
                        });
                },
                
                // Fetch professionals pending verification
                fetchPendingVerifications() {
                    axios.get('/admin/api/pending-verifications')
                        .then(response => {
                            this.pendingVerifications = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching pending verifications:', error);
                        });
                },
                
                // Verify a professional
                verifyProfessional(professionalId) {
                    axios.post(`/admin/professional/verify/${professionalId}`)
                        .then(response => {
                            // Remove from pending list
                            this.pendingVerifications = this.pendingVerifications.filter(
                                p => p.id !== professionalId
                            );
                            
                            // Show success message
                            this.showAlert('Professional verified successfully!', 'success');
                        })
                        .catch(error => {
                            console.error('Error verifying professional:', error);
                            this.showAlert('Failed to verify professional', 'danger');
                        });
                },
                
                // Toggle user active status
                toggleUserActive(userId) {
                    axios.post(`/admin/user/toggle-active/${userId}`)
                        .then(response => {
                            this.showAlert('User status updated successfully!', 'success');
                            // Refresh data
                            this.fetchPendingVerifications();
                        })
                        .catch(error => {
                            console.error('Error toggling user status:', error);
                            this.showAlert('Failed to update user status', 'danger');
                        });
                },
                
                // Show alert message
                showAlert(message, type = 'info') {
                    // Implementation would depend on how alerts are shown in the UI
                    console.log(`[${type}] ${message}`);
                }
            },
            created() {
                // Fetch initial data
                this.fetchStats();
                this.fetchRecentRequests();
                this.fetchPendingVerifications();
                
                // Set up auto-refresh (every 60 seconds)
                this.refreshInterval = setInterval(() => {
                    this.fetchStats();
                    this.fetchRecentRequests();
                    this.fetchPendingVerifications();
                }, 60000);
            },
            beforeDestroy() {
                // Clean up interval when component is destroyed
                if (this.refreshInterval) {
                    clearInterval(this.refreshInterval);
                }
            }
        });
    }
    
    // Initialize service management Vue app if it exists
    if (document.getElementById('service-management')) {
        new Vue({
            el: '#service-management',
            delimiters: ['${', '}'],
            data: {
                services: [],
                loading: false,
                editingService: null
            },
            methods: {
                // Fetch all services
                fetchServices() {
                    this.loading = true;
                    axios.get('/admin/api/services')
                        .then(response => {
                            this.services = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching services:', error);
                            this.loading = false;
                        });
                },
                
                // Begin editing a service
                editService(service) {
                    this.editingService = {...service};
                },
                
                // Toggle service active status
                toggleServiceActive(serviceId) {
                    const service = this.services.find(s => s.id === serviceId);
                    if (service) {
                        service.is_active = !service.is_active;
                        
                        axios.post(`/admin/service/toggle-active/${serviceId}`)
                            .then(response => {
                                this.showAlert('Service status updated successfully!', 'success');
                            })
                            .catch(error => {
                                console.error('Error toggling service status:', error);
                                this.showAlert('Failed to update service status', 'danger');
                                // Revert the change in the UI
                                service.is_active = !service.is_active;
                            });
                    }
                },
                
                // Show alert message
                showAlert(message, type = 'info') {
                    // Implementation would depend on how alerts are shown in the UI
                    console.log(`[${type}] ${message}`);
                }
            },
            created() {
                // Fetch initial data
                this.fetchServices();
            }
        });
    }
});

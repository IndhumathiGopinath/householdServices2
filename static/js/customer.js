/**
 * Customer-specific JavaScript
 * Handles functionality for customer-related pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize customer dashboard Vue app if it exists
    if (document.getElementById('customer-dashboard')) {
        new Vue({
            el: '#customer-dashboard',
            delimiters: ['${', '}'],
            data: {
                activeRequests: [],
                completedRequests: [],
                loading: false
            },
            methods: {
                // Fetch active service requests
                fetchActiveRequests() {
                    this.loading = true;
                    axios.get('/customer/api/active-requests')
                        .then(response => {
                            this.activeRequests = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching active requests:', error);
                            this.loading = false;
                        });
                },
                
                // Fetch completed service requests
                fetchCompletedRequests() {
                    axios.get('/customer/api/completed-requests')
                        .then(response => {
                            this.completedRequests = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching completed requests:', error);
                        });
                },
                
                // Cancel a service request
                cancelRequest(requestId) {
                    if (confirm('Are you sure you want to cancel this request?')) {
                        axios.post(`/customer/request/cancel/${requestId}`)
                            .then(response => {
                                // Update the request status in the UI
                                const request = this.activeRequests.find(r => r.id === requestId);
                                if (request) {
                                    request.status = 'cancelled';
                                }
                                
                                // Remove from active requests
                                this.activeRequests = this.activeRequests.filter(r => r.id !== requestId);
                                
                                // Show success message
                                this.showAlert('Request cancelled successfully!', 'success');
                            })
                            .catch(error => {
                                console.error('Error cancelling request:', error);
                                this.showAlert('Failed to cancel request', 'danger');
                            });
                    }
                },
                
                // Complete a service request
                completeRequest(requestId) {
                    axios.post(`/customer/request/complete/${requestId}`)
                        .then(response => {
                            // Update the request status in the UI
                            const request = this.activeRequests.find(r => r.id === requestId);
                            if (request) {
                                request.status = 'completed';
                            }
                            
                            // Remove from active requests
                            this.activeRequests = this.activeRequests.filter(r => r.id !== requestId);
                            
                            // Add to completed requests
                            this.fetchCompletedRequests();
                            
                            // Show success message
                            this.showAlert('Request completed successfully!', 'success');
                            
                            // Redirect to the review page
                            window.location.href = `/customer/request/review/${requestId}`;
                        })
                        .catch(error => {
                            console.error('Error completing request:', error);
                            this.showAlert('Failed to complete request', 'danger');
                        });
                },
                
                // Format date
                formatDate(dateString) {
                    const options = { year: 'numeric', month: 'long', day: 'numeric' };
                    return new Date(dateString).toLocaleDateString(undefined, options);
                },
                
                // Format time
                formatTime(timeString) {
                    const options = { hour: '2-digit', minute: '2-digit' };
                    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString(undefined, options);
                },
                
                // Show alert message
                showAlert(message, type = 'info') {
                    // Implementation would depend on how alerts are shown in the UI
                    console.log(`[${type}] ${message}`);
                }
            },
            created() {
                // Fetch initial data
                this.fetchActiveRequests();
                this.fetchCompletedRequests();
            }
        });
    }
    
    // Initialize service booking Vue app if it exists
    if (document.getElementById('book-service-app')) {
        new Vue({
            el: '#book-service-app',
            delimiters: ['${', '}'],
            data: {
                services: [],
                selectedService: null,
                loading: false,
                bookingData: {
                    service_id: '',
                    scheduled_date: '',
                    scheduled_time: '',
                    address: '',
                    pin_code: '',
                    description: ''
                }
            },
            methods: {
                // Fetch all active services
                fetchServices() {
                    this.loading = true;
                    axios.get('/service/api/list')
                        .then(response => {
                            this.services = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching services:', error);
                            this.loading = false;
                        });
                },
                
                // Update selected service
                updateSelectedService(serviceId) {
                    this.selectedService = this.services.find(s => s.id == serviceId) || null;
                    this.bookingData.service_id = serviceId;
                },
                
                // Submit booking form
                submitBooking() {
                    // Form validation would typically happen here
                    this.loading = true;
                    
                    axios.post('/customer/book-service', this.bookingData)
                        .then(response => {
                            this.loading = false;
                            this.showAlert('Service booked successfully!', 'success');
                            
                            // Redirect to requests page
                            window.location.href = '/customer/requests';
                        })
                        .catch(error => {
                            console.error('Error booking service:', error);
                            this.loading = false;
                            this.showAlert('Failed to book service', 'danger');
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
                this.fetchServices();
                
                // Initialize from form data if available
                const serviceSelect = document.getElementById('service_id');
                if (serviceSelect && serviceSelect.value) {
                    this.updateSelectedService(serviceSelect.value);
                }
            },
            mounted() {
                // Add event listener to service select field
                const serviceSelect = document.getElementById('service_id');
                if (serviceSelect) {
                    serviceSelect.addEventListener('change', (e) => {
                        this.updateSelectedService(e.target.value);
                    });
                }
            }
        });
    }
    
    // Initialize service review Vue app if it exists
    if (document.getElementById('review-service-app')) {
        new Vue({
            el: '#review-service-app',
            delimiters: ['${', '}'],
            data: {
                rating: 5,
                comment: '',
                requestId: null,
                loading: false
            },
            methods: {
                // Set rating
                setRating(value) {
                    this.rating = value;
                },
                
                // Submit review
                submitReview() {
                    this.loading = true;
                    
                    axios.post(`/customer/request/review/${this.requestId}`, {
                        rating: this.rating,
                        comment: this.comment
                    })
                        .then(response => {
                            this.loading = false;
                            this.showAlert('Review submitted successfully!', 'success');
                            
                            // Redirect to requests page
                            window.location.href = '/customer/requests';
                        })
                        .catch(error => {
                            console.error('Error submitting review:', error);
                            this.loading = false;
                            this.showAlert('Failed to submit review', 'danger');
                        });
                },
                
                // Show alert message
                showAlert(message, type = 'info') {
                    // Implementation would depend on how alerts are shown in the UI
                    console.log(`[${type}] ${message}`);
                }
            },
            created() {
                // Get request ID from URL if available
                const urlPath = window.location.pathname;
                const matches = urlPath.match(/\/request\/review\/(\d+)/);
                if (matches && matches[1]) {
                    this.requestId = matches[1];
                }
            }
        });
    }
});

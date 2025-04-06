/**
 * Professional-specific JavaScript
 * Handles functionality for professional-related pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize professional dashboard Vue app if it exists
    if (document.getElementById('professional-dashboard')) {
        new Vue({
            el: '#professional-dashboard',
            delimiters: ['${', '}'],
            data: {
                newRequests: [],
                acceptedRequests: [],
                completedRequests: [],
                reviews: [],
                avgRating: 0,
                isVerified: false,
                loading: false
            },
            methods: {
                // Fetch new service requests
                fetchNewRequests() {
                    this.loading = true;
                    axios.get('/professional/api/new-requests')
                        .then(response => {
                            this.newRequests = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching new requests:', error);
                            this.loading = false;
                        });
                },
                
                // Fetch accepted service requests
                fetchAcceptedRequests() {
                    axios.get('/professional/api/accepted-requests')
                        .then(response => {
                            this.acceptedRequests = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching accepted requests:', error);
                        });
                },
                
                // Fetch completed service requests
                fetchCompletedRequests() {
                    axios.get('/professional/api/completed-requests')
                        .then(response => {
                            this.completedRequests = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching completed requests:', error);
                        });
                },
                
                // Fetch reviews
                fetchReviews() {
                    axios.get('/professional/api/reviews')
                        .then(response => {
                            this.reviews = response.data.reviews;
                            this.avgRating = response.data.avg_rating;
                        })
                        .catch(error => {
                            console.error('Error fetching reviews:', error);
                        });
                },
                
                // Accept a service request
                acceptRequest(requestId) {
                    axios.post(`/professional/request/accept/${requestId}`)
                        .then(response => {
                            // Update the request status in the UI
                            const requestIndex = this.newRequests.findIndex(r => r.id === requestId);
                            if (requestIndex !== -1) {
                                const request = this.newRequests[requestIndex];
                                request.status = 'accepted';
                                
                                // Remove from new requests
                                this.newRequests.splice(requestIndex, 1);
                                
                                // Add to accepted requests
                                this.acceptedRequests.push(request);
                            }
                            
                            // Show success message
                            this.showAlert('Request accepted successfully!', 'success');
                        })
                        .catch(error => {
                            console.error('Error accepting request:', error);
                            this.showAlert('Failed to accept request', 'danger');
                        });
                },
                
                // Reject a service request
                rejectRequest(requestId) {
                    axios.post(`/professional/request/reject/${requestId}`)
                        .then(response => {
                            // Remove the request from the UI
                            this.newRequests = this.newRequests.filter(r => r.id !== requestId);
                            
                            // Show success message
                            this.showAlert('Request rejected successfully!', 'success');
                        })
                        .catch(error => {
                            console.error('Error rejecting request:', error);
                            this.showAlert('Failed to reject request', 'danger');
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
                },
                
                // Check verification status
                checkVerificationStatus() {
                    axios.get('/professional/api/profile')
                        .then(response => {
                            this.isVerified = response.data.is_verified;
                        })
                        .catch(error => {
                            console.error('Error checking verification status:', error);
                        });
                }
            },
            created() {
                // Fetch initial data
                this.checkVerificationStatus();
                this.fetchNewRequests();
                this.fetchAcceptedRequests();
                this.fetchCompletedRequests();
                this.fetchReviews();
            }
        });
    }
    
    // Initialize service requests Vue app if it exists
    if (document.getElementById('professional-requests')) {
        new Vue({
            el: '#professional-requests',
            delimiters: ['${', '}'],
            data: {
                assignedRequests: [],
                potentialRequests: [],
                loading: false,
                isVerified: false
            },
            methods: {
                // Fetch assigned service requests
                fetchAssignedRequests() {
                    this.loading = true;
                    axios.get('/professional/api/assigned-requests')
                        .then(response => {
                            this.assignedRequests = response.data;
                            this.loading = false;
                        })
                        .catch(error => {
                            console.error('Error fetching assigned requests:', error);
                            this.loading = false;
                        });
                },
                
                // Fetch potential service requests
                fetchPotentialRequests() {
                    axios.get('/professional/api/potential-requests')
                        .then(response => {
                            this.potentialRequests = response.data;
                        })
                        .catch(error => {
                            console.error('Error fetching potential requests:', error);
                        });
                },
                
                // Accept a service request
                acceptRequest(requestId) {
                    if (!this.isVerified) {
                        this.showAlert('Your profile must be verified before accepting requests.', 'warning');
                        return;
                    }
                    
                    axios.post(`/professional/request/accept/${requestId}`)
                        .then(response => {
                            // Update the UI
                            this.fetchAssignedRequests();
                            this.fetchPotentialRequests();
                            
                            // Show success message
                            this.showAlert('Request accepted successfully!', 'success');
                        })
                        .catch(error => {
                            console.error('Error accepting request:', error);
                            this.showAlert('Failed to accept request', 'danger');
                        });
                },
                
                // Reject a service request
                rejectRequest(requestId) {
                    axios.post(`/professional/request/reject/${requestId}`)
                        .then(response => {
                            // Update the UI
                            this.fetchAssignedRequests();
                            
                            // Show success message
                            this.showAlert('Request rejected successfully!', 'success');
                        })
                        .catch(error => {
                            console.error('Error rejecting request:', error);
                            this.showAlert('Failed to reject request', 'danger');
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
                },
                
                // Check verification status
                checkVerificationStatus() {
                    axios.get('/professional/api/profile')
                        .then(response => {
                            this.isVerified = response.data.is_verified;
                        })
                        .catch(error => {
                            console.error('Error checking verification status:', error);
                        });
                }
            },
            created() {
                // Fetch initial data
                this.checkVerificationStatus();
                this.fetchAssignedRequests();
                this.fetchPotentialRequests();
            }
        });
    }
});

/**
 * Main Vue application initializer
 * This script is responsible for initializing Vue components
 * that are used across the application.
 */

// Initialize Vue components when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if the Vue app container exists
    if (document.getElementById('vue-app')) {
        new Vue({
            el: '#vue-app',
            delimiters: ['${', '}'],
            data: {
                // Global application state
                services: [],
                professionals: [],
                loading: false,
                error: null
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
                            this.error = 'Failed to load services';
                            this.loading = false;
                        });
                },
                
                // Format price
                formatPrice(price) {
                    return '$' + parseFloat(price).toFixed(2);
                },
                
                // Format date
                formatDate(dateString) {
                    const options = { year: 'numeric', month: 'long', day: 'numeric' };
                    return new Date(dateString).toLocaleDateString(undefined, options);
                }
            },
            created() {
                // Fetch initial data when component is created
                this.fetchServices();
            }
        });
    }
});

// Service detail component
Vue.component('service-detail', {
    props: ['id'],
    delimiters: ['${', '}'],
    data() {
        return {
            service: null,
            loading: true,
            error: null
        };
    },
    template: `
        <div class="service-detail">
            <div v-if="loading" class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <div v-else-if="error" class="alert alert-danger" role="alert">
                ${ error }
            </div>
            <div v-else-if="service" class="card">
                <div class="card-body">
                    <h3 class="card-title">${ service.name }</h3>
                    <p class="card-text">${ service.description }</p>
                    <div class="d-flex justify-content-between">
                        <span><strong>Base Price:</strong> $${ service.base_price.toFixed(2) }</span>
                        <span><strong>Time Required:</strong> ${ service.time_required } mins</span>
                    </div>
                </div>
            </div>
        </div>
    `,
    mounted() {
        if (this.id) {
            this.fetchServiceDetails();
        }
    },
    methods: {
        fetchServiceDetails() {
            this.loading = true;
            axios.get(`/service/api/detail/${this.id}`)
                .then(response => {
                    this.service = response.data;
                    this.loading = false;
                })
                .catch(error => {
                    console.error('Error fetching service details:', error);
                    this.error = 'Failed to load service details';
                    this.loading = false;
                });
        }
    }
});

// Professional card component
Vue.component('professional-card', {
    props: ['professional'],
    delimiters: ['${', '}'],
    template: `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">${ professional.user.username }</h5>
                <div class="text-warning mb-2">
                    <template v-for="i in 5">
                        <i v-if="i <= Math.round(professional.avg_rating)" class="fas fa-star"></i>
                        <i v-else class="far fa-star"></i>
                    </template>
                    <span class="ms-1 text-muted">${ professional.avg_rating.toFixed(1) }</span>
                </div>
                <p class="card-text">${ professional.description }</p>
                <div class="d-flex justify-content-between mb-2">
                    <span><strong>Experience:</strong> ${ professional.experience } years</span>
                    <span><strong>Rate:</strong> $${ professional.hourly_rate }/hr</span>
                </div>
                <a :href="'/service/professional/' + professional.id" class="btn btn-outline-primary">View Profile</a>
            </div>
        </div>
    `
});

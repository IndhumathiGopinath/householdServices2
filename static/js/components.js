/**
 * Common components used across the application
 * This file registers Vue components that can be reused
 */

// Star Rating component
Vue.component('star-rating', {
    props: {
        rating: {
            type: Number,
            required: true
        },
        maxRating: {
            type: Number,
            default: 5
        },
        editable: {
            type: Boolean,
            default: false
        }
    },
    template: `
        <div class="star-rating">
            <span v-for="i in maxRating" :key="i" @click="setRating(i)" style="cursor: pointer;">
                <i v-if="i <= Math.round(rating)" class="fas fa-star text-warning"></i>
                <i v-else class="far fa-star text-warning"></i>
            </span>
            <span v-if="displayRating" class="ms-2 text-muted">({{ displayRating }})</span>
        </div>
    `,
    computed: {
        displayRating() {
            return this.rating ? this.rating.toFixed(1) : null;
        }
    },
    methods: {
        setRating(value) {
            if (this.editable) {
                this.$emit('rating-selected', value);
            }
        }
    }
});

// Status Badge component
Vue.component('status-badge', {
    props: {
        status: {
            type: String,
            required: true
        }
    },
    template: `
        <span class="badge" :class="badgeClass">{{ status }}</span>
    `,
    computed: {
        badgeClass() {
            const statusMap = {
                'pending': 'bg-warning',
                'assigned': 'bg-info',
                'accepted': 'bg-primary',
                'completed': 'bg-success',
                'cancelled': 'bg-danger',
                'rejected': 'bg-secondary'
            };
            return statusMap[this.status.toLowerCase()] || 'bg-secondary';
        }
    }
});

// Service Card component
Vue.component('service-card', {
    props: {
        service: {
            type: Object,
            required: true
        },
        showLink: {
            type: Boolean,
            default: true
        }
    },
    template: `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">{{ service.name }}</h5>
                <p class="card-text">{{ service.description }}</p>
                <div class="d-flex justify-content-between mb-2">
                    <span><strong>Base Price:</strong> ${{ service.base_price.toFixed(2) }}</span>
                    <span><strong>Time:</strong> {{ service.time_required }} mins</span>
                </div>
                <a v-if="showLink" :href="'/service/detail/' + service.id" class="btn btn-outline-primary">View Details</a>
            </div>
        </div>
    `
});

// Alert component
Vue.component('flash-alert', {
    props: {
        message: {
            type: String,
            required: true
        },
        type: {
            type: String,
            default: 'info'
        },
        dismissible: {
            type: Boolean,
            default: true
        },
        duration: {
            type: Number,
            default: 5000  // Auto-dismiss after 5 seconds
        }
    },
    template: `
        <div v-if="visible" class="alert" :class="'alert-' + type" role="alert">
            {{ message }}
            <button v-if="dismissible" type="button" class="btn-close" @click="dismiss" aria-label="Close"></button>
        </div>
    `,
    data() {
        return {
            visible: true,
            timeout: null
        };
    },
    mounted() {
        if (this.duration > 0) {
            this.timeout = setTimeout(() => {
                this.visible = false;
            }, this.duration);
        }
    },
    beforeDestroy() {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
    },
    methods: {
        dismiss() {
            this.visible = false;
        }
    }
});

// Loading Spinner component
Vue.component('loading-spinner', {
    props: {
        loading: {
            type: Boolean,
            default: false
        },
        size: {
            type: String,
            default: 'md'  // sm, md, lg
        },
        text: {
            type: String,
            default: 'Loading...'
        }
    },
    template: `
        <div v-if="loading" class="text-center my-3">
            <div class="spinner-border" :class="spinnerSize" role="status">
                <span class="visually-hidden">{{ text }}</span>
            </div>
            <div v-if="text" class="mt-2 text-muted">{{ text }}</div>
        </div>
    `,
    computed: {
        spinnerSize() {
            const sizes = {
                'sm': 'spinner-border-sm',
                'lg': 'spinner-border-lg'
            };
            return sizes[this.size] || '';
        }
    }
});

// Pagination component
Vue.component('pagination', {
    props: {
        currentPage: {
            type: Number,
            required: true
        },
        totalPages: {
            type: Number,
            required: true
        }
    },
    template: `
        <nav v-if="totalPages > 1" aria-label="Page navigation">
            <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Previous</a>
                </li>
                <li v-for="page in displayedPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                    <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
                </li>
            </ul>
        </nav>
    `,
    computed: {
        displayedPages() {
            // Show a maximum of 5 page numbers
            const pages = [];
            let startPage = Math.max(1, this.currentPage - 2);
            let endPage = Math.min(this.totalPages, startPage + 4);
            
            // Adjust start page if end page is maxed out
            startPage = Math.max(1, endPage - 4);
            
            for (let i = startPage; i <= endPage; i++) {
                pages.push(i);
            }
            
            return pages;
        }
    },
    methods: {
        changePage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.$emit('page-changed', page);
            }
        }
    }
});

// Search Input component
Vue.component('search-input', {
    props: {
        placeholder: {
            type: String,
            default: 'Search...'
        },
        value: {
            type: String,
            default: ''
        }
    },
    template: `
        <div class="search-input">
            <div class="input-group">
                <input 
                    type="text" 
                    class="form-control" 
                    :placeholder="placeholder"
                    :value="value"
                    @input="$emit('input', $event.target.value)"
                    @keyup.enter="$emit('search')"
                >
                <button class="btn btn-primary" type="button" @click="$emit('search')">
                    <i class="fas fa-search"></i>
                </button>
            </div>
        </div>
    `
});

// Empty State component
Vue.component('empty-state', {
    props: {
        text: {
            type: String,
            default: 'No items found'
        },
        icon: {
            type: String,
            default: 'fas fa-info-circle'
        },
        actionText: {
            type: String,
            default: null
        },
        actionLink: {
            type: String,
            default: null
        }
    },
    template: `
        <div class="text-center py-5">
            <div class="mb-3">
                <i :class="icon + ' fa-3x text-muted'"></i>
            </div>
            <h5 class="text-muted">{{ text }}</h5>
            <a v-if="actionText && actionLink" :href="actionLink" class="btn btn-primary mt-3">
                {{ actionText }}
            </a>
        </div>
    `
});

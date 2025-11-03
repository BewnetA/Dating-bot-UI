// API Configuration
const API_BASE_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken');

// Pagination settings
const PAGINATION_CONFIG = {
    users: {
        currentPage: 1,
        itemsPerPage: 10,
        totalItems: 0,
        searchTerm: '',
        currentData: []
    },
    payments: {
        currentPage: 1,
        itemsPerPage: 10,
        totalItems: 0,
        statusFilter: 'all',
        currentData: []
    },
    complaints: {
        currentPage: 1,
        itemsPerPage: 10,
        totalItems: 0,
        statusFilter: 'all',
        currentData: []
    }
};

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(url, config);
        
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Authentication check
function checkAuth() {
    const isAuthenticated = localStorage.getItem('adminAuthenticated');
    if (!isAuthenticated || isAuthenticated !== 'true') {
        window.location.href = 'login.html';
        return false;
    }
    
    authToken = localStorage.getItem('authToken');
    if (!authToken) {
        window.location.href = 'login.html';
        return false;
    }
    
    return true;
}

// Main application
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    
    initDashboard();
    setupEventListeners();
    
    // Initialize with saved theme
    const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    document.getElementById('themeSwitch').checked = savedTheme === 'dark';
});

function setupEventListeners() {
    // Date filter listeners
    document.querySelectorAll('.date-filter').forEach(item => {
        item.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            applyDateFilter(range);
        });
    });
    
    // Chart filter listeners
    document.querySelectorAll('.chart-filter').forEach(item => {
        item.addEventListener('click', function() {
            const chart = this.getAttribute('data-chart');
            const range = this.getAttribute('data-range');
            filterChart(chart, range);
            
            const dropdownBtn = this.closest('.dropdown').querySelector('.dropdown-toggle');
            dropdownBtn.innerHTML = `<i class="fas fa-filter me-1"></i>${this.textContent}`;
        });
    });
    
    // Payment filter listeners
    document.querySelectorAll('.payment-filter').forEach(item => {
        item.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            PAGINATION_CONFIG.payments.statusFilter = status;
            PAGINATION_CONFIG.payments.currentPage = 1;
            loadPayments();
            
            const dropdownBtn = this.closest('.dropdown').querySelector('.dropdown-toggle');
            dropdownBtn.innerHTML = `<i class="fas fa-filter me-1"></i>${this.textContent}`;
        });
    });
    
    // Complaint filter listeners
    document.querySelectorAll('.complaint-filter').forEach(item => {
        item.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            PAGINATION_CONFIG.complaints.statusFilter = status;
            PAGINATION_CONFIG.complaints.currentPage = 1;
            loadComplaints();
            
            const dropdownBtn = this.closest('.dropdown').querySelector('.dropdown-toggle');
            dropdownBtn.innerHTML = `<i class="fas fa-filter me-1"></i>${this.textContent}`;
        });
    });
    
    // Theme switcher
    document.getElementById('themeSwitch').addEventListener('change', function() {
        toggleTheme(this.checked);
    });
    
    // User search
    document.getElementById('user-search').addEventListener('input', function() {
        PAGINATION_CONFIG.users.searchTerm = this.value;
        PAGINATION_CONFIG.users.currentPage = 1;
        loadUsers();
    });
    
    document.getElementById('search-users-btn').addEventListener('click', function() {
        const searchTerm = document.getElementById('user-search').value;
        PAGINATION_CONFIG.users.searchTerm = searchTerm;
        PAGINATION_CONFIG.users.currentPage = 1;
        loadUsers();
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.removeItem('adminAuthenticated');
        localStorage.removeItem('authToken');
        window.location.href = 'login.html';
    });
}

// Initialize dashboard with data
async function initDashboard() {
    try {
        await updateStats('last7');
        await loadUsers();
        await loadPayments();
        await loadComplaints();
        await renderCharts('last7');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

// Update statistics cards with period comparison
async function updateStats(dateRange) {
    try {
        const stats = await apiRequest(`/dashboard/stats?range_type=${dateRange}`);
        
        document.getElementById('total-users').textContent = stats.total_users.toLocaleString();
        document.getElementById('active-users').textContent = stats.active_users.toLocaleString();
        document.getElementById('total-matches').textContent = stats.total_matches.toLocaleString();
        document.getElementById('pending-payments').textContent = stats.pending_payments.toLocaleString();
        
        updateChangeIndicator('user-change', stats.user_growth);
        updateChangeIndicator('active-change', stats.active_growth);
        updateChangeIndicator('matches-change', stats.matches_growth);
        updateChangeIndicator('payments-change', stats.payments_growth);
        
        document.getElementById('current-date-range').textContent = 
            document.querySelector(`.date-filter[data-range="${dateRange}"]`).textContent;
    } catch (error) {
        console.error('Error updating stats:', error);
        showError('Failed to load statistics');
    }
}

// Update change indicator in stats cards
function updateChangeIndicator(elementId, change) {
    const element = document.getElementById(elementId);
    const isPositive = parseFloat(change) >= 0;
    
    element.innerHTML = `
        <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i> ${Math.abs(change)}%
    `;
    element.className = `text-${isPositive ? 'success' : 'danger'} me-2`;
}

// Apply date filter to dashboard
async function applyDateFilter(range) {
    try {
        await updateStats(range);
        await renderCharts(range);
    } catch (error) {
        console.error('Error applying date filter:', error);
        showError('Failed to filter data');
    }
}

// Filter chart data
async function filterChart(chartType, range) {
    if (chartType === 'gender') {
        await renderGenderChart(range);
    } else if (chartType === 'registrations') {
        await renderRegistrationChart(range);
    }
}

// Toggle between light and dark themes
function toggleTheme(isDark) {
    const theme = isDark ? 'dark' : 'light';
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    renderCharts();
}

// Load users with pagination
async function loadUsers() {
    try {
        const config = PAGINATION_CONFIG.users;
        const skip = (config.currentPage - 1) * config.itemsPerPage;
        
        let endpoint = `/users?skip=${skip}&limit=${config.itemsPerPage}`;
        if (config.searchTerm) {
            endpoint += `&search=${encodeURIComponent(config.searchTerm)}`;
        }
        
        const users = await apiRequest(endpoint);
        config.currentData = users;
        
        // For demo, if API doesn't return total count, estimate it
        config.totalItems = users.length < config.itemsPerPage ? 
            skip + users.length : 
            skip + users.length + 1; // Estimate there might be more
        
        renderUsersTable(users);
        renderPagination('users', config);
        updatePaginationInfo('users', config, users.length);
    } catch (error) {
        console.error('Error loading users:', error);
        showError('Failed to load users');
    }
}

// Render users table
function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="8" class="text-center text-muted py-4">No users found</td>`;
        tbody.appendChild(row);
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.user_id}</td>
            <td>${user.username}</td>
            <td>${user.first_name} ${user.last_name || ''}</td>
            <td>${user.gender || 'Not set'}</td>
            <td>${user.city || 'Not set'}</td>
            <td>${user.coins}</td>
            <td><span class="badge ${user.is_active ? 'badge-active' : 'badge-inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load payments with pagination
async function loadPayments() {
    try {
        const config = PAGINATION_CONFIG.payments;
        const skip = (config.currentPage - 1) * config.itemsPerPage;
        
        let endpoint = `/payments?skip=${skip}&limit=${config.itemsPerPage}`;
        if (config.statusFilter !== 'all') {
            endpoint += `&status_filter=${config.statusFilter}`;
        }
        
        const payments = await apiRequest(endpoint);
        config.currentData = payments;
        config.totalItems = payments.length < config.itemsPerPage ? 
            skip + payments.length : 
            skip + payments.length + 1;
        
        renderPaymentsTable(payments);
        renderPagination('payments', config);
        updatePaginationInfo('payments', config, payments.length);
    } catch (error) {
        console.error('Error loading payments:', error);
        showError('Failed to load payments');
    }
}

// Render payments table
function renderPaymentsTable(payments) {
    const tbody = document.getElementById('payments-table-body');
    tbody.innerHTML = '';
    
    if (payments.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="7" class="text-center text-muted py-4">No payments found</td>`;
        tbody.appendChild(row);
        return;
    }
    
    payments.forEach(payment => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${payment._id}</td>
            <td>${payment.first_name || 'N/A'} (${payment.username || 'N/A'})</td>
            <td>${payment.package_name}</td>
            <td>${payment.coins_amount}</td>
            <td>$${payment.price}</td>
            <td><span class="badge badge-${payment.status}">${payment.status}</span></td>
            <td>${new Date(payment.created_at).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load complaints with pagination
async function loadComplaints() {
    try {
        const config = PAGINATION_CONFIG.complaints;
        const skip = (config.currentPage - 1) * config.itemsPerPage;
        
        let endpoint = `/complaints?skip=${skip}&limit=${config.itemsPerPage}`;
        if (config.statusFilter !== 'all') {
            endpoint += `&status_filter=${config.statusFilter}`;
        }
        
        const complaints = await apiRequest(endpoint);
        config.currentData = complaints;
        config.totalItems = complaints.length < config.itemsPerPage ? 
            skip + complaints.length : 
            skip + complaints.length + 1;
        
        renderComplaintsTable(complaints);
        renderPagination('complaints', config);
        updatePaginationInfo('complaints', config, complaints.length);
    } catch (error) {
        console.error('Error loading complaints:', error);
        showError('Failed to load complaints');
    }
}

// Render complaints table
function renderComplaintsTable(complaints) {
    const tbody = document.getElementById('complaints-table-body');
    tbody.innerHTML = '';
    
    if (complaints.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" class="text-center text-muted py-4">No complaints found</td>`;
        tbody.appendChild(row);
        return;
    }
    
    complaints.forEach(complaint => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${complaint._id}</td>
            <td>${complaint.user_id}</td>
            <td>${complaint.complaint_type}</td>
            <td>${complaint.reported_user_id || 'N/A'}</td>
            <td><span class="badge badge-${complaint.status}">${complaint.status}</span></td>
            <td>${new Date(complaint.created_at).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Render pagination
function renderPagination(type, config) {
    const paginationElement = document.getElementById(`${type}-pagination`);
    const totalPages = Math.ceil(config.totalItems / config.itemsPerPage);
    
    if (totalPages <= 1) {
        paginationElement.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${config.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${config.currentPage - 1}">Previous</a>
        </li>
    `;
    
    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, config.currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === config.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${config.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${config.currentPage + 1}">Next</a>
        </li>
    `;
    
    paginationElement.innerHTML = paginationHTML;
    
    // Add event listeners to pagination buttons
    paginationElement.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = parseInt(this.getAttribute('data-page'));
            if (page && page !== config.currentPage) {
                config.currentPage = page;
                if (type === 'users') loadUsers();
                else if (type === 'payments') loadPayments();
                else if (type === 'complaints') loadComplaints();
            }
        });
    });
}

// Update pagination info text
function updatePaginationInfo(type, config, currentCount) {
    const start = ((config.currentPage - 1) * config.itemsPerPage) + 1;
    const end = start + currentCount - 1;
    
    document.getElementById(`${type}-start`).textContent = start;
    document.getElementById(`${type}-end`).textContent = end;
    document.getElementById(`${type}-total`).textContent = config.totalItems;
}

// Render charts
async function renderCharts(dateRange = 'last7') {
    await renderGenderChart(dateRange);
    await renderRegistrationChart(dateRange);
}

// Render gender distribution chart
async function renderGenderChart(dateRange = 'all') {
    try {
        const data = await apiRequest('/charts/gender-distribution');
        
        const genderCtx = document.getElementById('genderChart').getContext('2d');
        
        if (window.genderChart instanceof Chart) {
            window.genderChart.destroy();
        }
        
        window.genderChart = new Chart(genderCtx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'],
                    hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617'],
                    hoverBorderColor: getComputedStyle(document.body).getPropertyValue('--bg-color'),
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: getComputedStyle(document.body).getPropertyValue('--text-color')
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error rendering gender chart:', error);
    }
}

// Render registration chart
async function renderRegistrationChart(dateRange = 'last7') {
    try {
        const days = dateRange === 'last30' ? 30 : dateRange === 'last90' ? 90 : 7;
        const data = await apiRequest(`/charts/registrations?days=${days}`);
        
        const regCtx = document.getElementById('registrationChart').getContext('2d');
        
        if (window.registrationChart instanceof Chart) {
            window.registrationChart.destroy();
        }
        
        window.registrationChart = new Chart(regCtx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Registrations",
                    backgroundColor: "#4e73df",
                    hoverBackgroundColor: "#2e59d9",
                    borderColor: "#4e73df",
                    data: data.data,
                }],
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            color: getComputedStyle(document.body).getPropertyValue('--text-color')
                        },
                        grid: {
                            color: getComputedStyle(document.body).getPropertyValue('--border-color')
                        }
                    },
                    x: {
                        ticks: {
                            color: getComputedStyle(document.body).getPropertyValue('--text-color')
                        },
                        grid: {
                            color: getComputedStyle(document.body).getPropertyValue('--border-color')
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.body).getPropertyValue('--text-color')
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error rendering registration chart:', error);
    }
}

// Utility function to show error messages
function showError(message) {
    console.error('Error:', message);
    // You can implement a toast notification here
}
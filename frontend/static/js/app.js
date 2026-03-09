// Placement Portal - Vue 3 SPA
const API = '';

const { createApp } = Vue;

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            // UI state
            sidebarOpen: false,
            darkMode: localStorage.getItem('ppa_darkmode') === '1',

            // Auth
            currentPage: 'login',
            isLoggedIn: false,
            token: localStorage.getItem('ppa_token') || '',
            user: JSON.parse(localStorage.getItem('ppa_user') || '{}'),
            loading: false,
            alert: { show: false, type: 'success', message: '' },

            // Notifications
            notifications: [],
            unreadNotifications: 0,

            // Login/Register forms
            loginTab: 'login',
            loginForm: { email: '', password: '' },
            sRegForm: { full_name: '', email: '', password: '', department: '', cgpa: '', graduation_year: '', phone: '' },
            cRegForm: { company_name: '', email: '', password: '', hr_name: '', hr_phone: '', website: '', industry: '', description: '' },

            // Admin
            adminStats: {},
            adminApplications: [],
            adminAppStatusFilter: '',
            pendingCompanies: [],
            pendingDrives: [],
            companies: [],
            adminDrives: [],
            students: [],
            reports: [],
            searchQuery: '',
            driveStatusFilter: '',
            selectedAdminDrive: null,
            adminDriveApplications: [],

            // Company
            companyProfile: null,
            companyDashboard: {},
            companyDrives: [],
            driveApplications: [],
            driveInterviews: [],
            showDriveForm: false,
            editingDriveId: null,
            driveForm: { drive_name: '', job_title: '', job_description: '', eligibility_branch: '', min_cgpa: '', eligible_year: '', application_deadline: '', location: '', salary: '', job_type: 'Full-time' },
            companyProfileForm: {},

            // Student
            studentProfile: null,
            approvedDrives: [],
            myApplications: [],
            placementHistory: [],
            myInterviews: [],
            atsResult: null,
            atsLoading: false,
            studentProfileForm: {},
            skillsInput: '',
            driveSearch: '',
            branchFilter: '',
            selectedDrive: null,

            // Interview
            interviewForm: { interview_date: '', mode: 'Online', venue: '' },
            interviewAppId: null,

            // Lists
            departments: ['CSE', 'ECE', 'EEE', 'ME', 'CE', 'IT', 'BT', 'CHE'],
            adminStatCards: {
                total_students: { label: 'Total Students', icon: 'bi bi-people text-primary', class: '' },
                total_companies: { label: 'Total Companies', icon: 'bi bi-building text-success', class: '' },
                total_drives: { label: 'Total Drives', icon: 'bi bi-briefcase text-warning', class: '' },
                total_applications: { label: 'Applications', icon: 'bi bi-file-earmark-text text-info', class: '' },
                selected_students: { label: 'Selections', icon: 'bi bi-trophy text-danger', class: '' },
                pending_companies: { label: 'Pending Companies', icon: 'bi bi-hourglass text-secondary', class: '' },
                pending_drives: { label: 'Pending Drives', icon: 'bi bi-clock text-dark', class: '' },
                blacklisted_users: { label: 'Blacklisted', icon: 'bi bi-shield-x text-danger', class: '' },
            },


        };
    },
    computed: {
        pageTitle() {
            const titles = {
                'dashboard': 'Dashboard',
                'admin-companies': 'Companies',
                'admin-drives': 'Placement Drives',
                'admin-drive-detail': 'Drive Details',
                'admin-students': 'Students',
                'admin-applications': 'Applications',
                'admin-reports': 'Reports',
                'company-drives': 'My Drives',
                'company-profile': 'Company Profile',
                'company-drive-applications': 'Drive Applications',
                'student-drives': 'Browse Drives',
                'student-drive-detail': 'Drive Details',
                'student-applications': 'My Applications',
                'student-interviews': 'Interviews',
                'student-history': 'Placement History',
                'student-profile': 'My Profile',
            };
            return titles[this.currentPage] || 'Placement Portal';
        }
    },
    methods: {
        // toggle dark/light
        toggleTheme() {
            this.darkMode = !this.darkMode;
            document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light');
            localStorage.setItem('ppa_darkmode', this.darkMode ? '1' : '0');
        },

        // api helper
        async api(url, method = 'GET', body = null) {
            const opts = {
                method,
                headers: {},
            };
            if (this.token) opts.headers['Authorization'] = `Bearer ${this.token}`;
            if (body) {
                opts.headers['Content-Type'] = 'application/json';
                opts.body = JSON.stringify(body);
            }

            try {
                const res = await fetch(API + url, opts);
                const contentType = res.headers.get('content-type') || '';
                if (!contentType.includes('application/json')) {
                    if (!res.ok) {
                        this.showAlert('Request failed (non-JSON response)', 'danger');
                        return null;
                    }
                    // non-JSON success (shouldn't happen for API calls, but handle gracefully)
                    return { message: 'OK' };
                }
                let data;
                try {
                    data = await res.json();
                } catch (parseErr) {
                    this.showAlert('Invalid response from server', 'danger');
                    return null;
                }
                if (!res.ok) {
                    this.showAlert(data.error || 'Request failed', 'danger');
                    return null;
                }
                return data;
            } catch (e) {
                this.showAlert('Network error: ' + e.message, 'danger');
                return null;
            }
        },

        showAlert(message, type = 'success') {
            this.alert = { show: true, type, message };
            setTimeout(() => { this.alert.show = false; }, 4000);
        },

        formatDate(d) {
            if (!d) return '-';
            return new Date(d).toLocaleDateString() + ' ' + new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        },

        statusBadge(status) {
            const m = { pending: 'badge bg-warning text-dark', approved: 'badge bg-success', rejected: 'badge bg-danger', closed: 'badge bg-secondary', applied: 'badge bg-primary', shortlisted: 'badge bg-info', selected: 'badge bg-success', withdrawn: 'badge bg-dark' };
            return m[status] || 'badge bg-secondary';
        },

        // navigation
        navigate(page) {
            this.currentPage = page;
            this.loadPageData(page);
        },

        // form validation
        validateForm(event) {
            const form = event.target;
            if (!form.checkValidity()) {
                event.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            form.classList.add('was-validated');
            return true;
        },

        // chart rendering
        renderAdminCharts() {
            if (typeof Chart === 'undefined') return;
            // Application Status Doughnut
            const appCtx = document.getElementById('appStatusChart');
            if (appCtx && this.adminStats.chart_app_status) {
                if (this._appChart) this._appChart.destroy();
                const d = this.adminStats.chart_app_status;
                this._appChart = new Chart(appCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Applied', 'Shortlisted', 'Selected', 'Rejected', 'Withdrawn'],
                        datasets: [{ data: [d.applied, d.shortlisted, d.selected, d.rejected, d.withdrawn], backgroundColor: ['#0d6efd', '#0dcaf0', '#198754', '#dc3545', '#6c757d'] }]
                    },
                    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
                });
            }
            // Drive Status Bar
            const driveCtx = document.getElementById('driveStatusChart');
            if (driveCtx && this.adminStats.chart_drive_status) {
                if (this._driveChart) this._driveChart.destroy();
                const d = this.adminStats.chart_drive_status;
                this._driveChart = new Chart(driveCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Pending', 'Approved', 'Rejected', 'Closed'],

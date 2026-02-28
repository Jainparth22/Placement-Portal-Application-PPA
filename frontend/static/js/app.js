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

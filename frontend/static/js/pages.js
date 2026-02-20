// page components

const LoginPage = {
    template: `
    <div class="login-page">
        <div class="container">
            <div class="row justify-content-center align-items-center min-vh-100">
                <div class="col-md-5">
                    <div class="card shadow-lg border-0 rounded-4">
                        <div class="card-body p-5">
                            <div class="text-center mb-4">
                                <i class="bi bi-mortarboard-fill text-primary" style="font-size:3rem;"></i>
                                <h2 class="fw-bold mt-2">Placement Portal</h2>
                                <p class="text-muted">Sign in to your account</p>
                            </div>
                            <ul class="nav nav-pills nav-fill mb-4">
                                <li class="nav-item"><a class="nav-link" :class="{active:tab==='login'}" href="#" @click.prevent="tab='login'">Login</a></li>
                                <li class="nav-item"><a class="nav-link" :class="{active:tab==='reg-student'}" href="#" @click.prevent="tab='reg-student'">Student</a></li>

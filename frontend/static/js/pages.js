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
                                <li class="nav-item"><a class="nav-link" :class="{active:tab==='reg-company'}" href="#" @click.prevent="tab='reg-company'">Company</a></li>
                            </ul>
                            <form v-if="tab==='login'" @submit.prevent="$emit('login',loginForm)">
                                <div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control" v-model="loginForm.email" required></div>
                                <div class="mb-3"><label class="form-label">Password</label><input type="password" class="form-control" v-model="loginForm.password" required></div>
                                <button type="submit" class="btn btn-primary w-100"><i class="bi bi-box-arrow-in-right me-1"></i>Login</button>
                            </form>
                            <form v-if="tab==='reg-student'" @submit.prevent="$emit('register-student',sForm)">
                                <div class="row"><div class="col-md-6 mb-3"><label class="form-label">Full Name *</label><input type="text" class="form-control" v-model="sForm.full_name" required></div><div class="col-md-6 mb-3"><label class="form-label">Email *</label><input type="email" class="form-control" v-model="sForm.email" required></div></div>
                                <div class="mb-3"><label class="form-label">Password *</label><input type="password" class="form-control" v-model="sForm.password" required minlength="6"></div>
                                <div class="row"><div class="col-md-4 mb-3"><label class="form-label">Department</label><select class="form-select" v-model="sForm.department"><option value="">Select</option><option v-for="d in depts" :value="d">{{d}}</option></select></div><div class="col-md-4 mb-3"><label class="form-label">CGPA</label><input type="number" class="form-control" v-model="sForm.cgpa" step="0.01" min="0" max="10"></div><div class="col-md-4 mb-3"><label class="form-label">Grad Year</label><input type="number" class="form-control" v-model="sForm.graduation_year" min="2020" max="2030"></div></div>
                                <div class="mb-3"><label class="form-label">Phone</label><input type="tel" class="form-control" v-model="sForm.phone"></div>
                                <button type="submit" class="btn btn-success w-100"><i class="bi bi-person-plus me-1"></i>Register</button>
                            </form>
                            <form v-if="tab==='reg-company'" @submit.prevent="$emit('register-company',cForm)">
                                <div class="mb-3"><label class="form-label">Company Name *</label><input type="text" class="form-control" v-model="cForm.company_name" required></div>
                                <div class="row"><div class="col-md-6 mb-3"><label class="form-label">Email *</label><input type="email" class="form-control" v-model="cForm.email" required></div><div class="col-md-6 mb-3"><label class="form-label">Password *</label><input type="password" class="form-control" v-model="cForm.password" required minlength="6"></div></div>
                                <div class="row"><div class="col-md-6 mb-3"><label class="form-label">HR Name</label><input type="text" class="form-control" v-model="cForm.hr_name"></div><div class="col-md-6 mb-3"><label class="form-label">Industry</label><input type="text" class="form-control" v-model="cForm.industry"></div></div>
                                <div class="row"><div class="col-md-6 mb-3"><label class="form-label">Website</label><input type="url" class="form-control" v-model="cForm.website"></div><div class="col-md-6 mb-3"><label class="form-label">HR Phone</label><input type="tel" class="form-control" v-model="cForm.hr_phone"></div></div>
                                <div class="mb-3"><label class="form-label">Description</label><textarea class="form-control" v-model="cForm.description" rows="2"></textarea></div>
                                <button type="submit" class="btn btn-primary w-100"><i class="bi bi-building-add me-1"></i>Register</button>
                            </form>
                        </div>
                    </div>
                </div>

const AuthManager = {
    auth: null,
    db: null,
    provider: null,
    
    init() {
        const fb = initFirebase();
        this.auth = fb.auth;
        this.db = fb.db;
        this.provider = fb.googleProvider;
        this.provider.setCustomParameters({prompt: 'select_account'});
        
        this.auth.onAuthStateChanged(user => {
            const isAdmin = user && user.email === APP_CONFIG.adminEmail;
            if (user) {
                sessionStorage.setItem('user_email', user.email);
                sessionStorage.setItem('is_admin', isAdmin ? 'true' : 'false');
            } else {
                sessionStorage.removeItem('user_email');
                sessionStorage.removeItem('is_admin');
            }
            this.handleRedirect(user, isAdmin);
            window.dispatchEvent(new CustomEvent('authChange', {detail: {user, isAdmin}}));
        });
        return this;
    },
    
    async login() {
        try {
            const result = await this.auth.signInWithPopup(this.provider);
            return {success: true, user: result.user};
        } catch(e) {
            if (e.code === 'auth/popup-blocked') {
                await this.auth.signInWithRedirect(this.provider);
                return {success: true, redirecting: true};
            }
            return {success: false, error: e.message};
        }
    },
    
    async logout() {
        try {
            await this.auth.signOut();
            sessionStorage.clear();
            return {success: true};
        } catch(e) {
            return {success: false, error: e.message};
        }
    },
    
    isAdmin() {
        return sessionStorage.getItem('is_admin') === 'true';
    },
    
    handleRedirect(user, isAdmin) {
        const currentPage = window.location.pathname.split('/').pop();
        if (currentPage === 'admin.html' && !isAdmin) {
            window.location.href = 'index.html?error=not_admin';
        }
    },
    
    log(action, detail) {
        const logs = JSON.parse(localStorage.getItem('audit_logs') || '[]');
        logs.push({action, detail: detail || '', user: this.auth?.currentUser?.email || 'guest', time: new Date().toISOString()});
        if (logs.length > 200) logs.shift();
        localStorage.setItem('audit_logs', JSON.stringify(logs));
    }
};

const Auth = AuthManager.init();

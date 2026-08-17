const GitHubManager = {
    config: JSON.parse(localStorage.getItem('github_config') || '{"token":"","owner":"","repo":"","branch":"main","enabled":false}'),
    
    saveConfig(token, owner, repo, branch) {
        this.config = {token, owner, repo, branch: branch || 'main', enabled: true};
        localStorage.setItem('github_config', JSON.stringify(this.config));
        return this.config;
    },
    
    async testConnection() {
        if (!this.config.enabled) return {success: false, message: 'Belum dikonfigurasi'};
        try {
            const res = await fetch('https://api.github.com/user', {
                headers: {'Authorization': 'token ' + this.config.token}
            });
            if (res.ok) {
                const user = await res.json();
                return {success: true, message: 'Connected as @' + user.login};
            }
            return {success: false, message: 'Token invalid'};
        } catch(e) {
            return {success: false, message: e.message};
        }
    },
    
    async pushFile(filename, content, message) {
        if (!this.config.enabled) return {success: false, message: 'Belum dikonfigurasi'};
        try {
            const base64 = btoa(unescape(encodeURIComponent(content)));
            const headers = {
                'Authorization': 'token ' + this.config.token,
                'Content-Type': 'application/json'
            };
            const apiUrl = `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/contents/${filename}`;
            
            let sha = null;
            try {
                const getRes = await fetch(apiUrl + '?ref=' + this.config.branch, {headers});
                if (getRes.ok) { const data = await getRes.json(); sha = data.sha; }
            } catch(e) {}
            
            const body = {message: message || 'Update ' + filename, content: base64, branch: this.config.branch};
            if (sha) body.sha = sha;
            
            const pushRes = await fetch(apiUrl, {method: 'PUT', headers, body: JSON.stringify(body)});
            const result = await pushRes.json();
            
            if (pushRes.ok) return {success: true, commit: result.commit?.sha?.substring(0, 10)};
            return {success: false, message: result.message};
        } catch(e) {
            return {success: false, message: e.message};
        }
    },
    
    async getFile(filename) {
        if (!this.config.enabled) return null;
        try {
            const res = await fetch(
                `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/contents/${filename}`,
                {headers: {'Authorization': 'token ' + this.config.token}}
            );
            if (res.ok) {
                const data = await res.json();
                return decodeURIComponent(escape(atob(data.content)));
            }
            return null;
        } catch(e) { return null; }
    }
};

const GitHub = GitHubManager;

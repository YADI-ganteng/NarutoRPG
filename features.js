const FeatureManager = {
    features: JSON.parse(localStorage.getItem('yad_features') || '[]'),
    
    save() {
        localStorage.setItem('yad_features', JSON.stringify(this.features));
        this.broadcast();
    },
    
    add(feature) {
        if (!feature.name || !feature.code) return {success: false, message: 'Nama dan kode wajib!'};
        feature.id = 'feature_' + Date.now();
        feature.time = new Date().toISOString();
        feature.active = true;
        this.features.push(feature);
        this.save();
        this.applyFeature(feature);
        return {success: true, message: 'Fitur ditambahkan!'};
    },
    
    delete(featureId) {
        const feature = this.features.find(f => f.id === featureId);
        if (!feature) return {success: false};
        this.features = this.features.filter(f => f.id !== featureId);
        this.save();
        return {success: true};
    },
    
    toggle(featureId) {
        const feature = this.features.find(f => f.id === featureId);
        if (feature) { feature.active = !feature.active; this.save(); }
    },
    
    applyFeature(feature) {
        if (!feature.active) return;
        const wrapper = document.createElement('div');
        wrapper.setAttribute('data-feature', feature.name);
        wrapper.innerHTML = feature.code;
        document.body.appendChild(wrapper);
    },
    
    applyAll() {
        this.features.filter(f => f.active).forEach(f => this.applyFeature(f));
    },
    
    getAll() { return this.features; },
    
    broadcast() {
        localStorage.setItem('last_feature_update', Date.now());
    }
};

const Features = FeatureManager;

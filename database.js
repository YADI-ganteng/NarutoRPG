const StoreDB = {
    state: {
        orders: JSON.parse(localStorage.getItem('store_orders') || '[]'),
        payments: JSON.parse(localStorage.getItem('store_payments') || '[]'),
        products: {},
        categories: {},
        coupons: JSON.parse(localStorage.getItem('store_coupons') || '{}'),
        markup: parseInt(localStorage.getItem('store_markup') || '30'),
        favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
    },
    
    defaultProducts: {
        game: [
            {id: 'ml', name: 'Mobile Legends', icon: '👑', dev: 'Moonton', items: [['3 Diamonds', 1500], ['86 Diamonds', 20000]]},
            {id: 'ff', name: 'Free Fire', icon: '🔥', dev: 'Garena', items: [['5 Diamonds', 1500], ['355 Diamonds', 56000]]}
        ],
        pulsa: [
            {id: 'tsel', name: 'Telkomsel', icon: '📱', dev: 'Pulsa', items: [['5000', 6500], ['100000', 101500]]}
        ]
    },
    
    defaultCategories: {
        game: {name: 'Game', icon: '🎮'},
        pulsa: {name: 'Pulsa', icon: '📱'}
    },
    
    init() {
        this.loadProducts();
        return this;
    },
    
    loadProducts() {
        const saved = localStorage.getItem('yad_products');
        this.state.products = saved ? JSON.parse(saved) : {...this.defaultProducts};
        const savedMeta = localStorage.getItem('yad_category_meta');
        this.state.categories = savedMeta ? JSON.parse(savedMeta) : {...this.defaultCategories};
    },
    
    saveProducts() {
        localStorage.setItem('yad_products', JSON.stringify(this.state.products));
        localStorage.setItem('yad_category_meta', JSON.stringify(this.state.categories));
    },
    
    addOrder(order) {
        this.state.orders.unshift(order);
        localStorage.setItem('store_orders', JSON.stringify(this.state.orders));
        return order;
    },
    
    updateOrderStatus(id, status) {
        const order = this.state.orders.find(o => o.id === id);
        if (order) { order.status = status; localStorage.setItem('store_orders', JSON.stringify(this.state.orders)); return true; }
        return false;
    },
    
    getOrders(filter) {
        if (filter === 'pending') return this.state.orders.filter(o => o.status === 'pending');
        if (filter === 'done') return this.state.orders.filter(o => o.status === 'done');
        return this.state.orders;
    }
};

const DB = StoreDB.init();

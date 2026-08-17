const APP_CONFIG = {
    version: "3.0.0",
    adminEmail: 'ynuraini686@gmail.com',
    firebase: {
        apiKey: "AIzaSyAvfHxcAT2syVbrf6-TU0JBRXtNLI0AIkc",
        authDomain: "yadstores.firebaseapp.com",
        projectId: "yadstores",
        storageBucket: "yadstores.firebasestorage.app",
        messagingSenderId: "666352014774",
        appId: "1:666352014774:web:159ab5b455efb2fb2f9d17"
    }
};

function initFirebase() {
    if (!firebase.apps.length) {
        firebase.initializeApp(APP_CONFIG.firebase);
    }
    return {
        auth: firebase.auth(),
        db: firebase.firestore(),
        googleProvider: new firebase.auth.GoogleAuthProvider()
    };
}

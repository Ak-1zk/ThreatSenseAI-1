/**
 * Firebase Configuration — ThreatSense AI
 * Client-side Firebase config (these values are public by design).
 */

const firebaseConfig = {
    apiKey: "AIzaSyDWKcZbfIZc11o0bBAo7poMJ7-QZsOQcZM",
    authDomain: "chirp-club-and-hospitality.firebaseapp.com",
    projectId: "chirp-club-and-hospitality",
    storageBucket: "chirp-club-and-hospitality.firebasestorage.app",
    messagingSenderId: "882858878681",
    appId: "1:882858878681:web:d09a39292c828205f0c0c8",
};

// Initialize Firebase
const firebaseApp = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

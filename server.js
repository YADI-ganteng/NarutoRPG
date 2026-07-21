const express = require("express");
const admin = require("firebase-admin");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const serviceAccount = require("./service-account.json");

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: "https://yadstores-default-rtdb.asia-southeast1.firebasedatabase.app",
    storageBucket: "yadstores.firebasestorage.app"
});

const db = admin.firestore();
const app = express();

app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.static("public"));

app.get("/api/status", (req, res) => {
    res.json({ status: "online", project: serviceAccount.project_id, timestamp: new Date().toISOString(), firebase: true, version: "8.0.0" });
});

app.post("/api/deploy", async (req, res) => {
    try {
        const { html, message } = req.body;
        if (!html) return res.status(400).json({ error: "HTML required" });
        console.log(`📤 Deploy: ${html.length} bytes`);
        const docRef = await db.collection("deployments").add({
            html, message: message || "Yad AI Deploy", size: html.length,
            timestamp: admin.firestore.FieldValue.serverTimestamp(), deployed_by: "yad-ai-server"
        });
        console.log(`✅ Deployment: ${docRef.id}`);
        await db.collection("config").doc("latest").set({
            deployment_id: docRef.id, size: html.length,
            timestamp: admin.firestore.FieldValue.serverTimestamp(), version: "8.0.0"
        }, { merge: true });
        fs.writeFileSync("./public/index.html", html);
        console.log("✅ Saved to public/index.html");
        res.json({ success: true, deployment_id: docRef.id, size: html.length, timestamp: new Date().toISOString() });
    } catch(e) {
        console.error("Deploy error:", e);
        res.status(500).json({ error: e.message });
    }
});

app.get("/api/deployments", async (req, res) => {
    try {
        const snapshot = await db.collection("deployments").orderBy("timestamp", "desc").limit(10).get();
        const deployments = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            deployments.push({ id: doc.id, size: data.size, timestamp: data.timestamp ? data.timestamp.toDate() : null, message: data.message });
        });
        res.json({ deployments });
    } catch(e) { res.status(500).json({ error: e.message }); }
});

app.get("*", (req, res) => { res.sendFile(path.join(__dirname, "public", "index.html")); });

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Server: http://localhost:${PORT}`);
    console.log(`🔥 Firestore: ${serviceAccount.project_id}`);
});

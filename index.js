import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import path, { dirname, join } from "path";
import { fileURLToPath } from "url";
import { initializeApp } from "firebase/app";
import { getDatabase, ref, get, child } from "firebase/database";

dotenv.config();
const app = express();
const PORT = process.env.PORT || 3000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const firebaseConfig = {
    apiKey: "AIzaSyABEN2ZPgxw6n-uNGP6Y7t3z6TaKwca2iY",
    authDomain: "event-30a4b.firebaseapp.com",
    databaseURL: "https://event-30a4b-default-rtdb.firebaseio.com",
    projectId: "event-30a4b",
    storageBucket: "event-30a4b.appspot.com", 
    messagingSenderId: "610818410436",
    appId: "1:610818410436:web:70f72f289b1333affac691",
    measurementId: "G-YHPFF3QHFE"
};
const firebaseApp = initializeApp(firebaseConfig);
const db = getDatabase(firebaseApp);
app.use(express.static(join(__dirname, "assets")));
app.get("/", (req, res) => {
    res.sendFile(join(__dirname, "index.html"));
});

app.get("/events", async (req, res) => {
    console.log("GET /events called");
    try {
        const snapshot = await get(child(ref(db), "scrapedData"));
        if (snapshot.exists()) {
            const data = snapshot.val();
            const events = Object.values(data); 
            res.json(events);
        } else {
            res.status(404).json({ message: "No events found." });
        }
    } catch (error) {
        console.error("Error fetching data:", error.message);
        res.status(500).json({ error: error.message });
    }
});
const { exec } = require("child_process");

app.get("/scrape", (req, res) => {
  exec("python3 scrap.py", (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).send("Error running scraper");
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
    res.send("Scraping finished");
  });
});
app.listen(PORT, () => {
    console.log(`✅ Server running at http://localhost:${PORT}`);
});

import express from "express";
import pg from "pg";
import cron from "node-cron";
import { exec } from "child_process";

// Run the scraper every 24 hours (midnight)
cron.schedule("0 0 * * *", () => {
    console.log("Running scraper...");
    exec("python scraper.py", (error, stdout, stderr) => {
        if (error) {
            console.error(`Error running scraper: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Scraper stderr: ${stderr}`);
            return;
        }
        console.log(`Scraper output: ${stdout}`);
    });
});

const app = express();
const port = 3000;
const db = new pg.Client({
  user: "postgres",
  host: "localhost",
  database: "all_events",
  password: "root",
  port: 5432,
});
db.connect();
app.get("/", (req, res) => {
  res.sendFile("/web dev/mine/Assignments/assignment1/index.html");
});
app.get("/events", async (req, res) => {
    try {
      const result = await db.query("SELECT * FROM events ORDER BY date desc");
      res.json(result.rows);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
  });
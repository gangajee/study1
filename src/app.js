// src/app.js
import express from "express";
import pool from "./db.js";
const app = express();

app.use(express.json());

// 전체 목록 조회
app.get("/api", async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const offset = (page - 1) * limit;

    const [rows] = await pool.query(
      "SELECT * FROM exchange_rate ORDER BY collected_at DESC LIMIT ? OFFSET ?",
      [Number(limit), Number(offset)],
    );
    res.json({ data: rows, page: Number(page) });
  } catch (err) {
    next(err);
  }
});

// 단건 조회
app.get("/api/:id", async (req, res, next) => {
  try {
    const [rows] = await pool.query("SELECT * FROM exchange_rate WHERE id = ?", [
      req.params.id,
    ]);
    if (rows.length === 0) {
      return res.status(404).json({ error: "Not found" });
    }
    res.json(rows[0]);
  } catch (err) {
    next(err);
  }
});

// 전역 에러 핸들러
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});

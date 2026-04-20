const cors = require("cors");
const { env } = require("./env");

const allowedOrigins = [
  env.UI_URL,
  env.API_URL,
  "http://localhost:8000",
  "http://127.0.0.1:8000",
];

const corsPolicy = cors({
  origin: function (origin, callback) {
    // Allow requests with no origin (like Python service / curl / Postman)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
  },
  methods: ["GET", "POST", "PUT", "DELETE"],
  allowedHeaders: ["Content-Type", "Accept", "Origin", "X-CSRF-TOKEN", "x-csrf-token"],
  credentials: true,
});

module.exports = { corsPolicy };
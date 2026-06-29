require("dotenv").config();

const express = require("express");
const cors = require('cors')     

const app = express();

app.use(cors())  
app.use(express.json());

app.use("/api", require("./routes/upload"));
app.use('/api/auth', require('./routes/auth')) 

app.get("/health", (req, res) => {
  res.json({ status: "server is running" });
});

app.get("/", (req, res) => {
  res.json({
    message: "Welcome to AI Knowledge Assistant API",
    routes: {
      upload: "POST /api/upload",
      documents: "GET /api/documents",
      health: "GET /health",
      delete: 'DELETE /api/documents/:id',
      register: 'POST /api/auth/register',
      login: 'POST /api/auth/login'

    },
  });
});

app.use(require("./middleware/errorHandler"));

app.listen(process.env.PORT || 3000, () => {
  console.log(`server is running on port ${process.env.PORT || 3000}`);
});

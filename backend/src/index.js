const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const customSkillsRouter = require('./routes/customskills');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Backend API with Skills' });
});

app.use('/api/skills', customSkillsRouter);

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;

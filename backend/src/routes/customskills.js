const express = require('express');
const router = express.Router();
const customSkillsService = require('../../../skills/Back-End/customSkillsService');

// Get all available skills
router.get('/', (req, res) => {
  try {
    const skills = customSkillsService.getAllSkills();
    res.json(skills);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Execute a specific skill
router.post('/:skillId/execute', async (req, res) => {
  try {
    const { skillId } = req.params;
    const { data } = req.body;

    const result = await customSkillsService.executeSkill(skillId, data);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

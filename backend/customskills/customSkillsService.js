const skillRegistry = require('./skillRegistry');

class CustomSkillsService {
  constructor() {
    this.registry = skillRegistry;
  }

  getAllSkills() {
    return this.registry.getAll();
  }

  async executeSkill(skillId, data) {
    const skill = this.registry.get(skillId);

    if (!skill) {
      throw new Error(`Skill ${skillId} not found`);
    }

    try {
      const result = await skill.execute(data);
      return {
        success: true,
        skillId,
        result,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        skillId,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  registerSkill(skill) {
    return this.registry.register(skill);
  }

  removeSkill(skillId) {
    return this.registry.remove(skillId);
  }
}

module.exports = new CustomSkillsService();

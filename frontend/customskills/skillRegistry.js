class SkillRegistry {
  constructor() {
    this.skills = new Map();
    this.initializeDefaultSkills();
  }

  initializeDefaultSkills() {
    // Example skill: Data Formatter
    this.register({
      id: 'data-formatter',
      name: 'Data Formatter',
      description: 'Formats data for display',
      execute: async (data) => {
        return {
          formatted: JSON.stringify(data, null, 2),
          timestamp: new Date().toISOString()
        };
      }
    });

    // Example skill: Validation
    this.register({
      id: 'validator',
      name: 'Validator',
      description: 'Validates input data',
      execute: async (data) => {
        const isValid = data && Object.keys(data).length > 0;
        return {
          isValid,
          message: isValid ? 'Data is valid' : 'Data is invalid'
        };
      }
    });
  }

  register(skill) {
    if (!skill.id || !skill.name || !skill.execute) {
      throw new Error('Invalid skill: must have id, name, and execute function');
    }
    this.skills.set(skill.id, skill);
  }

  get(skillId) {
    return this.skills.get(skillId);
  }

  getAll() {
    return Array.from(this.skills.values());
  }

  remove(skillId) {
    return this.skills.delete(skillId);
  }
}

export const skillRegistry = new SkillRegistry();
export default SkillRegistry;

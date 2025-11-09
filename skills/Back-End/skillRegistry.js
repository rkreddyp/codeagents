class SkillRegistry {
  constructor() {
    this.skills = new Map();
    this.initializeDefaultSkills();
  }

  initializeDefaultSkills() {
    // Example skill: Data Processing
    this.register({
      id: 'data-processor',
      name: 'Data Processor',
      description: 'Processes and transforms data',
      execute: async (data) => {
        // Example: Transform data
        return {
          processed: true,
          original: data,
          transformed: {
            ...data,
            processedAt: new Date().toISOString(),
            status: 'completed'
          }
        };
      }
    });

    // Example skill: Analytics
    this.register({
      id: 'analytics',
      name: 'Analytics',
      description: 'Performs analytics on data',
      execute: async (data) => {
        return {
          analytics: {
            recordCount: Array.isArray(data) ? data.length : 1,
            type: typeof data,
            isEmpty: !data || Object.keys(data).length === 0,
            timestamp: new Date().toISOString()
          }
        };
      }
    });

    // Example skill: Email Notification (stub)
    this.register({
      id: 'email-notifier',
      name: 'Email Notifier',
      description: 'Sends email notifications',
      execute: async (data) => {
        // In production, this would integrate with an email service
        console.log('Email notification triggered:', data);
        return {
          sent: true,
          recipient: data.recipient || 'default@example.com',
          subject: data.subject || 'Notification',
          sentAt: new Date().toISOString()
        };
      }
    });
  }

  register(skill) {
    if (!skill.id || !skill.name || !skill.execute) {
      throw new Error('Invalid skill: must have id, name, and execute function');
    }
    this.skills.set(skill.id, skill);
    return true;
  }

  get(skillId) {
    return this.skills.get(skillId);
  }

  getAll() {
    return Array.from(this.skills.values()).map(skill => ({
      id: skill.id,
      name: skill.name,
      description: skill.description
    }));
  }

  remove(skillId) {
    return this.skills.delete(skillId);
  }
}

module.exports = new SkillRegistry();

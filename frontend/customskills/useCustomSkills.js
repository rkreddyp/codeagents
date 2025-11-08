import { useState, useEffect } from 'react';
import axios from 'axios';
import { skillRegistry } from './skillRegistry';

export const useCustomSkills = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load local skills from registry
    setSkills(skillRegistry.getAll());
  }, []);

  const executeSkill = async (skillId, data = {}) => {
    setLoading(true);
    try {
      const skill = skillRegistry.get(skillId);
      if (!skill) {
        throw new Error(`Skill ${skillId} not found`);
      }

      // Execute the skill locally or via backend API
      const result = await skill.execute(data);
      return result;
    } catch (error) {
      console.error('Error executing skill:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const executeBackendSkill = async (skillId, data = {}) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/customskills/${skillId}/execute`,
        { data }
      );
      return response.data;
    } catch (error) {
      console.error('Error executing backend skill:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    skills,
    executeSkill,
    executeBackendSkill,
    loading
  };
};

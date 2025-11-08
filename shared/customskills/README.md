# Shared CustomSkills

This directory contains shared customskills that can be used by both frontend and backend.

## Purpose

The shared customskills folder allows you to:
- Define common skill interfaces
- Share utility functions between frontend and backend
- Maintain consistent skill definitions across the application

## Usage

### Creating a Shared Skill

1. Create a new JavaScript/TypeScript file in this directory
2. Define the skill interface
3. Export the skill for use in both frontend and backend

### Example

```javascript
// shared/customskills/dateFormatter.js
module.exports = {
  id: 'date-formatter',
  name: 'Date Formatter',
  description: 'Formats dates consistently across the app',
  execute: (data) => {
    return new Date(data.date).toISOString();
  }
};
```

## Best Practices

1. Keep skills focused on a single responsibility
2. Document all skill parameters and return values
3. Handle errors gracefully
4. Write tests for shared skills

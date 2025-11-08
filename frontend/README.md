# Frontend Application

React-based frontend application with CustomSkills support.

## Structure

```
frontend/
├── src/
│   ├── index.js          # Application entry point
│   └── App.js            # Main application component
├── public/
│   └── index.html        # HTML template
├── customskills/
│   ├── useCustomSkills.js    # React hook for skills
│   └── skillRegistry.js      # Skill registration and management
└── package.json
```

## CustomSkills in Frontend

The frontend uses a React hook-based approach to manage customskills:

### useCustomSkills Hook

```javascript
import { useCustomSkills } from './customskills/useCustomSkills';

function MyComponent() {
  const { skills, executeSkill, executeBackendSkill, loading } = useCustomSkills();

  // Execute a frontend skill
  const result = await executeSkill('data-formatter', { data: 'test' });

  // Execute a backend skill via API
  const backendResult = await executeBackendSkill('data-processor', { data: 'test' });
}
```

### Available Methods

- `skills`: Array of all registered skills
- `executeSkill(skillId, data)`: Execute a frontend skill locally
- `executeBackendSkill(skillId, data)`: Execute a backend skill via API
- `loading`: Boolean indicating if a skill is executing

## Adding New Skills

Add skills to `customskills/skillRegistry.js`:

```javascript
skillRegistry.register({
  id: 'my-skill',
  name: 'My Skill',
  description: 'What this skill does',
  execute: async (data) => {
    // Your skill logic
    return { result: 'success' };
  }
});
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
REACT_APP_API_URL=http://localhost:3001
REACT_APP_ENV=development
```

## Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests

## Dependencies

- React 18
- Axios for API calls
- CustomSkills architecture

## Development

1. Install dependencies: `npm install`
2. Configure environment: `cp .env.example .env`
3. Start development server: `npm start`
4. Open http://localhost:3000

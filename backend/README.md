# Backend Application

Node.js/Express backend API with CustomSkills support.

## Structure

```
backend/
├── src/
│   ├── index.js                  # Application entry point
│   └── routes/
│       └── customskills.js       # CustomSkills API routes
├── customskills/
│   ├── customSkillsService.js    # Service layer for skills
│   └── skillRegistry.js          # Skill registration and management
└── package.json
```

## CustomSkills in Backend

The backend provides a service-based architecture for managing customskills:

### SkillRegistry

Manages all registered skills:

```javascript
const skillRegistry = require('./customskills/skillRegistry');

// Get all skills
const skills = skillRegistry.getAll();

// Get specific skill
const skill = skillRegistry.get('data-processor');

// Register new skill
skillRegistry.register({
  id: 'my-skill',
  name: 'My Skill',
  description: 'What this skill does',
  execute: async (data) => {
    return { result: 'success' };
  }
});
```

### CustomSkillsService

Handles skill execution with error handling:

```javascript
const customSkillsService = require('./customskills/customSkillsService');

// Execute a skill
const result = await customSkillsService.executeSkill('data-processor', {
  key: 'value'
});
```

## API Endpoints

### GET /api/customskills

Get all available skills.

**Response:**
```json
[
  {
    "id": "data-processor",
    "name": "Data Processor",
    "description": "Processes and transforms data"
  }
]
```

### POST /api/customskills/:skillId/execute

Execute a specific skill.

**Request:**
```json
{
  "data": {
    "key": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "skillId": "data-processor",
  "result": {
    "processed": true,
    "transformed": { ... }
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Built-in Skills

### data-processor
Processes and transforms data with timestamps.

### analytics
Performs analytics on provided data.

### email-notifier
Sends email notifications (stub implementation).

## Adding New Skills

Add skills to `customskills/skillRegistry.js`:

```javascript
this.register({
  id: 'my-backend-skill',
  name: 'My Backend Skill',
  description: 'Detailed description',
  execute: async (data) => {
    // Implement your skill logic
    return { result: 'processed' };
  }
});
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
```

## Scripts

- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests

## Dependencies

- Express - Web framework
- CORS - Cross-origin resource sharing
- dotenv - Environment variable management

## Development

1. Install dependencies: `npm install`
2. Configure environment: `cp .env.example .env`
3. Start development server: `npm run dev`
4. Server runs on http://localhost:3001

## Testing Skills

Using curl:
```bash
# Get all skills
curl http://localhost:3001/api/customskills

# Execute a skill
curl -X POST http://localhost:3001/api/customskills/data-processor/execute \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": "value"}}'
```

Using JavaScript:
```javascript
const response = await fetch('http://localhost:3001/api/customskills/data-processor/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: { test: 'value' } })
});
const result = await response.json();
```

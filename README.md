# Application with Skills

A full-stack application with frontend and backend, both utilizing a skills architecture for extensible functionality.

## Project Structure

```
.
├── frontend/              # React frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── package.json
├── backend/              # Node.js/Express backend API
│   ├── src/              # Source code
│   └── package.json
├── shared/               # Shared code and utilities
└── skills/               # Skills architecture (top level)
    ├── Front-End/        # Frontend skills
    ├── Back-End/         # Backend skills
    └── Shared/           # Shared skills
```

## Skills Architecture

This application uses a skills architecture that allows both frontend and backend to:
- Register modular, reusable functionality as "skills"
- Execute skills independently or via API calls
- Extend functionality without modifying core code
- Share common skills between frontend and backend

### How Skills Work

1. **Skill Registration**: Skills are registered in the skill registry with an ID, name, description, and execute function
2. **Skill Execution**: Skills can be executed locally or via API endpoints
3. **Extensibility**: New skills can be added without modifying existing code

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd codeagents
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
npm install
```

### Configuration

1. Backend configuration:
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

2. Frontend configuration:
```bash
cd frontend
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

1. Start the backend server:
```bash
cd backend
npm run dev
```
The backend will run on http://localhost:3001

2. Start the frontend development server:
```bash
cd frontend
npm start
```
The frontend will run on http://localhost:3000

## Skills Examples

### Frontend Skills

Located in `skills/Front-End/skillRegistry.js`:
- **data-formatter**: Formats data for display
- **validator**: Validates input data

### Backend Skills

Located in `skills/Back-End/skillRegistry.js`:
- **data-processor**: Processes and transforms data
- **analytics**: Performs analytics on data
- **email-notifier**: Sends email notifications

## Creating New Skills

### Frontend Skill

```javascript
// In skills/Front-End/skillRegistry.js
skillRegistry.register({
  id: 'my-custom-skill',
  name: 'My Custom Skill',
  description: 'Description of what this skill does',
  execute: async (data) => {
    // Skill logic here
    return { result: 'success' };
  }
});
```

### Backend Skill

```javascript
// In skills/Back-End/skillRegistry.js
this.register({
  id: 'my-backend-skill',
  name: 'My Backend Skill',
  description: 'Description of what this skill does',
  execute: async (data) => {
    // Skill logic here
    return { result: 'success' };
  }
});
```

## API Endpoints

### Skills API

- `GET /api/skills` - Get all available skills
- `POST /api/skills/:skillId/execute` - Execute a specific skill

Example:
```bash
curl -X POST http://localhost:3001/api/skills/data-processor/execute \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "value"}}'
```

## Development

### Frontend

- Built with React
- Uses React Hooks for skill management
- Axios for API communication

### Backend

- Built with Node.js and Express
- RESTful API architecture
- Modular skill system

## Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
npm test
```

## Contributing

1. Create a new branch for your feature
2. Add your skills to the appropriate registry
3. Test your changes
4. Submit a pull request

## License

MIT

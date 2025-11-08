import React from 'react';
import { useCustomSkills } from './customskills/useCustomSkills';

function App() {
  const { skills, executeSkill } = useCustomSkills();

  return (
    <div className="App">
      <header>
        <h1>Frontend Application</h1>
        <p>With CustomSkills Support</p>
      </header>
      <main>
        <h2>Available Skills</h2>
        <ul>
          {skills.map(skill => (
            <li key={skill.id}>
              <button onClick={() => executeSkill(skill.id)}>
                {skill.name}
              </button>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

export default App;

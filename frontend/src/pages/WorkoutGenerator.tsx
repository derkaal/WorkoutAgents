import React from 'react';
import { WorkoutGenerator } from '../components/WorkoutGenerator';

const WorkoutGeneratorPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-md mx-auto space-y-6 pt-8">
        <h1 className="text-2xl font-bold text-white">Mike Lawry Workout Generator</h1>
        <WorkoutGenerator />
      </div>
    </div>
  );
};

export default WorkoutGeneratorPage;
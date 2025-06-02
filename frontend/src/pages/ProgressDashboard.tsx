import React from 'react';
import { ProgressAnalyzer } from '../components/ProgressAnalyzer';

const ProgressDashboardPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6 pt-8">
        <h1 className="text-2xl font-bold text-white">Trystero Progress Analysis</h1>
        <p className="text-gray-300">
          Track your workout progress and receive personalized insights from Trystero.
        </p>
        <ProgressAnalyzer />
      </div>
    </div>
  );
};

export default ProgressDashboardPage;
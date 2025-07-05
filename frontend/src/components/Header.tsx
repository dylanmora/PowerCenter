import React from 'react';
import { Search, Target } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-gray-900 to-red-600 text-white p-6 shadow-lg">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search meets..." 
              className="bg-red-800 text-white px-4 py-2 rounded-lg pl-10 focus:outline-none focus:ring-2 focus:ring-red-500" 
            />
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          </div>
          <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center transition-colors">
            <Target className="w-4 h-4 mr-2" />
            New Meet
          </button>
        </div>
      </div>
    </header>
  );
}; 
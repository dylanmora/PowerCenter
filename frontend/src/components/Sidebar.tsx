import React from 'react';
import { Home, Trophy, BarChart3, Users, Settings } from 'lucide-react';
import ShinyText from '../blocks/TextAnimations/ShinyText/ShinyText';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'lifters', label: 'Lifters', icon: Users },
  { id: 'meets', label: 'Meets', icon: Trophy },
  { id: 'analysis', label: 'Analysis', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
] as const;

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="sidebar fixed inset-y-0 left-0 w-64 bg-gray-900 text-white p-6 z-40">
              <div className="flex items-center justify-between mb-10">
          <h1 className="text-2xl font-bold">
            <ShinyText 
              text="Power" 
              disabled={false} 
              speed={2} 
              className="text-2xl font-bold"
            />
            <span className="text-white">Center</span>
          </h1>
        </div>
      
      <nav>
        <ul className="space-y-4">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <li key={id}>
              <button 
                onClick={() => onTabChange(id)}
                className={`w-full flex items-center p-3 rounded-lg transition-colors ${
                  activeTab === id 
                    ? 'bg-red-800 text-white' 
                    : 'hover:bg-gray-800 text-gray-300 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}; 
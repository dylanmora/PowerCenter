import React from 'react';
import { LucideIcon } from 'lucide-react';

interface PlaceholderTabProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export const PlaceholderTab: React.FC<PlaceholderTabProps> = ({ 
  title, 
  description, 
  icon: Icon 
}) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="flex items-center gap-3 mb-4">
        <Icon className="w-6 h-6 text-gray-500" />
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      </div>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}; 
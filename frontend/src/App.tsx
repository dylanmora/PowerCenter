import React, { useState } from 'react';
import { Trophy, BarChart3, Users, Settings } from 'lucide-react';
import { MeetResult } from './types/meet';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { LiftersPage } from './components/LiftersPage';
import { PlaceholderTab } from './components/PlaceholderTab';
import './App.css';

/**
 * Main application component for PowerCenter
 * A professional powerlifting meet analysis dashboard
 */
function App() {
  const [result, setResult] = useState<MeetResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleResult = (newResult: MeetResult) => {
    setResult(newResult);
    setError(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setResult(null);
  };

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard
            result={result}
            error={error}
            isLoading={isLoading}
            onResult={handleResult}
            onError={handleError}
            onLoadingChange={handleLoadingChange}
          />
        );
      case 'meets':
        return (
          <PlaceholderTab
            title="Meets"
            description="Meet management features coming soon..."
            icon={Trophy}
          />
        );
      case 'analysis':
        return (
          <PlaceholderTab
            title="Analysis"
            description="Advanced analysis features coming soon..."
            icon={BarChart3}
          />
        );
      case 'lifters':
        return (
          <LiftersPage
            onError={handleError}
            onLoadingChange={handleLoadingChange}
          />
        );
      case 'settings':
        return (
          <PlaceholderTab
            title="Settings"
            description="Settings and configuration coming soon..."
            icon={Settings}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="md:ml-64 min-h-screen flex-1">
        <Header />
        <main className="p-6">
          {renderTabContent()}
        </main>
      </div>
    </div>
  );
}

export default App;

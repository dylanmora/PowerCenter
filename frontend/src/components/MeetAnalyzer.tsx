import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { MeetResult } from '../types/meet';
import { API_ENDPOINTS, API_CONFIG } from '../config/api';

interface MeetAnalyzerProps {
  onResult: (result: MeetResult) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export const MeetAnalyzer: React.FC<MeetAnalyzerProps> = ({ 
  onResult, 
  onError, 
  onLoadingChange 
}) => {
  const [meetUrl, setMeetUrl] = useState('');

  const analyzeMeet = async () => {
    if (!meetUrl.trim()) {
      onError('Please enter a meet URL');
      return;
    }

    onLoadingChange(true);
    onError('');

    try {
      const response = await fetch(API_ENDPOINTS.MEET_ANALYZE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ meet_url: meetUrl }),
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      onResult(result);
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Failed to analyze meet. Please check the URL and try again.';
      onError(errorMessage);
    } finally {
      onLoadingChange(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      analyzeMeet();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Analyze New Meet</h3>
      <p className="text-sm text-gray-600 mb-4">Enter the URL of the meet you want to analyze. Meets can be found at LiftingCast.com. The URL should be in the format https://liftingcast.com/meet/meet-name/roster. </p>
      <div className="flex gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={meetUrl}
            onChange={(e) => setMeetUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter LiftingCast meet URL..."
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all duration-200"
          />
        </div>
        <button
          onClick={analyzeMeet}
          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold transition-all duration-200"
        >
          <Search className="w-5 h-5" />
          Analyze
        </button>
      </div>
    </div>
  );
}; 
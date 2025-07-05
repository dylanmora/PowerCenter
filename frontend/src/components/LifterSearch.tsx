import React, { useState } from 'react';
import { Search, Loader2, User, Calendar, Trophy } from 'lucide-react';
import { LifterSearchParams, LifterSearchResult } from '../types/lifter';
import { API_ENDPOINTS, API_CONFIG } from '../config/api';
import { formatWeight, formatDotScore } from '../utils/formatters';

interface LifterSearchProps {
  onResult: (result: LifterSearchResult) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export const LifterSearch: React.FC<LifterSearchProps> = ({ 
  onResult, 
  onError, 
  onLoadingChange 
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const searchLifters = async () => {
    if (!searchTerm.trim()) {
      onError('Please enter a lifter name to search');
      return;
    }

    onLoadingChange(true);
    onError('');

    try {
      const params: LifterSearchParams = {
        name: searchTerm.trim(),
        limit: 20,
        offset: 0
      };

      const queryString = new URLSearchParams({
        name: params.name,
        limit: params.limit?.toString() || '20',
        offset: params.offset?.toString() || '0'
      }).toString();

      const response = await fetch(`${API_ENDPOINTS.LIFTER_SEARCH}?${queryString}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
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
        : 'Failed to search for lifters. Please try again.';
      onError(errorMessage);
    } finally {
      onLoadingChange(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchLifters();
    }
  };

  return (
    <div className="mb-8">
      <h3 className="text-xl font-bold text-gray-900 mb-2">Search Lifters</h3>
      <p className="text-sm text-gray-600 mb-4">
        Search for lifters by name. Results will show their competition history and personal bests.
      </p>
      <div className="flex gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter lifter name (e.g., John Smith)..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all duration-200"
          />
        </div>
        <button
          onClick={searchLifters}
          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold transition-all duration-200"
        >
          <Search className="w-5 h-5" />
          Search
        </button>
      </div>
    </div>
  );
}; 
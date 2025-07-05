import React, { useState } from 'react';
import { Users, AlertCircle, Search, TrendingUp } from 'lucide-react';
import { LifterSearchResult } from '../types/lifter';
import { LifterSearch } from './LifterSearch';
import { LifterCard } from './LifterCard';
import { StatsCard } from './StatsCard';

interface LiftersPageProps {
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export const LiftersPage: React.FC<LiftersPageProps> = ({ 
  onError, 
  onLoadingChange 
}) => {
  const [searchResult, setSearchResult] = useState<LifterSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearchResult = (result: LifterSearchResult) => {
    setSearchResult(result);
    setError(null);
  };

  const handleSearchError = (errorMessage: string) => {
    setError(errorMessage);
    setSearchResult(null);
    onError(errorMessage);
  };

  const statsCards = [
    {
      title: 'Total Results',
      value: searchResult ? searchResult.total_count : '0',
      subtitle: searchResult ? 'Lifters found' : 'No search yet',
      icon: Users,
      iconBgColor: 'bg-blue-100',
      iconColor: 'text-blue-600',
      valueColor: 'text-blue-500'
    },
    {
      title: 'Avg. Total',
      value: searchResult && searchResult.lifters.length > 0 
        ? `${(searchResult.lifters.reduce((sum, l) => sum + l.total, 0) / searchResult.lifters.length).toFixed(1)} kg`
        : '0 kg',
      subtitle: searchResult ? 'Average performance' : 'No data',
      icon: TrendingUp,
      iconBgColor: 'bg-red-100',
      iconColor: 'text-red-600',
      valueColor: 'text-red-500'
    }
  ];

  return (
    <>
      {/* Page Header */}
      {/*<div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Lifter Database</h1>
        <p className="text-gray-600">
          Search and explore lifter profiles, competition history, and performance data.
        </p>
      </div>*/}

      {/* Search Section */}
      <div className="mb-8">
        <LifterSearch 
          onResult={handleSearchResult}
          onError={handleSearchError}
          onLoadingChange={onLoadingChange}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-8">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-center gap-4">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <p className="text-red-700 text-lg">{error}</p>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResult && (
        <>
          {/* Results Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Search Results for "{searchResult.search_term}"
              </h2>
              <div className="text-sm text-gray-600">
                {searchResult.total_count} lifters found
              </div>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="flex items-center gap-8 mb-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-600" />
              <span><strong className="text-gray-900">{searchResult ? searchResult.total_count : '0'}</strong> lifters found</span>
            </div>
            {searchResult && searchResult.lifters.length > 0 && (
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-red-600" />
                <span>Avg total: <strong className="text-gray-900">
                  {(searchResult.lifters.reduce((sum, l) => sum + l.total, 0) / searchResult.lifters.length).toFixed(1)} kg
                </strong></span>
              </div>
            )}
          </div>

          {/* Lifters List */}
          <div className="space-y-4">
            {searchResult.lifters.map((lifter, index) => (
              <LifterCard key={index} lifter={lifter} index={index} />
            ))}
          </div>

          {/* No Results Message */}
          {searchResult.lifters.length === 0 && (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No lifters found</h3>
              <p className="text-gray-600">
                Try adjusting your search terms or check the spelling.
              </p>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!searchResult && !error && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Search for Lifters</h3>
          <p className="text-gray-600">
            Enter a lifter's name above to search the database and view their competition history.
          </p>
        </div>
      )}
    </>
  );
}; 
import React from 'react';
import { Trophy, Users, TrendingUp, Target, AlertCircle, TrendingUp as TrendingUpIcon } from 'lucide-react';
import { MeetResult } from '../types/meet';
import { formatWeight, formatPercentage, calculateAverageDotScore } from '../utils/formatters';
import { MeetAnalyzer } from './MeetAnalyzer';
import { StatsCard } from './StatsCard';
import { TopPerformers } from './TopPerformers';

interface DashboardProps {
  result: MeetResult | null;
  error: string | null;
  isLoading: boolean;
  onResult: (result: MeetResult) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  result,
  error,
  isLoading,
  onResult,
  onError,
  onLoadingChange
}) => {
  const statsCards = [
    {
      title: 'Total Meets',
      value: '1',
      subtitle: '',
      icon: Trophy,
      iconBgColor: 'bg-red-100',
      iconColor: 'text-red-600',
      valueColor: 'text-green-500'
    },
    {
      title: 'Total Lifters',
      value: result ? result.total_lifters : '0',
      subtitle: result ? `${result.successful_lookups} found` : 'No data yet',
      icon: Users,
      iconBgColor: 'bg-blue-100',
      iconColor: 'text-blue-600',
      valueColor: 'text-blue-500'
    },
    {
      title: 'Avg. Dot Score',
      value: result && result.top_performers.length > 0 
        ? calculateAverageDotScore(result.top_performers).toFixed(1)
        : '0.0',
      subtitle: result ? 'Performance metric' : 'No data yet',
      icon: TrendingUp,
      iconBgColor: 'bg-red-100',
      iconColor: 'text-red-600',
      valueColor: 'text-red-500'
    },
    {
      title: 'Avg. Total',
      value: result ? formatWeight(result.average_total) : '0 kg',
      subtitle: result ? 'Combined strength' : 'No data yet',
      icon: Target,
      iconBgColor: 'bg-red-100',
      iconColor: 'text-red-600',
      valueColor: 'text-red-500'
    }
  ];

  return (
    <>
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((card, index) => (
          <StatsCard key={index} {...card} />
        ))}
      </div>

      {/* Meet Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Input Form */}
        <div className="lg:col-span-2">
          <MeetAnalyzer 
            onResult={onResult}
            onError={onError}
            onLoadingChange={onLoadingChange}
          />
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Meet Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Lifters</span>
              <span className="text-gray-900 font-medium">
                {result ? result.total_lifters : '0'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Successful Lookups</span>
              <span className="text-green-500 font-medium">
                {result ? result.successful_lookups : '0'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Failed Lookups</span>
              <span className="text-red-500 font-medium">
                {result ? result.failed_lookups : '0'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Success Rate</span>
              <span className="text-blue-500 font-medium">
                {result && result.total_lifters > 0 
                  ? formatPercentage(result.successful_lookups, result.total_lifters)
                  : '0%'
                }
              </span>
            </div>
          </div>
        </div>
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

      {/* Results */}
      {result && (
        <div className="space-y-8">
          {/* Meet Title */}
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">{result.meet_name}</h2>
          </div>

          {/* Statistics */}
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <TrendingUpIcon className="w-6 h-6 mr-3 text-red-500" />
              Meet Statistics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatWeight(result.average_squat)}
                </div>
                <div className="text-gray-500 text-sm">Avg Squat</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatWeight(result.average_bench)}
                </div>
                <div className="text-gray-500 text-sm">Avg Bench</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatWeight(result.average_deadlift)}
                </div>
                <div className="text-gray-500 text-sm">Avg Deadlift</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatWeight(result.average_total)}
                </div>
                <div className="text-gray-500 text-sm">Avg Total</div>
              </div>
            </div>
          </div>

          {/* Top Performers */}
          <TopPerformers performers={result.top_performers} />
        </div>
      )}
    </>
  );
}; 
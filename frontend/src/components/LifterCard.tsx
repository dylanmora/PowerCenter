import React from 'react';
import { User, Calendar, Trophy, TrendingUp } from 'lucide-react';
import { Lifter } from '../types/lifter';
import { formatWeight, formatDotScore } from '../utils/formatters';

interface LifterCardProps {
  lifter: Lifter;
  index: number;
}

export const LifterCard: React.FC<LifterCardProps> = ({ lifter, index }) => {
  const lifts = [
    { label: 'Squat', value: lifter.squat_kg, key: 'squat_kg' },
    { label: 'Bench', value: lifter.bench_kg, key: 'bench_kg' },
    { label: 'Deadlift', value: lifter.deadlift_kg, key: 'deadlift_kg' },
  ];

  const bestLift = lifts.reduce((max, curr) => (curr.value > max.value ? curr : max), lifts[0]);

  return (
    <div className="border-b border-gray-200 pb-4 hover:bg-gray-50 transition-colors duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-lg font-bold text-gray-400 w-8">#{index + 1}</div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{lifter.name}</h3>
            <p className="text-sm text-gray-600">
              {lifter.division} • {lifter.weight_class}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-gray-900">
            {formatWeight(lifter.total)}
          </div>
          <div className="text-sm text-yellow-600">
            Dot: {formatDotScore(lifter.dotscore)}
          </div>
        </div>
      </div>

      {/* Lift Details */}
      <div className="flex items-center gap-6 mt-3 ml-12">
        {lifts.map((lift) => (
          <div
            key={lift.key}
            className={`px-3 py-1 rounded text-sm transition-all duration-200 ${
              bestLift.key === lift.key
                ? 'bg-yellow-100 text-yellow-800 font-semibold'
                : 'text-gray-600'
            }`}
          >
            <span className="text-xs text-gray-500 mr-1">{lift.label}:</span>
            <span className="font-medium">{formatWeight(lift.value)}</span>
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="flex items-center gap-4 mt-2 ml-12 text-xs text-gray-500">
        {lifter.meet_name && (
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>{lifter.meet_name}</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <TrendingUp className="w-3 h-3" />
          <span>Age: {lifter.age}</span>
        </div>
      </div>
    </div>
  );
}; 
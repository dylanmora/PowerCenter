import React from 'react';
import { Trophy } from 'lucide-react';
import { TopPerformer, LiftData } from '../types/meet';
import { formatWeight, formatDotScore } from '../utils/formatters';

interface TopPerformersProps {
  performers: TopPerformer[];
}

export const TopPerformers: React.FC<TopPerformersProps> = ({ performers }) => {
  const getLiftData = (performer: TopPerformer): LiftData[] => [
    { label: 'Squat', value: performer.squat_kg, key: 'squat_kg' },
    { label: 'Bench', value: performer.bench_kg, key: 'bench_kg' },
    { label: 'Deadlift', value: performer.deadlift_kg, key: 'deadlift_kg' },
  ];

  const getBestLift = (lifts: LiftData[]): LiftData => {
    return lifts.reduce((max, curr) => (curr.value > max.value ? curr : max), lifts[0]);
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
        <Trophy className="w-6 h-6 mr-3 text-yellow-500" />
        Top Performers
      </h3>
      <div className="space-y-4">
        {performers.map((performer, index) => {
          const lifts = getLiftData(performer);
          const bestLift = getBestLift(lifts);
          
          return (
            <div
              key={index}
              className="relative group flex items-center justify-between p-4 rounded-xl bg-gray-50 border border-gray-200 hover:border-red-300 transition-all duration-300"
            >
              <div className="flex items-center gap-4">
                <div className="text-xl font-bold text-red-600">#{index + 1}</div>
                <div>
                  <h4 className="text-lg font-bold text-gray-900">{performer.name}</h4>
                  <p className="text-sm text-gray-600">
                    {performer.division} • {performer.weight_class}
                  </p>
                </div>
              </div>
              <div className="flex gap-6 items-center">
                {lifts.map((lift) => (
                  <div
                    key={lift.key}
                    className={`px-3 py-1 rounded-lg text-center transition-all duration-200 ${
                      bestLift.key === lift.key
                        ? 'bg-yellow-100 font-bold text-yellow-800 border border-yellow-300'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <span className="text-xs text-gray-500">{lift.label}</span>
                    <div className="font-semibold flex items-center gap-1">
                      {formatWeight(lift.value)}
                    </div>
                  </div>
                ))}
                <div className="text-right ml-4">
                  <div className="text-2xl font-bold text-gray-900">
                    {formatWeight(performer.total)}
                  </div>
                  <div className="text-sm text-yellow-600">
                    Dot: {formatDotScore(performer.dotscore)}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 
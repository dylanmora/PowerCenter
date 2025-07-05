/**
 * Utility functions for formatting data in the PowerCenter application
 */

export const formatWeight = (weight: number): string => {
  if (!weight) return 'N/A';
  const lbs = weight * 2.20462; // Convert kg to lbs
  return `${weight.toFixed(1)} kg (${lbs.toFixed(1)} lbs)`;
};

export const formatAge = (age: number): string => {
  return age ? `${age.toFixed(1)} years` : 'N/A';
};

export const formatPercentage = (numerator: number, denominator: number): string => {
  if (denominator === 0) return '0%';
  return `${((numerator / denominator) * 100).toFixed(1)}%`;
};

export const formatDotScore = (dotScore: number): string => {
  return dotScore ? dotScore.toFixed(2) : 'N/A';
};

export const calculateAverageDotScore = (performers: Array<{ dotscore: number }>): number => {
  if (performers.length === 0) return 0;
  const total = performers.reduce((sum, p) => sum + (p.dotscore || 0), 0);
  return total / performers.length;
}; 
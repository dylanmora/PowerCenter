export interface TopPerformer {
  name: string;
  total: number;
  squat_kg: number;
  bench_kg: number;
  deadlift_kg: number;
  dotscore: number;
  weight_class: string;
  age: number;
  division: string;
}

export interface MeetResult {
  meet_name: string;
  date: string;
  total_lifters: number;
  successful_lookups: number;
  failed_lookups: number;
  average_squat: number;
  average_bench: number;
  average_deadlift: number;
  average_total: number;
  top_performers: TopPerformer[];
}

export interface LiftData {
  label: string;
  value: number;
  key: keyof Pick<TopPerformer, 'squat_kg' | 'bench_kg' | 'deadlift_kg'>;
} 
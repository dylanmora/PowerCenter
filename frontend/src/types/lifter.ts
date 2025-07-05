export interface Lifter {
  name: string;
  total: number;
  squat_kg: number;
  bench_kg: number;
  deadlift_kg: number;
  dotscore: number;
  weight_class: string;
  age: number;
  division: string;
  meet_name?: string;
  date?: string;
}

export interface LifterSearchResult {
  lifters: Lifter[];
  total_count: number;
  search_term: string;
}

export interface LifterSearchParams {
  name: string;
  limit?: number;
  offset?: number;
} 
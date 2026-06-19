export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterResponse {
  status: string;
  message: string;
  user_id: number;
}

export interface SuccessPrediction {
  success_probability: number;
  model_version: string;
}

export interface GrowthPrediction {
  growth_1y: number;
  growth_3y: number;
  growth_5y: number;
  model_version: string;
}

export interface RiskPrediction {
  financial_risk: number;
  operational_risk: number;
  market_risk: number;
  team_risk: number;
  risk_score: number;
}

export interface Startup {
  id: number;
  founder_id: number;
  name: string;
  industry: string;
  location: string;
  founding_year: number;
  description: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardData {
  rankings: Array<{ name: string; score: number }>;
  risk_distribution: Record<string, number>;
  funding_trends: Array<{ year: number; amount: number }>;
  industry_analysis: Record<string, { count: number; avg_success: number }>;
}

export interface SimilarStartup {
  startup_id: number;
  similarity_score: number;
}

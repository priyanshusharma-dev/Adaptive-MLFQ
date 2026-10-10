import axios from 'axios';
import type { SimulationRequest, SimulationResponse } from '../types';

const API_URL = 'http://localhost:8000/api';

export const runSimulation = async (request: SimulationRequest): Promise<SimulationResponse> => {
  const response = await axios.post(`${API_URL}/simulations/run`, request);
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};

export const generateWorkload = async (type: string, count: number, seed: number = 42): Promise<any[]> => {
  const response = await axios.post(`${API_URL}/workloads/generate`, { type, count, seed });
  return response.data;
};

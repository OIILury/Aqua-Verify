import { AnalysisReport, ChatMessage } from '../types';

const API_BASE = '/api';

/**
 * Analyse les documents uploadés
 */
export async function analyzeDocuments(
  files: File[],
  caseType: 'PC' | 'PA' = 'PC'
): Promise<AnalysisReport> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  const params = new URLSearchParams({ case_type: caseType });
  
  const response = await fetch(`${API_BASE}/analyze?${params.toString()}`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur lors de l\'analyse');
  }
  
  return response.json();
}

/**
 * Envoie un message au chatbot
 */
export async function sendChatMessage(
  message: string, 
  report?: AnalysisReport
): Promise<ChatMessage> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, report }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erreur de communication avec le chatbot');
  }
  
  return response.json();
}

/**
 * Vérifie l'état de l'API
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}


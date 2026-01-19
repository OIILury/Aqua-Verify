// Types pour les documents
export type DocumentType = 
  | 'PC1' | 'PC2' | 'PC3' | 'PC4' | 'PC5' | 'PC6' | 'PC7' | 'PC8'
  | 'CERFA' | 'AVIS_EP' | 'AVIS_DEA' | 'DPC' | 'COUPE_BASSIN' | 'AUTRE';

export type DocumentStatus = 'conforme' | 'non_conforme' | 'manquant';

export interface Document {
  filename: string;
  document_type: DocumentType;
  status: DocumentStatus;
  confidence: number;
  extracted_text?: string;
  issues: string[];
}

export interface ProjectInfo {
  surface_m2?: number;
  is_small_project?: boolean;
  address?: string;
  reference?: string;
}

export interface AnalysisReport {
  project_info: ProjectInfo;
  documents_conformes: Document[];
  documents_non_conformes: Document[];
  documents_manquants: string[];
  total_documents: number;
  conformity_score: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// Labels français pour les types de documents
export const DOCUMENT_LABELS: Record<DocumentType, string> = {
  PC1: 'Plan de situation',
  PC2: 'Plan de masse',
  PC3: 'Plan en coupe',
  PC4: 'Notice descriptive',
  PC5: 'Plan des façades',
  PC6: "Document d'insertion",
  PC7: 'Photo env. proche',
  PC8: 'Photo paysage lointain',
  CERFA: 'Formulaire CERFA',
  AVIS_EP: 'Avis Eaux Pluviales',
  AVIS_DEA: 'Avis DEA',
  DPC: 'DPC',
  COUPE_BASSIN: 'Coupe bassin',
  AUTRE: 'Autre document',
};


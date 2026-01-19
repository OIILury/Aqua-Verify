import { CheckCircle, XCircle, AlertTriangle, FileText, Info } from 'lucide-react';
import { AnalysisReport, DOCUMENT_LABELS, DocumentType } from '../types';

interface ReportProps {
  report: AnalysisReport;
}

export function Report({ report }: ReportProps) {
  const getScoreColor = (score: number) => {
    if (score >= 100) return 'text-emerald-600';
    if (score >= 75) return 'text-amber-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 100) return 'from-emerald-500 to-emerald-600';
    if (score >= 75) return 'from-amber-500 to-amber-600';
    if (score >= 50) return 'from-orange-500 to-orange-600';
    return 'from-red-500 to-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Score de conformité */}
      <div className="bg-white/80 backdrop-blur rounded-2xl p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-aqua-900">Score de conformité</h2>
            <p className="text-aqua-600 text-sm mt-1">
              {report.total_documents} document{report.total_documents > 1 ? 's' : ''} analysé{report.total_documents > 1 ? 's' : ''}
            </p>
          </div>
          <div className={`text-4xl font-bold ${getScoreColor(report.conformity_score)}`}>
            {report.conformity_score}%
          </div>
        </div>
        
        {/* Barre de progression */}
        <div className="mt-4 h-3 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full bg-gradient-to-r ${getScoreBg(report.conformity_score)} transition-all duration-1000`}
            style={{ width: `${report.conformity_score}%` }}
          />
        </div>
        
        {/* Infos projet si disponibles */}
        {(report.project_info.surface_m2 || report.project_info.address) && (
          <div className="mt-4 p-3 bg-aqua-50 rounded-lg flex items-start gap-3">
            <Info className="w-5 h-5 text-aqua-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-aqua-800">
              {report.project_info.surface_m2 && (
                <p>
                  <strong>Surface :</strong> {report.project_info.surface_m2} m² 
                  ({report.project_info.is_small_project ? '< 240 m² - petit projet' : '≥ 240 m² - gros projet'})
                </p>
              )}
              {report.project_info.address && (
                <p><strong>Adresse :</strong> {report.project_info.address}</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Documents conformes */}
      {report.documents_conformes.length > 0 && (
        <div className="bg-white/80 backdrop-blur rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-6 h-6 text-emerald-500" />
            <h3 className="text-lg font-semibold text-aqua-900">
              Documents présents ({report.documents_conformes.length})
            </h3>
          </div>
          
          <div className="grid gap-2">
            {report.documents_conformes.map((doc, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-3 bg-emerald-50 rounded-lg"
              >
                <FileText className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-emerald-900 truncate">{doc.filename}</p>
                  <p className="text-sm text-emerald-700">
                    {DOCUMENT_LABELS[doc.document_type as DocumentType] || doc.document_type}
                    {doc.confidence > 0 && (
                      <span className="ml-2 text-emerald-500">
                        ({Math.round(doc.confidence * 100)}% confiance)
                      </span>
                    )}
                  </p>
                </div>
                <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documents non conformes */}
      {report.documents_non_conformes.length > 0 && (
        <div className="bg-white/80 backdrop-blur rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <XCircle className="w-6 h-6 text-red-500" />
            <h3 className="text-lg font-semibold text-aqua-900">
              Documents non conformes ({report.documents_non_conformes.length})
            </h3>
          </div>
          
          <div className="grid gap-2">
            {report.documents_non_conformes.map((doc, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-3 bg-red-50 rounded-lg"
              >
                <FileText className="w-5 h-5 text-red-600 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-red-900 truncate">{doc.filename}</p>
                  <p className="text-sm text-red-700">
                    {DOCUMENT_LABELS[doc.document_type as DocumentType] || doc.document_type}
                  </p>
                  {doc.issues.length > 0 && (
                    <ul className="mt-1 text-xs text-red-600">
                      {doc.issues.map((issue, i) => (
                        <li key={i}>• {issue}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documents manquants */}
      {report.documents_manquants.length > 0 && (
        <div className="bg-white/80 backdrop-blur rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-6 h-6 text-amber-500" />
            <h3 className="text-lg font-semibold text-aqua-900">
              Documents manquants ({report.documents_manquants.length})
            </h3>
          </div>
          
          <div className="grid gap-2">
            {report.documents_manquants.map((docType, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-3 bg-amber-50 rounded-lg"
              >
                <FileText className="w-5 h-5 text-amber-600 flex-shrink-0" />
                <div className="flex-1">
                  <p className="font-medium text-amber-900">
                    {docType}
                  </p>
                  <p className="text-sm text-amber-700">
                    {DOCUMENT_LABELS[docType as DocumentType] || 'Document obligatoire'}
                  </p>
                </div>
                <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Non-conformités réglementaires (niveau dossier) */}
      {report.compliance_issues && report.compliance_issues.length > 0 && (
        <div className="bg-white/80 backdrop-blur rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-6 h-6 text-orange-500" />
            <h3 className="text-lg font-semibold text-aqua-900">
              Non-conformités / points à corriger ({report.compliance_issues.length})
            </h3>
          </div>

          <div className="grid gap-3">
            {report.compliance_issues.map((issue, index) => (
              <div key={index} className="p-4 bg-orange-50 rounded-xl border border-orange-100">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-semibold text-orange-900">{issue.title}</p>
                    <p className="text-sm text-orange-800 mt-1">{issue.message}</p>
                    {issue.related_documents?.length > 0 && (
                      <p className="text-xs text-orange-700 mt-2">
                        <strong>Lié à :</strong> {issue.related_documents.join(', ')}
                      </p>
                    )}
                    {issue.evidence && (
                      <p className="text-xs text-orange-700 mt-2">
                        <strong>Extrait :</strong> {issue.evidence}
                      </p>
                    )}
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-orange-100 text-orange-700 flex-shrink-0">
                    {issue.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


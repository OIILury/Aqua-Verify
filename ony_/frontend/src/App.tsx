import { useState } from 'react';
import { Droplets, RefreshCw } from 'lucide-react';
import { DropZone, Report, Chatbot } from './components';
import { analyzeDocuments } from './services/api';
import { AnalysisReport } from './types';

function App() {
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caseType, setCaseType] = useState<'PC' | 'PA'>('PC');

  const handleFilesSelected = async (files: File[]) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await analyzeDocuments(files, caseType);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setError(null);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gradient-to-r from-aqua-700 via-aqua-600 to-aqua-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-xl backdrop-blur">
                <Droplets className="w-8 h-8 animate-droplet" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Aqua Verify</h1>
                <p className="text-aqua-100 text-sm">
                  Vérification de conformité - Grand Chalon
                </p>
              </div>
            </div>
            
            {report && (
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors backdrop-blur"
              >
                <RefreshCw className="w-4 h-4" />
                Nouvelle analyse
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Message d'erreur */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            <p className="font-medium">Erreur</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!report ? (
          /* Vue d'upload */
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-aqua-900">
                Vérifiez votre dossier d&apos;urbanisme
              </h2>
              <p className="text-aqua-600 mt-2">
                Choisissez le type de demande, puis déposez vos documents pour vérifier leur conformité avec le zonage des eaux pluviales
              </p>
            </div>

            {/* Sélecteur de type de dossier */}
            <div className="mb-6 flex flex-wrap items-center justify-center gap-4">
              <span className="text-sm font-medium text-aqua-800">
                Type de demande :
              </span>
              <div className="inline-flex rounded-full bg-white/70 p-1 shadow-sm">
                <button
                  type="button"
                  onClick={() => setCaseType('PC')}
                  className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                    caseType === 'PC'
                      ? 'bg-aqua-600 text-white shadow-md'
                      : 'text-aqua-700 hover:bg-aqua-50'
                  }`}
                >
                  Permis de construire
                </button>
                <button
                  type="button"
                  onClick={() => setCaseType('PA')}
                  className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                    caseType === 'PA'
                      ? 'bg-aqua-600 text-white shadow-md'
                      : 'text-aqua-700 hover:bg-aqua-50'
                  }`}
                >
                  Permis d&apos;aménager
                </button>
              </div>
            </div>
            
            <DropZone onFilesSelected={handleFilesSelected} isLoading={isLoading} />
            
            {/* Infos */}
            <div className="mt-8 grid grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-white/50 rounded-xl">
                <div className="text-2xl font-bold text-aqua-700">PC / PA</div>
                <div className="text-sm text-aqua-600">Types de dossiers</div>
              </div>
              <div className="p-4 bg-white/50 rounded-xl">
                <div className="text-2xl font-bold text-aqua-700">PDF/DOCX</div>
                <div className="text-sm text-aqua-600">Formats acceptés</div>
              </div>
              <div className="p-4 bg-white/50 rounded-xl">
                <div className="text-2xl font-bold text-aqua-700">Instantané</div>
                <div className="text-sm text-aqua-600">Résultat rapide</div>
              </div>
            </div>
          </div>
        ) : (
          /* Vue des résultats */
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Rapport */}
            <div>
              <h2 className="text-xl font-semibold text-aqua-900 mb-4">
                Rapport d'analyse
              </h2>
              <Report report={report} />
            </div>
            
            {/* Chatbot */}
            <div>
              <h2 className="text-xl font-semibold text-aqua-900 mb-4">
                Assistant
              </h2>
              <Chatbot report={report} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 text-center text-aqua-600 text-sm">
        <p>
          Aqua Verify - Zonage des eaux pluviales du Grand Chalon
        </p>
        <p className="text-aqua-400 mt-1">
          Conformité réglementaire • Décembre 2024
        </p>
      </footer>
    </div>
  );
}

export default App;


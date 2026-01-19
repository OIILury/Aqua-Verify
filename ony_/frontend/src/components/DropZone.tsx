import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, Loader2 } from 'lucide-react';

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void;
  isLoading: boolean;
}

export function DropZone({ onFilesSelected, isLoading }: DropZoneProps) {
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    disabled: isLoading,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = () => {
    if (files.length > 0) {
      onFilesSelected(files);
    }
  };

  const clearAll = () => {
    setFiles([]);
  };

  return (
    <div className="space-y-4">
      {/* Zone de dépôt */}
      <div
        {...getRootProps()}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed p-8
          transition-all duration-300 cursor-pointer
          ${isDragActive 
            ? 'border-aqua-500 bg-aqua-50 scale-[1.02]' 
            : 'border-aqua-300 bg-white/50 hover:border-aqua-400 hover:bg-aqua-50/50'
          }
          ${isLoading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {/* Effet de vague en arrière-plan */}
        <div className="absolute inset-0 overflow-hidden opacity-10">
          <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-r from-aqua-400 via-aqua-500 to-aqua-400 animate-wave" 
               style={{ width: '200%' }} />
        </div>
        
        <div className="relative flex flex-col items-center gap-4">
          <div className={`
            p-4 rounded-full transition-all duration-300
            ${isDragActive ? 'bg-aqua-500 text-white scale-110' : 'bg-aqua-100 text-aqua-600'}
          `}>
            <Upload className="w-8 h-8" />
          </div>
          
          <div className="text-center">
            <p className="text-lg font-medium text-aqua-900">
              {isDragActive ? 'Déposez vos fichiers ici' : 'Glissez-déposez vos documents'}
            </p>
            <p className="text-sm text-aqua-600 mt-1">
              ou cliquez pour sélectionner (PDF, DOCX)
            </p>
          </div>
        </div>
      </div>

      {/* Liste des fichiers */}
      {files.length > 0 && (
        <div className="bg-white/70 backdrop-blur rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-aqua-900">
              {files.length} fichier{files.length > 1 ? 's' : ''} sélectionné{files.length > 1 ? 's' : ''}
            </h3>
            <button
              onClick={clearAll}
              className="text-sm text-aqua-600 hover:text-aqua-800 transition-colors"
            >
              Tout effacer
            </button>
          </div>
          
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center gap-3 p-2 bg-aqua-50 rounded-lg group"
              >
                <FileText className="w-5 h-5 text-aqua-600 flex-shrink-0" />
                <span className="text-sm text-aqua-800 truncate flex-1">
                  {file.name}
                </span>
                <span className="text-xs text-aqua-500">
                  {(file.size / 1024).toFixed(0)} Ko
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="p-1 opacity-0 group-hover:opacity-100 hover:bg-aqua-200 rounded transition-all"
                >
                  <X className="w-4 h-4 text-aqua-600" />
                </button>
              </div>
            ))}
          </div>
          
          {/* Bouton d'analyse */}
          <button
            onClick={handleAnalyze}
            disabled={isLoading || files.length === 0}
            className={`
              w-full mt-4 py-3 px-6 rounded-xl font-medium
              flex items-center justify-center gap-2
              transition-all duration-300
              ${isLoading 
                ? 'bg-aqua-300 text-aqua-100 cursor-not-allowed' 
                : 'bg-gradient-to-r from-aqua-600 to-aqua-700 text-white hover:from-aqua-700 hover:to-aqua-800 shadow-lg hover:shadow-xl hover:-translate-y-0.5'
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyse en cours...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Analyser les documents
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}


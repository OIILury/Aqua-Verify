import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { ChatMessage, AnalysisReport } from '../types';
import { sendChatMessage } from '../services/api';

interface ChatbotProps {
  report: AnalysisReport | null;
}

export function Chatbot({ report }: ChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: report 
        ? "Bonjour ! J'ai analysé vos documents. Posez-moi vos questions sur le rapport de conformité."
        : "Bonjour ! Je suis l'assistant Aqua Verify. Déposez d'abord vos documents pour que je puisse vous aider."
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Mettre à jour le message initial quand le rapport change
  useEffect(() => {
    if (report) {
      setMessages([{
        role: 'assistant',
        content: `Bonjour ! J'ai analysé vos ${report.total_documents} documents. Votre score de conformité est de **${report.conformity_score}%**. Posez-moi vos questions !`
      }]);
    }
  }, [report]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(input, report || undefined);
      setMessages(prev => [...prev, response]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Désolé, une erreur s'est produite. Veuillez réessayer."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Formater le contenu avec du markdown basique
  const formatContent = (content: string) => {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br />');
  };

  // Suggestions rapides
  const suggestions = [
    "Quels documents manquent ?",
    "Mon dossier est-il complet ?",
    "C'est quoi un PC2 ?",
  ];

  return (
    <div className="bg-white/80 backdrop-blur rounded-2xl shadow-lg flex flex-col h-[500px]">
      {/* Header */}
      <div className="p-4 border-b border-aqua-100 flex items-center gap-3">
        <div className="p-2 bg-aqua-100 rounded-full">
          <Bot className="w-5 h-5 text-aqua-600" />
        </div>
        <div>
          <h3 className="font-semibold text-aqua-900">Assistant Aqua Verify</h3>
          <p className="text-xs text-aqua-600">Posez vos questions sur votre dossier</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`
              p-2 rounded-full flex-shrink-0 h-fit
              ${message.role === 'user' ? 'bg-aqua-600' : 'bg-aqua-100'}
            `}>
              {message.role === 'user' 
                ? <User className="w-4 h-4 text-white" />
                : <Bot className="w-4 h-4 text-aqua-600" />
              }
            </div>
            <div className={`
              max-w-[80%] p-3 rounded-2xl chat-message
              ${message.role === 'user' 
                ? 'bg-aqua-600 text-white rounded-tr-md' 
                : 'bg-aqua-50 text-aqua-900 rounded-tl-md'
              }
            `}>
              <div 
                dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
              />
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="p-2 bg-aqua-100 rounded-full h-fit">
              <Bot className="w-4 h-4 text-aqua-600" />
            </div>
            <div className="bg-aqua-50 p-3 rounded-2xl rounded-tl-md">
              <Loader2 className="w-5 h-5 text-aqua-600 animate-spin" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 2 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => setInput(suggestion)}
              className="text-xs px-3 py-1.5 bg-aqua-50 text-aqua-700 rounded-full hover:bg-aqua-100 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-aqua-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez votre question..."
            className="flex-1 px-4 py-2 bg-aqua-50 rounded-xl border-0 focus:ring-2 focus:ring-aqua-500 outline-none text-aqua-900 placeholder-aqua-400"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`
              p-2 rounded-xl transition-all
              ${input.trim() && !isLoading
                ? 'bg-aqua-600 text-white hover:bg-aqua-700'
                : 'bg-aqua-200 text-aqua-400 cursor-not-allowed'
              }
            `}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}


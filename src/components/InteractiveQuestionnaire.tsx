import React, { useState, useEffect } from 'react';
import { CompanyData, QuestionnaireData } from './SSTDiagnosis';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface InteractiveQuestionnaireProps {
  companyData: CompanyData;
  onComplete: (data: QuestionnaireData) => void;
  onBack: () => void;
}

// Questions from the Python backend logic
const QUESTIONS = {
  q1: '¿Existe una Política de SST documentada y firmada?',
  q2: '¿La política ha sido difundida a todos los trabajadores?',
  q3: '¿La alta dirección evidencia su liderazgo?',
  q4: '¿Existe un RISST aprobado (+20trab)?',
  q5: '¿Se ha entregado el RISST a cada trabajador?',
  q6: '¿Cuenta con un CSST o Supervisor de SST?',
  q7: '¿El proceso de elección del CSST fue documentado?',
  q8: '¿Los miembros del CSST/Supervisor han sido capacitados?',
  q9: '¿El CSST se reúne mensualmente y tiene Libro de Actas?',
  q10: '¿Se ha realizado un estudio de línea base?',
  q11: '¿Existe una Matriz IPERC para todos los puestos?',
  q12: '¿La matriz IPERC ha sido actualizada?',
  q13: '¿Los trabajadores participaron en el IPERC?',
  q14: '¿Se ha elaborado y exhibido un Mapa de Riesgos?',
  q15: '¿Existe un Plan y Programa Anual de SST con presupuesto?',
  q16: '¿Existe un Programa Anual de Capacitaciones?',
  q17: '¿Se han realizado las 4 capacitaciones obligatorias al año?',
  q18: '¿Se realiza la inducción de SST a todo nuevo trabajador?',
  q19: '¿Las capacitaciones están documentadas?',
  q20: '¿Se aplican los controles del IPERC (jerarquía)?',
  q21: '¿Se entregan los EPP adecuados sin costo?',
  q22: '¿Existe un registro de entrega de EPP?',
  q23: '¿Se capacitó en el uso correcto de EPP?',
  q24: '¿Existen PETS para tareas de alto riesgo?',
  q25: '¿Cuenta con un Plan de Respuesta ante Emergencias?',
  q26: '¿Se han conformado y capacitado las brigadas?',
  q27: '¿Se realizan simulacros de emergencia periódicamente?',
  q28: '¿Se realizan los Exámenes Médicos Ocupacionales?',
  q29: '¿Se realiza el monitoreo de agentes (físicos, químicos, etc.)?',
  q30: '¿Se verifica que las contratas cumplen con la normativa SST?',
  q31: '¿Se realiza seguimiento a los objetivos del Plan Anual?',
  q32: '¿Existe un procedimiento para investigación de accidentes?',
  q33: '¿Se ha realizado la auditoría obligatoria del SGSST?',
  q34: '¿Lleva el Registro de accidentes de trabajo?',
  q35: '¿Lleva el Registro de exámenes médicos ocupacionales?',
  q36: '¿Lleva el Registro del monitoreo de agentes?',
  q37: '¿Lleva el Registro de inspecciones internas de SST?',
  q38: '¿Lleva el Registro de estadísticas de seguridad y salud?',
  q39: '¿Lleva el Registro de equipos de seguridad o emergencia?',
  q40: '¿Lleva el Registro de inducción y capacitación?',
  q41: '¿Lleva el Registro de auditorías?'
};

// Questions exempt for MYPE companies (micro and pequeña)
const PREGUNTAS_EXENTAS_MYPE = ['q36', 'q37', 'q38', 'q39', 'q41'];

export const InteractiveQuestionnaire: React.FC<InteractiveQuestionnaireProps> = ({
  companyData,
  onComplete,
  onBack
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<QuestionnaireData>({});
  const [isAnimating, setIsAnimating] = useState(false);

  // Filter questions based on company type
  const questionEntries = Object.entries(QUESTIONS).filter(([questionId]) => {
    if (companyData.tipoEmpresa === 'micro' || companyData.tipoEmpresa === 'pequena') {
      return !PREGUNTAS_EXENTAS_MYPE.includes(questionId);
    }
    return true;
  });

  const totalQuestions = questionEntries.length;
  const currentQuestion = questionEntries[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;

  const handleAnswer = (answer: 'si' | 'no') => {
    if (!currentQuestion) return;

    setIsAnimating(true);
    setAnswers(prev => ({ ...prev, [currentQuestion[0]]: answer }));

    setTimeout(() => {
      if (currentQuestionIndex < totalQuestions - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
      } else {
        // Questionnaire complete
        const finalAnswers = { ...answers, [currentQuestion[0]]: answer };
        onComplete(finalAnswers);
      }
      setIsAnimating(false);
    }, 300);
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    } else {
      onBack();
    }
  };

  useEffect(() => {
    setIsAnimating(false);
  }, [currentQuestionIndex]);

  if (!currentQuestion) return null;

  return (
    <div className="min-h-screen">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full z-50 bg-background border-b border-border">
        <div className="sb-progress-bar">
          <div 
            className="sb-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="px-4 py-3 text-center">
          <span className="text-sm text-muted-foreground">
            Pregunta {currentQuestionIndex + 1} de {totalQuestions}
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="pt-24 pb-12 px-4 min-h-screen flex items-center justify-center">
        <div className={`w-full max-w-4xl transition-all duration-300 ${isAnimating ? 'opacity-0 transform translate-y-4' : 'opacity-100 transform translate-y-0'}`}>
          {/* Logo */}
          <div className="text-center mb-8">
            <img 
              src="https://www.supportbrigades.com/wp-content/uploads/2025/09/xxpfbFuUGcA4.png" 
              alt="Support Brigades" 
              className="h-12 mx-auto"
            />
          </div>

          {/* Question Card */}
          <div className="sb-question-card text-center">
            <h2 className="text-2xl md:text-3xl font-semibold text-foreground mb-8 leading-relaxed">
              {currentQuestion[1]}
            </h2>

            {/* Answer Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
              <button
                onClick={() => handleAnswer('si')}
                className="sb-response-button hover:scale-105 active:scale-95"
              >
                ✅ Sí
              </button>
              <button
                onClick={() => handleAnswer('no')}
                className="sb-response-button hover:scale-105 active:scale-95"
              >
                ❌ No
              </button>
            </div>

            {/* Navigation */}
            <div className="mt-8 flex justify-between items-center">
              <button
                onClick={handleBack}
                className="sb-button-secondary"
              >
                <ChevronLeft className="w-4 h-4" />
                {currentQuestionIndex === 0 ? 'Volver a datos' : 'Anterior'}
              </button>

              <div className="text-sm text-muted-foreground">
                {currentQuestionIndex + 1} / {totalQuestions}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
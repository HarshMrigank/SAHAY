"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, ArrowLeft, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';

const QUESTIONS = [
  {
    id: 'feeling',
    title: 'How have you been feeling recently?',
    options: ['Very well', 'Okay', 'A little difficult', 'Quite difficult', 'Very difficult'],
  },
  {
    id: 'sleep',
    title: 'How has your sleep been?',
    options: ['Good', 'Mostly okay', 'Some difficulty', 'Very difficult'],
  },
  {
    id: 'routine',
    title: 'How has your daily routine been?',
    options: ['Normal', 'Slightly affected', 'Moderately affected', 'Significantly affected'],
  },
  {
    id: 'stress',
    title: 'Have you been experiencing increased fear, worry, or stress?',
    options: ['Never', 'Sometimes', 'Often', 'Almost always'],
  },
  {
    id: 'speak',
    title: 'Would you like to speak with someone?',
    options: ['Yes', 'Maybe later', 'No'],
  }
];

export default function CheckInPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [freeText, setFreeText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const handleOptionSelect = (option: string) => {
    setAnswers({ ...answers, [QUESTIONS[step].id]: option });
  };

  const handleNext = () => {
    if (step < QUESTIONS.length) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
    } else {
      router.push('/victim/dashboard');
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    // Mock submit
    setTimeout(() => {
      setIsSubmitting(false);
      setIsDone(true);
      setTimeout(() => router.push('/victim/dashboard'), 3000);
    }, 1500);
  };

  if (isDone) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-100 mb-6">
          <CheckCircle className="h-10 w-10 text-emerald-600" />
        </div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Check-in Complete</h1>
        <p className="text-slate-600">Thank you for sharing how you feel. Returning to dashboard...</p>
      </div>
    );
  }

  // Final Free-Text Step
  if (step === QUESTIONS.length) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white p-6 md:p-10 rounded-xl shadow-sm border border-slate-200">
          <div className="mb-8">
             <span className="text-sm font-medium text-slate-500 mb-2 block">Step {step + 1} of {QUESTIONS.length + 1}</span>
             <h2 className="text-2xl font-bold text-slate-800">Is there anything else you would like us to know?</h2>
             <p className="text-slate-500 mt-2">Your response will be handled according to the system&apos;s privacy and access controls.</p>
          </div>

          <div className="space-y-4">
             <textarea 
               rows={5}
               value={freeText}
               onChange={(e) => setFreeText(e.target.value)}
               placeholder="Optional: Tell us more about how you&apos;re feeling..."
               className="w-full p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
             />

             <div className="p-4 border border-slate-200 rounded-lg bg-slate-50 flex items-center justify-between">
                <div className="flex items-center">
                  <Mic className={`h-6 w-6 mr-3 ${isRecording ? 'text-rose-500 animate-pulse' : 'text-slate-400'}`} />
                  <div>
                    <p className="font-medium text-slate-700">Voice Response (Optional)</p>
                    <p className="text-sm text-slate-500">
                       {isRecording ? 'Recording... 00:14' : 'Tap to record a voice message'}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => setIsRecording(!isRecording)}
                  className={`px-4 py-2 rounded-full font-medium text-sm ${isRecording ? 'bg-rose-100 text-rose-700' : 'bg-slate-200 text-slate-700'}`}
                >
                  {isRecording ? 'Stop' : 'Record'}
                </button>
             </div>
          </div>

          <div className="mt-10 flex justify-between">
            <button onClick={handleBack} className="flex items-center px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">
              <ArrowLeft className="h-5 w-5 mr-2" /> Back
            </button>
            <button 
              onClick={handleSubmit} 
              disabled={isSubmitting}
              className="flex items-center px-6 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-800 font-medium transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Check-in'} <CheckCircle className="h-5 w-5 ml-2" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQ = QUESTIONS[step];
  const hasAnswered = !!answers[currentQ.id];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white p-6 md:p-10 rounded-xl shadow-sm border border-slate-200">
        <div className="mb-8">
           <span className="text-sm font-medium text-slate-500 mb-2 block">Step {step + 1} of {QUESTIONS.length + 1}</span>
           <h2 className="text-2xl font-bold text-slate-800">{currentQ.title}</h2>
        </div>

        <div className="space-y-3">
          {currentQ.options.map((option) => (
            <button
              key={option}
              onClick={() => handleOptionSelect(option)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                answers[currentQ.id] === option 
                  ? 'border-blue-600 bg-blue-50 text-blue-900 font-medium' 
                  : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50 text-slate-700'
              }`}
            >
              {option}
            </button>
          ))}
        </div>

        <div className="mt-10 flex justify-between">
          <button onClick={handleBack} className="flex items-center px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors">
            <ArrowLeft className="h-5 w-5 mr-2" /> Back
          </button>
          <button 
            onClick={handleNext} 
            disabled={!hasAnswered}
            className="flex items-center px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue <ArrowRight className="h-5 w-5 ml-2" />
          </button>
        </div>
      </div>
      
      <div className="mt-6 flex items-center justify-center space-x-2 text-sm text-slate-500">
         <AlertCircle className="h-4 w-4" />
         <span>Your responses are private and help us provide better support.</span>
      </div>
    </div>
  );
}

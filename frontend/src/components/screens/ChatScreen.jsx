import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Brain, Send, Mic, MicOff } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useVoice } from '@/hooks/useVoice';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { NeoInput } from '@/components/ui/NeoInput';
import { VoiceWaveform } from '@/components/ui/VoiceWaveform';
import { api } from '@/utils/api';
import { MOCK_CHAT_RESPONSES } from '@/utils/constants';

const QUICK_CHIPS = [
  'Where is my seat?',
  'Nearest food?',
  'Crowd at Gate A?',
  'I need help',
  'Translate this',
];

export const ChatScreen = () => {
  const [input, setInput] = useState('');
  const messages = useAppStore((s) => s.messages);
  const addMessage = useAppStore((s) => s.addMessage);
  const isTyping = useAppStore((s) => s.isTyping);
  const setTyping = useAppStore((s) => s.setTyping);
  const userId = useAppStore((s) => s.userId);
  const language = useAppStore((s) => s.language);
  const navigateTo = useAppStore((s) => s.navigateTo);
  const goBack = useAppStore((s) => s.goBack);
  const { isOnline } = useNetworkStatus();
  const { isListening, transcript, setTranscript, startListening, stopListening, speak } = useVoice();
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  const getMockResponse = (msg) => {
    const lower = msg.toLowerCase();
    if (lower.includes('hungry') || lower.includes('food') || lower.includes('eat')) return MOCK_CHAT_RESPONSES.food;
    if (lower.includes('seat') || lower.includes('gate')) return MOCK_CHAT_RESPONSES.seat;
    if (lower.includes('crowd') || lower.includes('busy') || lower.includes('gate')) return MOCK_CHAT_RESPONSES.crowd;
    if (lower.includes('hello') || lower.includes('hi')) return MOCK_CHAT_RESPONSES.hello;
    if (lower.includes('help')) return MOCK_CHAT_RESPONSES.help;
    return MOCK_CHAT_RESPONSES.default;
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { id: Date.now(), role: 'user', text: text.trim(), time: new Date().toISOString() };
    addMessage(userMsg);
    setInput('');
    setTranscript('');
    setTyping(true);

    if (!isOnline) {
      setTimeout(() => {
        addMessage({
          id: Date.now() + 1,
          role: 'assistant',
          text: 'I am currently offline. Please check your internet connection to use AI features. Your cached data is still available.',
          time: new Date().toISOString(),
        });
        setTyping(false);
      }, 500);
      return;
    }

    try {
      const res = await api.post('/api/v1/chat', {
        message: text.trim(),
        user_id: userId,
        language,
      });
      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: res.data.response_text || res.data.response || 'I understand. How can I help?',
        actions: res.data.actions || [],
        time: new Date().toISOString(),
      };
      addMessage(aiMsg);
      speak(aiMsg.text);
    } catch {
      const mock = getMockResponse(text.trim());
      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: mock.response_text,
        actions: mock.actions,
        time: new Date().toISOString(),
      };
      addMessage(aiMsg);
      speak(aiMsg.text);
    } finally {
      setTyping(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
      if (transcript || input) {
        sendMessage(transcript || input);
      }
    } else {
      startListening();
    }
  };

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-stadium-surface">
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
          style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ background: '#111D2E', boxShadow: '0 0 10px rgba(0, 180, 216, 0.3)' }}
          >
            <Brain size={20} color="#00B4D8" />
          </div>
          <div>
            <p className="text-stadium-text font-semibold text-sm">StadiumAI</p>
            <div className="flex items-center gap-1.5">
              <motion.div
                className="w-2 h-2 rounded-full bg-stadium-green"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <span className="text-stadium-text-secondary text-xs">Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-50">
            <Brain size={48} color="#4A5D75" />
            <p className="text-stadium-text-secondary mt-4">Ask me anything about the stadium</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-3 rounded-neo-input ${msg.role === 'user' ? 'rounded-br-sm' : 'rounded-bl-sm'}`}
              style={{
                background: msg.role === 'user' ? '#111D2E' : '#070F1A',
                boxShadow: msg.role === 'user'
                  ? '8px 8px 16px #050A10, -8px -8px 16px #1A2A40'
                  : 'inset 4px 4px 8px #050A10, inset -4px -4px 8px #1A2A40',
              }}
            >
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ background: '#111D2E' }}>
                    <Brain size={12} color="#00B4D8" />
                  </div>
                  <span className="text-stadium-text-secondary text-[10px]">StadiumAI</span>
                </div>
              )}
              <p className="text-stadium-text text-sm leading-relaxed">{msg.text}</p>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div
              className="px-4 py-3 rounded-neo-input rounded-bl-sm"
              style={{
                background: '#070F1A',
                boxShadow: 'inset 4px 4px 8px #050A10, inset -4px -4px 8px #1A2A40',
              }}
            >
              <div className="flex items-center gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-stadium-blue"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Voice Waveform */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-4 overflow-hidden"
          >
            <div className="py-2 flex items-center justify-center">
              <VoiceWaveform isActive={isListening} />
              <span className="text-stadium-blue text-xs ml-2">Listening...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Chips */}
      {messages.length === 0 && (
        <div className="px-4 pb-2">
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip}
                onClick={() => sendMessage(chip)}
                className="flex-shrink-0 px-3 py-2 rounded-xl text-xs text-stadium-text-secondary cursor-pointer whitespace-nowrap"
                style={{
                  background: '#111D2E',
                  boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
                }}
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="px-4 py-3 flex items-end gap-2 safe-area-bottom">
        <NeoInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isOnline ? 'Ask StadiumAI...' : 'AI features require internet'}
          disabled={!isOnline}
          className="flex-1"
        />
        <motion.button
          type="button"
          whileTap={{ scale: 0.9 }}
          onClick={handleMicToggle}
          className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 cursor-pointer"
          style={{
            background: isListening ? '#FF3D00' : '#FFD700',
            boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
          }}
        >
          {isListening ? <MicOff size={20} color="#FFFFFF" /> : <Mic size={20} color="#0A1628" />}
        </motion.button>
        <motion.button
          type="submit"
          whileTap={{ scale: 0.9 }}
          disabled={!input.trim() || !isOnline}
          className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 cursor-pointer disabled:opacity-50"
          style={{
            background: '#00B4D8',
            boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
          }}
        >
          <Send size={20} color="#FFFFFF" />
        </motion.button>
      </form>
    </div>
  );
};

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Brain, Send, Mic, MicOff, Sparkles } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useVoice } from '@/hooks/useVoice';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { VoiceWaveform } from '@/components/ui/VoiceWaveform';
import { api } from '@/utils/api';
import { MOCK_CHAT_RESPONSES } from '@/utils/constants';

const QUICK_CHIPS = [
  '🗺️ Where is my seat?',
  '🍔 Nearest food corner?',
  '🚶 Crowd status at Gate A?',
  '🚨 Need emergency support',
  '🌎 Translate sign board',
];

const StreamingText = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let index = 0;
    setDisplayedText('');
    const timer = setInterval(() => {
      setDisplayedText((prev) => prev + text.charAt(index));
      index++;
      if (index >= text.length) {
        clearInterval(timer);
      }
    }, 12);
    return () => clearInterval(timer);
  }, [text]);

  return <span>{displayedText}</span>;
};

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
    <div 
      className="h-full flex flex-col relative" 
      style={{ background: '#050608', color: '#F0F4F8' }}
    >
      {/* Header */}
      <div 
        className="flex items-center gap-3 px-6 py-4 border-b"
        style={{ borderColor: 'rgba(255, 255, 255, 0.06)' }}
      >
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-colors duration-200"
          style={{ background: 'rgba(255, 255, 255, 0.04)', border: '1px solid rgba(255, 255, 255, 0.08)' }}
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ 
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(6, 182, 212, 0.05))', 
              border: '1px solid rgba(6, 182, 212, 0.3)' 
            }}
          >
            <Brain size={20} color="#06B6D4" />
          </div>
          <div>
            <p className="text-white font-bold text-sm tracking-wide">StadiumAI Concierge</p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <motion.div
                className="w-2.5 h-2.5 rounded-full bg-[#06B6D4]"
                animate={{ scale: [1, 1.25, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Gemini Agent Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef} 
        className="flex-1 overflow-y-auto px-6 py-6 space-y-6 scrollbar-thin"
      >
        <div className="max-w-2xl mx-auto space-y-6">
          
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-full bg-cyan-950/40 border border-cyan-800/30 flex items-center justify-center mb-6">
                <Sparkles size={32} className="text-[#06B6D4] animate-pulse" />
              </div>
              <h2 className="text-xl font-bold text-white mb-2">How can I assist you today?</h2>
              <p className="text-gray-400 text-xs max-w-sm leading-relaxed">
                I can help you navigate to your seat, check live crowd congestion levels, translate text, find emergency exits, and classify recycle items.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => {
            const isLatestAssistant = msg.role === 'assistant' && idx === messages.length - 1;
            
            return (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-5 py-3.5 rounded-2xl relative ${
                    msg.role === 'user' 
                      ? 'rounded-br-sm text-white' 
                      : 'rounded-bl-sm text-gray-200'
                  }`}
                  style={{
                    background: msg.role === 'user' 
                      ? 'rgba(255, 255, 255, 0.08)' 
                      : 'rgba(6, 182, 212, 0.05)',
                    backdropFilter: 'blur(16px)',
                    border: msg.role === 'user'
                      ? '1px solid rgba(255, 255, 255, 0.08)'
                      : '1px solid rgba(6, 182, 212, 0.15)',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
                  }}
                >
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-5 h-5 rounded-full flex items-center justify-center bg-cyan-950 border border-cyan-800/30">
                        <Brain size={12} color="#06B6D4" />
                      </div>
                      <span className="text-gray-400 text-[10px] font-bold uppercase tracking-wider">STADIUM AI</span>
                    </div>
                  )}
                  
                  <p className="text-sm leading-relaxed whitespace-pre-wrap select-text">
                    {isLatestAssistant ? (
                      <StreamingText text={msg.text} />
                    ) : (
                      msg.text
                    )}
                  </p>
                </div>
              </div>
            );
          })}

          {isTyping && (
            <div className="flex justify-start">
              <div
                className="px-5 py-3.5 rounded-2xl rounded-bl-sm"
                style={{
                  background: 'rgba(6, 182, 212, 0.05)',
                  border: '1px solid rgba(6, 182, 212, 0.15)'
                }}
              >
                <div className="flex items-center gap-1.5 py-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2.5 h-2.5 rounded-full bg-[#06B6D4]"
                      animate={{ y: [0, -6, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Voice Waveform */}
      <AnimatePresence>
        {isListening && (
          <div className="absolute inset-x-0 bottom-32 flex justify-center z-55">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="px-5 py-2.5 rounded-full flex items-center gap-3 bg-red-950 border border-red-800/50 shadow-lg"
            >
              <VoiceWaveform isActive={isListening} />
              <span className="text-red-400 font-bold text-xs uppercase tracking-wider animate-pulse">Listening...</span>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Bottom Floating Control Panel */}
      <div 
        className="w-full pb-8 pt-4 px-6 border-t"
        style={{ 
          background: 'rgba(5, 6, 8, 0.95)', 
          backdropFilter: 'blur(20px)',
          borderColor: 'rgba(255, 255, 255, 0.06)' 
        }}
      >
        <div className="max-w-2xl mx-auto space-y-4">
          
          {/* Quick Chips Prompts */}
          {messages.length === 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
              {QUICK_CHIPS.map((chip) => (
                <button
                  key={chip}
                  onClick={() => sendMessage(chip)}
                  className="flex-shrink-0 px-3.5 py-2 rounded-xl text-xs text-gray-300 hover:text-white cursor-pointer whitespace-nowrap transition-colors"
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                  }}
                >
                  {chip}
                </button>
              ))}
            </div>
          )}

          {/* Floating Input Box */}
          <form 
            onSubmit={handleSubmit} 
            className="flex items-center gap-3 p-2 rounded-2xl focus-within:ring-2 focus-within:ring-[#06B6D4]/30 transition-all duration-200"
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isOnline ? 'Type a question or message to StadiumAI...' : 'AI features require internet connection'}
              disabled={!isOnline}
              className="flex-1 bg-transparent text-sm text-white placeholder-gray-500 outline-none px-3"
            />
            
            <motion.button
              type="button"
              whileTap={{ scale: 0.92 }}
              onClick={handleMicToggle}
              className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 cursor-pointer transition-colors duration-150"
              style={{
                background: isListening ? '#EF4444' : 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              {isListening ? <MicOff size={18} color="#FFFFFF" /> : <Mic size={18} color="#06B6D4" />}
            </motion.button>
            
            <motion.button
              type="submit"
              whileTap={{ scale: 0.92 }}
              disabled={!input.trim() || !isOnline}
              className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 cursor-pointer disabled:opacity-30 bg-[#06B6D4] hover:bg-[#06B6D4]/90"
            >
              <Send size={18} color="#FFFFFF" />
            </motion.button>
          </form>

        </div>
      </div>
    </div>
  );
};

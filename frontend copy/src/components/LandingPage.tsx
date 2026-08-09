'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useEmotionStore } from '@/stores/emotionStore';

const LandingPage = () => {
  const navigate = useNavigate();
  const resetState = useEmotionStore((state) => state.resetState);

  const handleDiveIn = () => {
    resetState();
    navigate('/scanner');
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20">
        <motion.div
          className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-neon-blue/20 blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-neon-magenta/20 blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.4, 0.2, 0.4],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="text-center z-10 px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          {/* Main Title */}
          <motion.h1
            className="text-8xl md:text-9xl font-bold mb-8 text-gradient-primary"
            animate={{
              textShadow: [
                "0 0 20px hsl(195 100% 50% / 0.5)",
                "0 0 40px hsl(300 100% 50% / 0.5)",
                "0 0 20px hsl(195 100% 50% / 0.5)",
              ],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            AURA
          </motion.h1>

          {/* Subtitle with process explanation */}
          <motion.div
            className="mb-12 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
          >
            <p className="text-xl text-muted-foreground leading-relaxed">
              Discover movies that match your emotional aura through advanced emotion detection
            </p>
            
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { step: "1", title: "Scan Your Emotion", desc: "Let our AI analyze your facial expressions" },
                { step: "2", title: "Refine Your Mood", desc: "Choose to amplify or transition your feelings" },
                { step: "3", title: "Discover Your Movie", desc: "Get personalized recommendations" }
              ].map((item, index) => (
                <motion.div
                  key={item.step}
                  className="glass p-6 rounded-xl border border-white/10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                >
                  <div className="text-neon-blue text-2xl font-bold mb-2">{item.step}</div>
                  <h3 className="text-white font-semibold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground text-sm">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.8, ease: "easeOut" }}
          >
            <Button
              variant="hero"
              size="xl"
              onClick={handleDiveIn}
              className="animate-pulse-glow"
            >
              Dive In
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;
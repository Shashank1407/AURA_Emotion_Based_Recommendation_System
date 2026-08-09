'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useNavigate } from 'react-router-dom';
import { useEmotionStore } from '@/stores/emotionStore';
import { Camera, Scan, Zap, RotateCcw } from 'lucide-react';

const EmotionScanner = () => {
  const navigate = useNavigate();
  const { 
    isScanning, 
    hasScanned, 
    emotions, 
    startScanning, 
    completeScanning, 
    setChoice 
  } = useEmotionStore();
  
  const [showWebcamDialog, setShowWebcamDialog] = useState(true);
  const [webcamGranted, setWebcamGranted] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);

  const handleWebcamAccess = async () => {
    setWebcamGranted(true);
    setShowWebcamDialog(false);
    startScanning();
    // Access webcam and capture a frame
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setVideoStream(stream); // Save stream for live preview
      const video = document.createElement('video');
      video.srcObject = stream;
      await new Promise(resolve => {
        video.onloadedmetadata = () => {
          video.play();
          resolve(true);
        };
      });
      // Wait a moment for camera to adjust
      await new Promise(res => setTimeout(res, 1000));
      // Draw video frame to canvas
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      // Get image as blob
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        setScanProgress(50);
        // Send to backend
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        try {
          const response = await fetch('http://localhost:8000/predict-emotion', {
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          // Map backend emotions to frontend format (first detected face)
          const colorMap = {
            'Happy': 'hsl(195 100% 50%)',
            'Neutral': 'hsl(0 0% 65%)',
            'Surprise': 'hsl(300 100% 50%)',
            'Sad': 'hsl(220 100% 45%)',
            'Angry': 'hsl(0 100% 50%)',
            'Disgust': 'hsl(120 100% 40%)',
            'Fear': 'hsl(270 100% 40%)',
            'No Face': 'hsl(0 0% 65%)'
          };
          let emotions = [];
          if (data.results && data.results.length > 0) {
            emotions = (data.results[0].emotions || []).map(e => ({
              name: e.name,
              percentage: e.percentage,
              color: colorMap[e.name] || 'hsl(0 0% 65%)'
            }));
          }
          setScanProgress(100);
          completeScanning(emotions);
        } catch (err) {
          setScanProgress(100);
          completeScanning([]);
        }
        // Cleanup
        stream.getTracks().forEach(track => track.stop());
      }, 'image/jpeg');
    } catch (err) {
      setScanProgress(100);
      completeScanning([]);
    }
  };

  useEffect(() => {
    if (videoStream && videoRef.current) {
      videoRef.current.srcObject = videoStream;
    }
    return () => {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [videoStream]);

  const handleChoice = (choice: 'amplify' | 'transition') => {
    setChoice(choice);
    navigate('/recommendations');
  };

  if (!webcamGranted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Dialog open={showWebcamDialog} onOpenChange={() => {}}>
          <DialogContent className="glass border border-white/20">
            <DialogHeader>
              <DialogTitle className="text-gradient-primary text-2xl">
                Camera Access Required
              </DialogTitle>
              <DialogDescription className="text-lg text-muted-foreground mt-4">
                AURA needs access to your camera to analyze your emotional state. 
                Your privacy is protected - all processing happens locally.
              </DialogDescription>
            </DialogHeader>
            <div className="flex justify-center mt-6">
              <Button 
                variant="hero" 
                size="lg" 
                onClick={handleWebcamAccess}
                className="gap-2"
              >
                <Camera className="w-5 h-5" />
                Grant Access
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-4xl">
        
        {/* Scanning Phase */}
        {!hasScanned && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold mb-8 text-gradient-primary">
              Analyzing Your Emotional Aura
            </h1>
            
            {/* Webcam Frame */}
            <div 
              className="relative mb-8 mx-auto w-80 h-80"
              style={{
                filter: emotions.length > 0 
                  ? `drop-shadow(0 0 20px ${emotions[0]?.color}40)` 
                  : 'drop-shadow(0 0 20px hsl(195 100% 50% / 0.25))'
              }}
            >
              <motion.div
                className="glass w-full h-full rounded-full border-2 overflow-hidden relative"
                style={{
                  borderColor: emotions.length > 0 
                    ? `${emotions[0]?.color}80` 
                    : 'hsl(195 100% 50% / 0.5)'
                }}
                animate={emotions.length > 0 ? {
                  borderColor: [
                    `${emotions[0]?.color}60`,
                    `${emotions[0]?.color}`,
                    `${emotions[0]?.color}60`,
                  ],
                  boxShadow: [
                    `0 0 30px ${emotions[0]?.color}30`,
                    `0 0 50px ${emotions[0]?.color}50`,
                    `0 0 30px ${emotions[0]?.color}30`,
                  ],
                } : {
                  borderColor: [
                    "hsl(195 100% 50% / 0.6)",
                    "hsl(300 100% 50% / 0.8)",
                    "hsl(195 100% 50% / 0.6)",
                  ],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {/* Live webcam feed */}
                {videoStream ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-card/50 to-muted/30 flex items-center justify-center">
                    <Camera className="w-16 h-16 text-muted-foreground" />
                  </div>
                )}
                {/* Scanning overlay */}
                {isScanning && (
                  <motion.div
                    className="absolute inset-0 border-4 border-neon-blue/80 rounded-full"
                    animate={{
                      scale: [1, 1.1, 1],
                      opacity: [0.8, 0.4, 0.8],
                    }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                )}
                
                {/* Scan lines */}
                {isScanning && (
                  <motion.div
                    className="absolute inset-0 overflow-hidden rounded-full"
                    initial={{ y: "-100%" }}
                    animate={{ y: "100%" }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <div className="w-full h-1 bg-gradient-primary opacity-80" />
                  </motion.div>
                )}
              </motion.div>
            </div>
            
            {/* Progress indicator */}
            {isScanning && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="max-w-md mx-auto"
              >
                <Progress value={scanProgress} className="mb-4" />
                <p className="text-muted-foreground flex items-center justify-center gap-2">
                  <Scan className="w-4 h-4 animate-spin" />
                  Scanning emotional patterns... {scanProgress}%
                </p>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Results Phase */}
        {hasScanned && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold mb-4 text-gradient-primary">
              Your Emotional Aura
            </h1>
            <p className="text-muted-foreground mb-8 text-lg">
              We've analyzed your emotional state. Here's what we found:
            </p>
            
            {/* Emotion Graph */}
            <Card className="glass p-8 mb-8 max-w-2xl mx-auto">
              <div className="space-y-6">
                {emotions.map((emotion, index) => (
                  <motion.div
                    key={emotion.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="space-y-2"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-foreground">
                        {emotion.name}
                      </span>
                      <span className="text-2xl font-bold text-neon-blue">
                        {emotion.percentage}%
                      </span>
                    </div>
                    <Progress 
                      value={emotion.percentage} 
                      className="h-3"
                      style={{ 
                        '--progress-color': emotion.color 
                      } as React.CSSProperties}
                    />
                  </motion.div>
                ))}
              </div>
            </Card>
            
            {/* Choice Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto"
            >
              <Button
                variant="neon"
                size="xl"
                onClick={() => handleChoice('amplify')}
                className="p-6 h-auto flex-col gap-4 text-center min-h-[140px]"
              >
                <Zap className="w-8 h-8" />
                <div className="space-y-2">
                  <div className="text-lg font-bold leading-tight">Amplify This Feeling</div>
                  <div className="text-xs opacity-80 leading-relaxed">
                    Find movies that enhance your current emotional state
                  </div>
                </div>
              </Button>
              
              <Button
                variant="neon-magenta"
                size="xl"
                onClick={() => handleChoice('transition')}
                className="p-6 h-auto flex-col gap-4 text-center min-h-[140px]"
              >
                <RotateCcw className="w-8 h-8" />
                <div className="space-y-2">
                  <div className="text-lg font-bold leading-tight">Transition My Mood</div>
                  <div className="text-xs opacity-80 leading-relaxed">
                    Discover movies that will shift your emotional energy
                  </div>
                </div>
              </Button>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default EmotionScanner;
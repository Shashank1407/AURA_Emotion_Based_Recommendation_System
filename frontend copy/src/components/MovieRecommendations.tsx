'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { useEmotionStore } from '@/stores/emotionStore';
import { ArrowLeft, Star, Clock, Calendar } from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface Movie {
  title: string;
  year: number;
  poster: string;
  plot: string;
  imdbRating: string;
}

const MovieRecommendations = () => {
  const navigate = useNavigate();
  const { selectedChoice, emotions } = useEmotionStore();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!emotions || emotions.length === 0) return;
      setLoading(true);
      setError(null);
      const mood = emotions[0].name;
      try {
        const response = await fetch(`http://localhost:5000/recommend?mood=${encodeURIComponent(mood)}`);
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        const data = await response.json();
        setMovies(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching recommendations');
      } finally {
        setLoading(false);
      }
    };
    fetchRecommendations();
  }, [emotions]);

  const getRecommendationTitle = () => {
    if (!selectedChoice) return "Your Movie Recommendations";
    const dominantEmotion = emotions.length > 0 ? emotions[0].name : "Happy";
    if (selectedChoice === 'amplify') {
      return `Movies to Amplify Your ${dominantEmotion} Mood`;
    } else {
      return `Movies to Transform Your ${dominantEmotion} Energy`;
    }
  };

  const getRecommendationSubtitle = () => {
    if (selectedChoice === 'amplify') {
      return "These films will enhance and celebrate your current emotional state";
    } else {
      return "These movies will guide you through an emotional journey and transformation";
    }
  };

  const handleBackToStart = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gradient-primary">
            {getRecommendationTitle()}
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            {getRecommendationSubtitle()}
          </p>
          {/* Emotion summary */}
          {emotions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex justify-center gap-2 mt-6"
            >
              {emotions.map((emotion) => (
                <Badge
                  key={emotion.name}
                  variant="secondary"
                  className="glass text-white border-neon-blue/50 px-4 py-2"
                >
                  {emotion.name} {emotion.percentage}%
                </Badge>
              ))}
            </motion.div>
          )}
        </motion.div>

        {/* Loading/Error State */}
        {loading && <div className="text-center text-lg">Loading recommendations...</div>}
        {error && <div className="text-center text-red-500">{error}</div>}

        {/* Movie Grid */}
        {!loading && !error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
          >
            {movies.map((movie, index) => (
              <motion.div
                key={movie.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
                whileHover={{ scale: 1.02 }}
              >
                <Card className="glass h-full border border-white/10 hover:border-neon-blue/50 transition-all duration-300">
                  <CardHeader className="text-center pb-4">
                    {/* Movie poster */}
                    <img src={movie.poster} alt={movie.title} className="mb-4 mx-auto w-20 h-32 object-cover rounded-lg bg-gradient-card" />
                    <CardTitle className="text-xl text-foreground">
                      {movie.title}
                    </CardTitle>
                    <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {movie.year}
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4" />
                        {movie.imdbRating}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-muted-foreground mb-4">
                      {movie.plot}
                    </CardDescription>
                    <Button variant="neon" className="w-full">
                      Watch Now
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Back to Start Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center"
        >
          <Button
            variant="glass"
            size="lg"
            onClick={handleBackToStart}
            className="gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Start
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default MovieRecommendations;
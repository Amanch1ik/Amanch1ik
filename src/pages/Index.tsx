import { useState, useEffect } from "react";
import EmotionCamera from "@/components/EmotionCamera";
import RobotAvatar from "@/components/RobotAvatar";
import StatsPanel from "@/components/StatsPanel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Brain, Github, Info, Eye } from "lucide-react";

const Index = () => {
  const [currentEmotion, setCurrentEmotion] = useState("Нейтральное");
  const [isSystemActive, setIsSystemActive] = useState(false);
  const [totalScans, setTotalScans] = useState(0);

  useEffect(() => {
    // Simulate scan counter
    let interval: NodeJS.Timeout;
    if (isSystemActive) {
      interval = setInterval(() => {
        setTotalScans(prev => prev + 1);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isSystemActive]);

  return (
    <div className="min-h-screen bg-gradient-bg">
      {/* Header */}
      <header className="border-b border-primary/20 bg-card/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center shadow-glow-primary">
                <Brain className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">Emotion Robot</h1>
                <p className="text-sm text-muted-foreground">AI-Powered Emotion Recognition System</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="bg-accent/20 text-accent border-accent/30">
                v2.1.0
              </Badge>
              <Button variant="outline" size="sm" className="border-primary/50">
                <Github className="w-4 h-4 mr-2" />
                GitHub
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Camera and Controls */}
          <div className="lg:col-span-2 space-y-6">
            <EmotionCamera 
              onEmotionChange={setCurrentEmotion}
              onStatusChange={setIsSystemActive}
            />
          </div>

          {/* Right Column - Robot Avatar and Stats */}
          <div className="space-y-6">
            <RobotAvatar currentEmotion={currentEmotion} />
            <StatsPanel isActive={isSystemActive} totalScans={totalScans} />
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12">
          <Card className="p-8 bg-gradient-to-br from-card to-card/50 border-primary/20 backdrop-blur-sm">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold gradient-text mb-4">
                Технологии будущего
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Наш робот использует передовые алгоритмы машинного обучения для анализа 
                эмоций в реальном времени с высочайшей точностью.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center p-6 rounded-lg bg-primary/5 border border-primary/20">
                <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4 shadow-glow-primary">
                  <Brain className="w-6 h-6 text-primary-foreground" />
                </div>
                <h3 className="font-semibold mb-2">ИИ Анализ</h3>
                <p className="text-sm text-muted-foreground">
                  Глубокое машинное обучение для точного распознавания эмоций
                </p>
              </div>

              <div className="text-center p-6 rounded-lg bg-secondary/5 border border-secondary/20">
                <div className="w-12 h-12 bg-gradient-secondary rounded-full flex items-center justify-center mx-auto mb-4 shadow-glow-secondary">
                  <Eye className="w-6 h-6 text-secondary-foreground" />
                </div>
                <h3 className="font-semibold mb-2">Реальное время</h3>
                <p className="text-sm text-muted-foreground">
                  Мгновенная обработка и анализ выражений лица
                </p>
              </div>

              <div className="text-center p-6 rounded-lg bg-accent/5 border border-accent/20">
                <div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center mx-auto mb-4 shadow-glow-accent">
                  <Info className="w-6 h-6 text-accent-foreground" />
                </div>
                <h3 className="font-semibold mb-2">Высокая точность</h3>
                <p className="text-sm text-muted-foreground">
                  94.2% точность распознавания основных эмоций
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-primary/20 bg-card/20 backdrop-blur-sm mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-muted-foreground">
            <p>© 2024 Emotion Robot. Создано с использованием React и современного ИИ.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;

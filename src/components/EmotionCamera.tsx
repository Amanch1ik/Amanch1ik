import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Camera, CameraOff, RotateCcw } from "lucide-react";

const emotions = [
  { name: "Счастье", color: "bg-green-500", intensity: 0 },
  { name: "Грусть", color: "bg-blue-500", intensity: 0 },
  { name: "Удивление", color: "bg-yellow-500", intensity: 0 },
  { name: "Злость", color: "bg-red-500", intensity: 0 },
  { name: "Страх", color: "bg-purple-500", intensity: 0 },
  { name: "Отвращение", color: "bg-orange-500", intensity: 0 },
  { name: "Нейтральное", color: "bg-gray-500", intensity: 0 },
];

interface EmotionCameraProps {
  onEmotionChange?: (emotion: string) => void;
  onStatusChange?: (isActive: boolean) => void;
}

export default function EmotionCamera({ onEmotionChange, onStatusChange }: EmotionCameraProps) {
  const [isActive, setIsActive] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState("Нейтральное");
  const [confidence, setConfidence] = useState(0);
  const [emotionData, setEmotionData] = useState(emotions);
  const [scanning, setScanning] = useState(false);

  const simulateEmotionDetection = () => {
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    const randomConfidence = Math.floor(Math.random() * 40) + 60; // 60-100%
    
    setCurrentEmotion(randomEmotion.name);
    setConfidence(randomConfidence);
    onEmotionChange?.(randomEmotion.name);
    
    // Update emotion data with random values
    setEmotionData(prev => prev.map(emotion => ({
      ...emotion,
      intensity: emotion.name === randomEmotion.name 
        ? randomConfidence 
        : Math.floor(Math.random() * 30)
    })));
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isActive) {
      setScanning(true);
      onStatusChange?.(true);
      interval = setInterval(simulateEmotionDetection, 2000);
    } else {
      setScanning(false);
      onStatusChange?.(false);
      setEmotionData(emotions);
      setCurrentEmotion("Нейтральное");
      setConfidence(0);
      onEmotionChange?.("Нейтральное");
    }
    return () => clearInterval(interval);
  }, [isActive, onEmotionChange, onStatusChange]);

  const toggleCamera = () => {
    setIsActive(!isActive);
  };

  const resetAnalysis = () => {
    setEmotionData(emotions);
    setCurrentEmotion("Нейтральное");
    setConfidence(0);
  };

  return (
    <div className="space-y-6">
      {/* Camera View */}
      <Card className="relative overflow-hidden bg-gradient-to-br from-card to-card/50 border-primary/20 backdrop-blur-sm">
        <div className="aspect-video bg-gradient-to-br from-muted/30 to-muted/10 relative flex items-center justify-center">
          {isActive ? (
            <div className="relative w-full h-full">
              {/* Scanning Line Animation */}
              {scanning && (
                <div className="absolute inset-0 z-10">
                  <div className="w-full h-0.5 bg-gradient-primary animate-scan opacity-60"></div>
                </div>
              )}
              
              {/* Face Detection Frame */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 border-2 border-primary animate-pulse-glow rounded-lg">
                  <div className="w-full h-full bg-gradient-primary/10 rounded-lg flex items-center justify-center">
                    <div className="text-4xl animate-float">👤</div>
                  </div>
                </div>
              </div>

              {/* Current Emotion Display */}
              {currentEmotion !== "Нейтральное" && (
                <div className="absolute bottom-4 left-4 right-4">
                  <Badge variant="secondary" className="w-full justify-center py-3 text-lg bg-primary/90 text-primary-foreground backdrop-blur-sm">
                    {currentEmotion} - {confidence}%
                  </Badge>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-muted-foreground">
              <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Камера выключена</p>
            </div>
          )}
        </div>
      </Card>

      {/* Controls */}
      <div className="flex gap-4 justify-center">
        <Button 
          onClick={toggleCamera}
          variant={isActive ? "destructive" : "default"}
          className="bg-gradient-primary hover:shadow-glow-primary transition-all duration-300"
        >
          {isActive ? <CameraOff className="w-4 h-4 mr-2" /> : <Camera className="w-4 h-4 mr-2" />}
          {isActive ? "Остановить" : "Запустить"}
        </Button>
        
        <Button 
          onClick={resetAnalysis}
          variant="outline" 
          disabled={!isActive}
          className="border-primary/50 hover:bg-primary/10 transition-all duration-300"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Сброс
        </Button>
      </div>

      {/* Emotion Analysis */}
      <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-primary/20 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4 gradient-text">Анализ эмоций</h3>
        <div className="space-y-3">
          {emotionData.map((emotion) => (
            <div key={emotion.name} className="flex items-center gap-3">
              <div className="w-24 text-sm text-muted-foreground">
                {emotion.name}
              </div>
              <div className="flex-1 bg-muted/30 rounded-full h-2 relative overflow-hidden">
                <div 
                  className={`h-full ${emotion.color} transition-all duration-1000 ease-out rounded-full`}
                  style={{ width: `${emotion.intensity}%` }}
                />
              </div>
              <div className="w-12 text-sm text-right text-muted-foreground">
                {emotion.intensity}%
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
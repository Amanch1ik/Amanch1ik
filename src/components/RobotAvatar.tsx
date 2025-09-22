import { useState, useEffect } from "react";
import robotAvatar from "@/assets/robot-avatar.jpg";

interface RobotAvatarProps {
  currentEmotion?: string;
}

export default function RobotAvatar({ currentEmotion = "Нейтральное" }: RobotAvatarProps) {
  const [eyeGlow, setEyeGlow] = useState("primary");

  useEffect(() => {
    // Change eye color based on detected emotion
    switch (currentEmotion) {
      case "Счастье":
        setEyeGlow("accent");
        break;
      case "Злость":
        setEyeGlow("destructive");
        break;
      case "Грусть":
        setEyeGlow("secondary");
        break;
      default:
        setEyeGlow("primary");
    }
  }, [currentEmotion]);

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="relative">
        <div 
          className={`w-32 h-32 rounded-full bg-gradient-to-br from-card to-card/50 p-2 shadow-glow-${eyeGlow} animate-pulse-glow border-2 border-${eyeGlow}/50`}
        >
          <img 
            src={robotAvatar}
            alt="Emotion Robot"
            className="w-full h-full rounded-full object-cover"
          />
        </div>
        
        {/* Animated pulse ring */}
        <div className={`absolute inset-0 rounded-full border-2 border-${eyeGlow} animate-ping opacity-20`}></div>
      </div>
      
      <div className="text-center">
        <h2 className="text-xl font-bold gradient-text">Emotion Robot</h2>
        <p className="text-sm text-muted-foreground">
          Состояние: <span className="text-foreground">{currentEmotion}</span>
        </p>
      </div>
    </div>
  );
}
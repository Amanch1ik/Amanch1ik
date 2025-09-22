import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Eye, Zap, TrendingUp } from "lucide-react";

interface StatsPanelProps {
  isActive: boolean;
  totalScans?: number;
}

export default function StatsPanel({ isActive, totalScans = 0 }: StatsPanelProps) {
  const stats = [
    {
      icon: <Activity className="w-5 h-5" />,
      label: "Статус",
      value: isActive ? "Активен" : "Неактивен",
      color: isActive ? "text-accent" : "text-muted-foreground",
    },
    {
      icon: <Eye className="w-5 h-5" />,
      label: "Сканирований",
      value: totalScans.toString(),
      color: "text-primary",
    },
    {
      icon: <Zap className="w-5 h-5" />,
      label: "Точность",
      value: "94.2%",
      color: "text-accent",
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      label: "Скорость",
      value: "Real-time",
      color: "text-secondary",
    },
  ];

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-primary/20 backdrop-blur-sm">
      <h3 className="text-lg font-semibold mb-4 gradient-text">Статистика системы</h3>
      
      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              {stat.icon}
              <span className="text-sm">{stat.label}</span>
            </div>
            <div className={`font-mono text-lg font-semibold ${stat.color}`}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Производительность</span>
          <Badge variant="secondary" className="bg-accent/20 text-accent border-accent/30">
            Отлично
          </Badge>
        </div>
        
        <div className="w-full bg-muted/30 rounded-full h-2">
          <div className="h-full bg-gradient-secondary rounded-full w-[94%] animate-pulse"></div>
        </div>
      </div>

      {isActive && (
        <div className="mt-4 p-3 bg-accent/10 rounded-lg border border-accent/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span className="text-sm text-accent font-medium">
              Система активно анализирует эмоции
            </span>
          </div>
        </div>
      )}
    </Card>
  );
}
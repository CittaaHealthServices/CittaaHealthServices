import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// CITTAA Brand Colors (from official website)
export const CITTAA_COLORS = {
  purple: '#9B8AA8',
  lavender: '#E8E0ED',
  lavenderLight: '#F5F0F8',
  green: '#7A9E7E',
  greenLight: '#A8C5AB',
  teal: '#7A9E7E',
  darkButton: '#4A4A4A',
  warmGray: '#6B7280',
  darkText: '#1F2937',
  lightBg: '#FAF8FC',
  white: '#FFFFFF',
};

// Escalation level colors
export const ESCALATION_COLORS = {
  level_4_emergency: '#DC2626',
  level_3_high: '#EA580C',
  level_2_moderate: '#CA8A04',
  level_1_low: '#059669',
};

// Format date for display
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// Format datetime for display
export function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Get escalation level display text
export function getEscalationLevelText(level: string): string {
  const levels: Record<string, string> = {
    level_4_emergency: 'Emergency',
    level_3_high: 'High Risk',
    level_2_moderate: 'Moderate',
    level_1_low: 'Low',
  };
  return levels[level] || level;
}

// Get escalation level color
export function getEscalationLevelColor(level: string): string {
  return ESCALATION_COLORS[level as keyof typeof ESCALATION_COLORS] || CITTAA_COLORS.warmGray;
}

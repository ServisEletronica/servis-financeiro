/* General utility functions (exposes cn) */
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merges multiple class names into a single string
 * @param inputs - Array of class names
 * @returns Merged class names
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Converte uma cor hex para RGB
 * @param hex - Cor em formato hex (#RRGGBB ou #RGB)
 * @returns Objeto com valores RGB
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex) ||
                 /^#?([a-f\d])([a-f\d])([a-f\d])$/i.exec(hex)
  
  if (!result) return null
  
  if (result[1].length === 1) {
    // Formato #RGB
    return {
      r: parseInt(result[1] + result[1], 16),
      g: parseInt(result[2] + result[2], 16),
      b: parseInt(result[3] + result[3], 16)
    }
  }
  
  // Formato #RRGGBB
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  }
}

/**
 * Calcula a luminância relativa de uma cor
 * @param r - Valor vermelho (0-255)
 * @param g - Valor verde (0-255)
 * @param b - Valor azul (0-255)
 * @returns Luminância relativa (0-1)
 */
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}

/**
 * Determina se deve usar texto claro ou escuro baseado na cor de fundo
 * @param backgroundColor - Cor de fundo em hex
 * @returns Cor do texto ideal ('#ffffff' ou '#000000')
 */
export function getContrastTextColor(backgroundColor: string): string {
  if (!backgroundColor) return '#000000'
  
  const rgb = hexToRgb(backgroundColor)
  if (!rgb) return '#000000'
  
  const luminance = getLuminance(rgb.r, rgb.g, rgb.b)
  
  // Se a luminância for baixa (cor escura), usar texto claro
  // Se a luminância for alta (cor clara), usar texto escuro
  return luminance > 0.5 ? '#000000' : '#ffffff'
}

/**
 * Adapta uma cor para o tema atual (light/dark mode)
 * @param color - Cor original em hex
 * @param isDarkMode - Se está no modo escuro
 * @returns Objeto com cores adaptadas para o tema
 */
export function getThemeAdaptedQueueColors(color: string, isDarkMode: boolean): {
  backgroundColor: string
  borderColor: string
  textColor: string
} {
  if (!color) {
    return {
      backgroundColor: 'transparent',
      borderColor: 'currentColor',
      textColor: 'currentColor'
    }
  }

  const rgb = hexToRgb(color)
  if (!rgb) {
    return {
      backgroundColor: 'transparent',
      borderColor: color,
      textColor: 'currentColor'
    }
  }

  if (isDarkMode) {
    // Tema escuro: usar a cor com opacidade baixa e border mais visível
    return {
      backgroundColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.15)`,
      borderColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.6)`,
      textColor: `rgb(${Math.min(255, rgb.r + 60)}, ${Math.min(255, rgb.g + 60)}, ${Math.min(255, rgb.b + 60)})`
    }
  } else {
    // Tema claro: usar a cor com opacidade baixa e texto mais escuro
    return {
      backgroundColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.1)`,
      borderColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.4)`,
      textColor: `rgb(${Math.max(0, rgb.r - 80)}, ${Math.max(0, rgb.g - 80)}, ${Math.max(0, rgb.b - 80)})`
    }
  }
}

/**
 * Gera cores para badges de tags seguindo o padrão visual dos templates
 * Cores mais sólidas e visíveis, similar ao estilo bg-{color}-100 text-{color}-800
 * @param color - Cor original em hex
 * @param isDarkMode - Se está no modo escuro
 * @returns Objeto com cores adaptadas para badges
 */
export function getTagBadgeColors(color: string, isDarkMode: boolean): {
  backgroundColor: string
  borderColor: string
  textColor: string
} {
  if (!color) {
    return {
      backgroundColor: isDarkMode ? 'rgb(23, 23, 23)' : 'rgb(243, 244, 246)',
      borderColor: isDarkMode ? 'rgb(38, 38, 38)' : 'rgb(229, 231, 235)',
      textColor: isDarkMode ? 'rgb(212, 212, 212)' : 'rgb(31, 41, 55)'
    }
  }

  const rgb = hexToRgb(color)
  if (!rgb) {
    return {
      backgroundColor: isDarkMode ? 'rgb(23, 23, 23)' : 'rgb(243, 244, 246)',
      borderColor: color,
      textColor: 'currentColor'
    }
  }

  if (isDarkMode) {
    // Dark mode: fundo escuro com a cor (similar a bg-{color}-900)
    // Texto claro com a cor (similar a text-{color}-300)
    return {
      backgroundColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.25)`,
      borderColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.4)`,
      textColor: `rgb(${Math.min(255, rgb.r + 100)}, ${Math.min(255, rgb.g + 100)}, ${Math.min(255, rgb.b + 100)})`
    }
  } else {
    // Light mode: fundo claro com a cor (similar a bg-{color}-100)
    // Texto escuro com a cor (similar a text-{color}-800)
    return {
      backgroundColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.15)`,
      borderColor: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.3)`,
      textColor: `rgb(${Math.max(0, rgb.r - 100)}, ${Math.max(0, rgb.g - 100)}, ${Math.max(0, rgb.b - 100)})`
    }
  }
}

// Add any other utility functions here

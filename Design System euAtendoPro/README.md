# Design System euAtendoPro

Este é o Design System extraído do sistema euAtendoPro, contendo todos os componentes de tema, cores, modo claro/escuro, toast e alert.

## Estrutura de Pastas

```
Design System euAtendoPro/
├── components/
│   ├── providers/
│   │   ├── ThemeProvider.tsx          # Provider principal do tema
│   │   └── CustomToastProvider.tsx    # Provider de toasts customizados
│   ├── ui/
│   │   ├── toast-new.tsx              # Toast moderno com progresso
│   │   ├── toast.tsx                  # Toast base (Radix UI)
│   │   ├── toast-custom.tsx           # Toast customizado
│   │   ├── toaster.tsx                # Renderizador de toasts
│   │   ├── sonner.tsx                 # Integração com Sonner
│   │   ├── alert.tsx                  # Alert com notificações
│   │   ├── alert-dialog.tsx           # Dialog de alert (Radix UI)
│   │   ├── alert-info.tsx             # Alert informativo
│   │   ├── button.tsx                 # Botão base
│   │   ├── dialog.tsx                 # Dialog base
│   │   ├── tooltip.tsx                # Tooltip
│   │   ├── card.tsx                   # Card
│   │   ├── input.tsx                  # Input
│   │   ├── label.tsx                  # Label
│   │   ├── badge.tsx                  # Badge
│   │   └── separator.tsx              # Separator
│   └── CustomVariantToast.tsx         # Toast com variantes customizadas
├── hooks/
│   ├── use-toast.ts                   # Hook principal de toast
│   └── useProgressTimer.ts            # Hook para timer com progresso
├── lib/
│   ├── utils.ts                       # Utilitários (cn, etc)
│   └── toast.ts                       # Serviço de toast
└── styles/
    └── main.css                       # Estilos globais e variáveis CSS
```

---

## Passo 1: Instalação de Dependências

Instale as dependências necessárias no seu novo projeto:

```bash
npm install @radix-ui/react-toast @radix-ui/react-alert-dialog @radix-ui/react-dialog @radix-ui/react-tooltip @radix-ui/react-slot lucide-react sonner class-variance-authority clsx tailwind-merge
```

### Dependências Dev (se ainda não tiver):

```bash
npm install -D tailwindcss postcss autoprefixer
```

---

## Passo 2: Configuração do Tailwind CSS

Atualize seu `tailwind.config.js` ou `tailwind.config.ts`:

```javascript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};

export default config;
```

---

## Passo 3: Importar os Estilos Globais

No seu arquivo principal (`main.tsx`, `index.tsx`, ou `_app.tsx`), importe o CSS:

```typescript
import './styles/main.css'
// ou o caminho onde você colocou o main.css do Design System
```

---

## Passo 4: Configurar Path Aliases

No seu `tsconfig.json`, adicione:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Se estiver usando Vite, adicione no `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

---

## Passo 5: Copiar os Arquivos

Copie toda a pasta `Design System euAtendoPro` para dentro do seu projeto. Sugestão de estrutura:

```
seu-projeto/
├── src/
│   ├── components/
│   │   ├── providers/
│   │   │   ├── ThemeProvider.tsx
│   │   │   └── CustomToastProvider.tsx
│   │   ├── ui/
│   │   │   └── [todos os componentes]
│   │   └── CustomVariantToast.tsx
│   ├── hooks/
│   │   ├── use-toast.ts
│   │   └── useProgressTimer.ts
│   ├── lib/
│   │   ├── utils.ts
│   │   └── toast.ts
│   └── styles/
│       └── main.css
```

---

## Passo 6: Setup no App Principal

No seu arquivo principal de aplicação (ex: `App.tsx`, `_app.tsx`, ou `layout.tsx`):

```typescript
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { CustomToastProvider } from '@/components/providers/CustomToastProvider'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Toaster } from '@/components/ui/toaster'
import { Sonner } from '@/components/ui/sonner'

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <TooltipProvider>
        <CustomToastProvider>
          <Toaster />
          <Sonner />

          {/* Seu conteúdo aqui */}
          <YourAppContent />

        </CustomToastProvider>
      </TooltipProvider>
    </ThemeProvider>
  )
}

export default App
```

---

## Uso dos Componentes

### 1. Mudar Tema (Light/Dark/System)

```typescript
import { useTheme } from '@/components/providers/ThemeProvider'

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <select value={theme} onChange={(e) => setTheme(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="system">System</option>
    </select>
  )
}
```

### 2. Usar Toast Customizado

```typescript
import { useCustomToast } from '@/components/providers/CustomToastProvider'

function MyComponent() {
  const { showToast } = useCustomToast()

  const handleSuccess = () => {
    showToast('success', 'Sucesso!', 'Operação realizada com sucesso')
  }

  const handleError = () => {
    showToast('error', 'Erro!', 'Algo deu errado')
  }

  const handleWarning = () => {
    showToast('warning', 'Atenção!', 'Verifique os dados')
  }

  const handleInfo = () => {
    showToast('info', 'Informação', 'Dados atualizados')
  }

  return (
    <div>
      <button onClick={handleSuccess}>Mostrar Sucesso</button>
      <button onClick={handleError}>Mostrar Erro</button>
      <button onClick={handleWarning}>Mostrar Aviso</button>
      <button onClick={handleInfo}>Mostrar Info</button>
    </div>
  )
}
```

### 3. Usar Toast via Serviço

```typescript
import {
  showCustomToastSuccess,
  showCustomToastError,
  showCustomToastWarning,
  showCustomToastInfo
} from '@/lib/toast'

// Em qualquer lugar do código
showCustomToastSuccess('Sucesso!', 'Dados salvos')
showCustomToastError('Erro!', 'Falha ao salvar')
showCustomToastWarning('Atenção!', 'Campos obrigatórios')
showCustomToastInfo('Info', 'Processando...')
```

### 4. Usar Alert de Notificação

```typescript
import { useAlert } from '@/components/ui/alert'

function MyComponent() {
  const { showNotification } = useAlert()

  const handleClick = () => {
    showNotification('success', 'Operação concluída com sucesso!')
    // Tipos: 'success' | 'error' | 'info'
  }

  return <button onClick={handleClick}>Executar</button>
}
```

### 5. Usar Alert de Confirmação

```typescript
import { useAlert } from '@/components/ui/alert'

function MyComponent() {
  const { showConfirmation } = useAlert()

  const handleDelete = () => {
    showConfirmation(
      'Confirmar exclusão?',
      'Esta ação não pode ser desfeita.',
      () => {
        // Callback quando confirmar
        console.log('Item deletado')
      },
      () => {
        // Callback quando cancelar (opcional)
        console.log('Cancelado')
      }
    )
  }

  return <button onClick={handleDelete}>Deletar</button>
}
```

### 6. Usar Sonner Toast

```typescript
import { toast } from 'sonner'

function MyComponent() {
  const handleClick = () => {
    toast.success('Sucesso!')
    toast.error('Erro!')
    toast.info('Informação')
    toast.warning('Aviso')
  }

  return <button onClick={handleClick}>Mostrar Toast</button>
}
```

### 7. Usar AlertInfo (Banners)

```typescript
import { AlertInfo } from '@/components/ui/alert-info'

function MyComponent() {
  return (
    <div>
      <AlertInfo variant="info" title="Informação">
        Conteúdo informativo aqui
      </AlertInfo>

      <AlertInfo variant="warning" title="Atenção">
        Aviso importante
      </AlertInfo>

      <AlertInfo variant="success" title="Sucesso">
        Operação realizada
      </AlertInfo>

      <AlertInfo variant="error" title="Erro">
        Algo deu errado
      </AlertInfo>
    </div>
  )
}
```

---

## Customização de Cores Primárias

O ThemeProvider suporta cores primárias customizadas via JWT. Se você quiser usar cores customizadas:

### Método 1: Via Token JWT

O ThemeProvider automaticamente decodifica o token JWT do localStorage (chave `token`) e procura pela propriedade `clientPrimaryColor` (formato hex, ex: `#3b82f6`).

```typescript
// Exemplo de payload JWT
{
  "userId": "123",
  "clientPrimaryColor": "#3b82f6"
}
```

### Método 2: Manualmente via CSS Variables

Você pode definir manualmente as cores no seu CSS:

```css
:root {
  --primary: 244 47% 37%;
  --primary-foreground: 0 0% 98%;
}

.dark {
  --primary: 244 47% 52%;
  --primary-foreground: 0 0% 10%;
}
```

---

## Variáveis CSS Disponíveis

O Design System usa as seguintes variáveis CSS que você pode customizar:

### Cores Base:
- `--background`: Cor de fundo principal
- `--foreground`: Cor do texto principal
- `--primary`: Cor primária
- `--primary-foreground`: Cor do texto sobre primária
- `--secondary`: Cor secundária
- `--secondary-foreground`: Cor do texto sobre secundária
- `--muted`: Cor neutra
- `--muted-foreground`: Cor do texto neutro
- `--accent`: Cor de destaque
- `--accent-foreground`: Cor do texto sobre destaque
- `--destructive`: Cor destrutiva (erro)
- `--destructive-foreground`: Cor do texto sobre destrutiva

### Componentes:
- `--card`: Cor de fundo do card
- `--card-foreground`: Cor do texto do card
- `--popover`: Cor de fundo do popover
- `--popover-foreground`: Cor do texto do popover
- `--border`: Cor da borda
- `--input`: Cor da borda do input
- `--ring`: Cor do foco

### Outros:
- `--radius`: Border radius padrão (0.5rem)

---

## Componentes UI Incluídos

- **Button**: Botão com variantes (default, destructive, outline, secondary, ghost, link)
- **Card**: Card com header, content, footer
- **Dialog**: Modal dialog
- **AlertDialog**: Dialog de confirmação
- **Tooltip**: Tooltip
- **Badge**: Badge com variantes
- **Separator**: Linha separadora
- **Input**: Input de texto
- **Label**: Label para inputs

---

## Observações Importantes

1. **Fontes**: O `main.css` importa as fontes Geist, Lora e Fira Code do Google Fonts. Certifique-se de que seu projeto tem acesso à internet ou baixe as fontes localmente.

2. **Radix UI**: A maioria dos componentes usa Radix UI como base. Certifique-se de instalar todas as dependências necessárias.

3. **Lucide Icons**: Os ícones usam a biblioteca `lucide-react`. Se quiser usar outros ícones, ajuste os imports nos componentes.

4. **JWT Decode**: Se não for usar cores customizadas via JWT, você pode remover a dependência `jwt-decode` do ThemeProvider ou simplesmente não configurar o token.

5. **LocalStorage**: O tema é salvo no localStorage com a chave `vite-ui-theme`. Você pode alterar isso no ThemeProvider.

---

## Estrutura Mínima para Funcionar

Se você quiser apenas o básico (tema + toast simples), os arquivos essenciais são:

1. `styles/main.css` (obrigatório)
2. `components/providers/ThemeProvider.tsx` (obrigatório)
3. `lib/utils.ts` (obrigatório)
4. `components/ui/sonner.tsx` (toast simples)
5. `components/ui/button.tsx` (componente comum)

Com esses 5 arquivos você já tem tema claro/escuro funcional e toasts básicos.

---

## Suporte e Customização

Este Design System foi extraído do euAtendoPro e pode ser livremente customizado para suas necessidades. As cores, espaçamentos e componentes podem ser ajustados editando:

- `styles/main.css` para variáveis CSS
- Componentes individuais em `components/ui/`
- `ThemeProvider.tsx` para lógica de tema

---

## Exemplo Completo de Setup

```typescript
// main.tsx ou index.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/main.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

```typescript
// App.tsx
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { CustomToastProvider } from '@/components/providers/CustomToastProvider'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Toaster } from '@/components/ui/toaster'
import { Sonner } from '@/components/ui/sonner'
import { Button } from '@/components/ui/button'
import { useCustomToast } from '@/components/providers/CustomToastProvider'
import { useTheme } from '@/components/providers/ThemeProvider'

function AppContent() {
  const { showToast } = useCustomToast()
  const { theme, setTheme } = useTheme()

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <h1 className="text-3xl font-bold mb-4">Design System euAtendoPro</h1>

      <div className="space-y-4">
        <div>
          <label>Tema: </label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="ml-2 border rounded px-2 py-1"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>

        <div className="space-x-2">
          <Button onClick={() => showToast('success', 'Sucesso!', 'Teste')}>
            Toast Sucesso
          </Button>
          <Button onClick={() => showToast('error', 'Erro!', 'Teste')} variant="destructive">
            Toast Erro
          </Button>
          <Button onClick={() => showToast('warning', 'Aviso!', 'Teste')} variant="secondary">
            Toast Aviso
          </Button>
          <Button onClick={() => showToast('info', 'Info!', 'Teste')} variant="outline">
            Toast Info
          </Button>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <TooltipProvider>
        <CustomToastProvider>
          <Toaster />
          <Sonner />
          <AppContent />
        </CustomToastProvider>
      </TooltipProvider>
    </ThemeProvider>
  )
}

export default App
```

---

Pronto! Com este guia você consegue replicar todo o Design System do euAtendoPro em qualquer outro projeto React/TypeScript.

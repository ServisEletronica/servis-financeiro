# 🚀 Template React + Vite + TypeScript + Shadcn UI

Template moderno e completo para iniciar projetos React com visual profissional, incluindo sidebar responsiva, sistema de autenticação, dashboard com gráficos e tema dark/light.

## ✨ Features

- ⚡ **Vite** - Build tool ultra rápido
- ⚛️ **React 19** - Biblioteca UI moderna
- 🎨 **Shadcn UI** - Componentes UI de alta qualidade
- 🎭 **Tailwind CSS** - Estilização utilitária
- 📱 **Responsivo** - Design mobile-first
- 🌓 **Dark Mode** - Tema claro/escuro
- 🔐 **Autenticação** - Sistema de login mock
- 📊 **Dashboard** - Gráficos com Recharts
- 🎯 **TypeScript** - Tipagem estática
- 🧭 **React Router** - Roteamento SPA

## 📦 Estrutura do Projeto

```
projeto-teste/
├── src/
│   ├── components/
│   │   ├── ui/              # ~30 componentes Shadcn UI
│   │   ├── AppSidebar.tsx   # Sidebar completa e responsiva
│   │   ├── Layout.tsx       # Layout principal
│   │   ├── MobileNav.tsx    # Navegação mobile
│   │   └── ThemeProvider.tsx # Sistema de temas
│   ├── context/
│   │   ├── auth-context.tsx      # Autenticação (mock)
│   │   └── sidebar-context.tsx   # Estado da sidebar
│   ├── hooks/
│   │   └── use-mobile.tsx        # Hook mobile detection
│   ├── lib/
│   │   ├── utils.ts         # Utilitários (cn, etc)
│   │   └── toast.ts         # Sistema de toast
│   ├── pages/
│   │   ├── Login.tsx        # Página de login
│   │   ├── Dashboard.tsx    # Dashboard com gráficos
│   │   └── NotFound.tsx     # Página 404
│   ├── App.tsx              # Router e providers
│   ├── main.tsx             # Entry point
│   └── main.css             # Estilos globais + tema
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## 🛠️ Instalação

### Pré-requisitos

- Node.js 18+
- npm ou yarn ou pnpm

### Passos

1. **Clone ou copie o projeto**

```bash
cd projeto-teste
```

2. **Instale as dependências**

```bash
npm install
```

3. **Inicie o servidor de desenvolvimento**

```bash
npm run dev
```

4. **Acesse no navegador**

```
http://localhost:8080
```

## 🔑 Login

O sistema usa autenticação mock. Use as seguintes credenciais:

- **Email:** `admin@teste.com` (ou qualquer email)
- **Senha:** `12345678`

> **Nota:** Qualquer email é aceito, mas a senha deve ser exatamente `12345678`

## 📝 Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev          # Inicia servidor dev em localhost:8080

# Build
npm run build        # Gera build de produção

# Preview
npm run preview      # Preview do build de produção
```

## 🎨 Customização

### Cores do Tema

Edite as variáveis CSS em `src/main.css`:

```css
:root {
  --primary: 260.4000 22.9358% 57.2549%;
  --secondary: 258.9474 33.3333% 88.8235%;
  /* ... outras cores */
}
```

### Adicionar Novas Páginas

1. Crie o componente em `src/pages/`
2. Adicione a rota em `src/App.tsx`:

```tsx
<Route path="/nova-pagina" element={<NovaPagina />} />
```

3. Adicione link na sidebar em `src/components/AppSidebar.tsx`:

```tsx
const MAIN_NAV_ITEMS = [
  { label: 'Dashboard', href: '/panel', icon: LayoutDashboard },
  { label: 'Nova Página', href: '/nova-pagina', icon: SeuIcone },
]
```

### Modificar Dados do Dashboard

Edite os dados mock em `src/pages/Dashboard.tsx`:

```tsx
const MOCK_STATS = {
  activeChats: { count: 24, change: 12.5 },
  // ... seus dados
}
```

## 🔐 Sistema de Autenticação

O template inclui um sistema de autenticação mock completo:

- ✅ Login com persistência (localStorage)
- ✅ Rotas protegidas
- ✅ Logout
- ✅ Loading states

Para integrar com uma API real, edite `src/context/auth-context.tsx`.

## 🎯 Componentes Disponíveis

O projeto inclui todos os componentes Shadcn UI:

- Avatar, Badge, Button, Card
- Checkbox, Dialog, Dropdown Menu
- Input, Label, Select, Switch
- Table, Tabs, Toast, Tooltip
- E muito mais...

Veja exemplos de uso em `src/pages/Dashboard.tsx` e `src/pages/Login.tsx`.

## 📱 Responsividade

O template é 100% responsivo:

- **Mobile:** Navegação via Sheet (menu hambúrguer)
- **Tablet/Desktop:** Sidebar colapsável
- **Breakpoints:** Tailwind padrão (sm, md, lg, xl, 2xl)

## 🌓 Dark Mode

O tema dark/light é automático e sincronizado com o sistema operacional. O usuário pode alternar manualmente.

Para forçar um tema:

```tsx
// Em qualquer componente
import { useTheme } from '@/components/ThemeProvider'

const { setTheme } = useTheme()
setTheme('dark') // ou 'light' ou 'system'
```

## 🚀 Deploy

### Build

```bash
npm run build
```

Os arquivos estarão em `dist/`.

### Opções de Deploy

- **Vercel:** Conecte o repo e deploy automático
- **Netlify:** Arraste a pasta `dist/`
- **GitHub Pages:** Configure no repositório
- **Docker:** Sirva os arquivos estáticos

## 🔧 Tecnologias

- [React 19](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn UI](https://ui.shadcn.com/)
- [React Router](https://reactrouter.com/)
- [Recharts](https://recharts.org/)
- [Lucide Icons](https://lucide.dev/)

## 📄 Licença

Livre para uso pessoal e comercial.

## 🤝 Contribuindo

Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar novos componentes
3. Melhorar a documentação
4. Reportar bugs

## 💡 Dicas

- Use `<Tooltip>` para melhorar UX na sidebar colapsada
- Prefira `<Card>` para organizar seções
- Use `showCustomToastSuccess()` para feedbacks
- Mantenha a consistência de cores usando variáveis CSS

## 🆘 Problemas Comuns

### Erro de importação de componentes UI

Execute `npm install` novamente.

### Tema não muda

Limpe o localStorage e recarregue a página.

### Build falha

Verifique se todas as dependências estão instaladas com `npm install`.

---

**Feito com ❤️ usando React + Vite + Shadcn UI**

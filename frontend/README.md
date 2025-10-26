# Prompt Firewall Frontend

A modern, responsive frontend for the Prompt Firewall MVP built with Next.js and Tailwind CSS.

## 🚀 Features

- **User-Facing Demo UI**: Clean interface for testing prompt analysis
- **Admin Console**: Comprehensive management interface
- **Multi-tenant Support**: Secure tenant isolation and management
- **Real-time Analysis**: Instant feedback with detailed risk assessments
- **Responsive Design**: Mobile-first, accessible design
- **Security**: Bearer token authentication and secure API integration

## 🏗️ Architecture

```
frontend/
├── pages/                 # Next.js pages
│   ├── index.js          # Demo UI
│   ├── admin/            # Admin console pages
│   └── api/              # API proxy routes
├── components/           # React components
│   ├── Layout.js         # Shared layout
│   ├── PromptForm.js     # Demo form
│   ├── ResultDisplay.js  # Results visualization
│   └── ...               # Other components
├── lib/                  # Utilities and configuration
│   ├── auth.js          # NextAuth configuration
│   ├── api.js           # API client utilities
│   └── constants.js     # Frontend constants
├── styles/               # Global styles
└── public/              # Static assets
```

## 🛠️ Tech Stack

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js
- **State Management**: React Hooks
- **Notifications**: React Hot Toast
- **Icons**: Emoji and Unicode symbols
- **Charts**: Recharts (for analytics)

## 📦 Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (see backend README)

### Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   ```
   http://localhost:3000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file with:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# Optional
NODE_ENV=development
```

### Backend Integration

The frontend integrates with the FastAPI backend through:

- **API Proxy Routes**: `/pages/api/*` proxy requests to backend
- **Authentication**: Bearer token format (`tenant_id:api_key`)
- **Error Handling**: Comprehensive error management
- **Type Safety**: Consistent data structures

## 🎨 UI Components

### Core Components

- **Layout**: Responsive navigation and footer
- **PromptForm**: Secure prompt input with validation
- **ResultDisplay**: Clear decision and risk visualization
- **RiskIndicator**: Visual risk severity indicators
- **LogTable**: Advanced filtering and export capabilities
- **RuleEditor**: Comprehensive rule management

### Design System

- **Colors**: Primary blue, semantic colors for states
- **Typography**: Inter font family with proper weights
- **Spacing**: Consistent 8px base unit
- **Components**: Reusable, accessible components
- **Responsive**: Mobile-first design approach

## 🔐 Authentication

### NextAuth.js Integration

- **Credentials Provider**: Tenant name/password authentication
- **JWT Strategy**: Secure session management
- **API Integration**: Backend login endpoint integration
- **Session Management**: Automatic token refresh

### Security Features

- **Bearer Tokens**: `tenant_id:api_key` format
- **HTTPS Enforcement**: Production security
- **Input Validation**: Client-side validation
- **Error Handling**: Secure error messages

## 📱 Pages

### Demo UI (`/`)

- **Prompt Input**: Secure form with tenant credentials
- **Real-time Analysis**: Instant security assessment
- **Risk Visualization**: Clear decision and risk indicators
- **Examples**: Built-in test cases for PII and injection

### Admin Console (`/admin`)

- **Dashboard**: Overview and quick stats
- **Tenant Management**: Create and manage tenants
- **Rule Management**: Configure detection rules
- **Log Viewer**: Monitor security events
- **Analytics**: Security metrics and trends

## 🔌 API Integration

### Proxy Routes

All API calls go through Next.js API routes for security:

- `/api/query` → `/v1/query`
- `/api/tenants` → `/v1/tenants`
- `/api/rules` → `/v1/rules`
- `/api/logs` → `/v1/logs`

### Error Handling

- **Network Errors**: Graceful fallbacks
- **API Errors**: User-friendly messages
- **Validation**: Client-side validation
- **Loading States**: User feedback

## 🎯 Features

### User-Facing Demo

- ✅ Clean, accessible interface
- ✅ Real-time prompt analysis
- ✅ Risk visualization
- ✅ Mobile-responsive design
- ✅ Built-in examples

### Admin Console

- ✅ Secure authentication
- ✅ Tenant management
- ✅ Rule configuration
- ✅ Log monitoring
- ✅ Export functionality

### Security

- ✅ Bearer token authentication
- ✅ Input validation
- ✅ Secure API integration
- ✅ Error handling
- ✅ HTTPS enforcement

## 🚀 Deployment

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
npm start
```

### Vercel Deployment

```bash
vercel --prod
```

### Environment Setup

1. Set production environment variables
2. Configure API URLs
3. Generate secure secrets
4. Enable HTTPS

## 🧪 Testing

### Manual Testing

1. **Demo UI**: Test with various prompts
2. **Admin Console**: Test all management features
3. **Authentication**: Test login/logout flows
4. **Responsive**: Test on different screen sizes

### Test Cases

- **PII Detection**: Emails, SSNs, phone numbers
- **Injection Attempts**: Various injection patterns
- **Authentication**: Login/logout flows
- **Error Handling**: Network and API errors

## 📊 Performance

### Optimization

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js image optimization
- **Bundle Analysis**: Webpack bundle analyzer
- **Caching**: Static and API response caching

### Metrics

- **Core Web Vitals**: LCP, FID, CLS
- **Bundle Size**: Optimized JavaScript bundles
- **Load Times**: Fast initial page loads
- **API Performance**: Efficient API calls

## 🔧 Development

### Scripts

```bash
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint checking
npm run type-check   # TypeScript checking
```

### Code Style

- **ESLint**: Configured for Next.js
- **Prettier**: Code formatting
- **TypeScript**: Type safety (optional)
- **Conventions**: Consistent naming and structure

## 🐛 Troubleshooting

### Common Issues

1. **API Connection**: Check `NEXT_PUBLIC_API_URL`
2. **Authentication**: Verify backend is running
3. **Build Errors**: Check Node.js version
4. **Styling**: Ensure Tailwind CSS is configured

### Debug Mode

Enable debug mode in development:

```bash
NODE_ENV=development npm run dev
```

## 📚 Documentation

### API Documentation

- **Backend API**: See backend README
- **Frontend API**: Proxy routes documentation
- **Authentication**: NextAuth.js configuration
- **Components**: Component documentation

### Resources

- **Next.js**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **NextAuth.js**: https://next-auth.js.org/
- **React**: https://reactjs.org/docs

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards

- **ESLint**: Follow configured rules
- **Components**: Use functional components
- **Styling**: Use Tailwind CSS classes
- **Testing**: Test all new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js Team**: For the excellent framework
- **Tailwind CSS**: For the utility-first CSS framework
- **NextAuth.js**: For authentication solutions
- **React Team**: For the component library

---

**Built with ❤️ for AI Security**

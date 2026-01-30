# JobMatch AI - Frontend

Modern, glassmorphic UI for AI-powered resume-job matching built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Glassmorphic Design** - Apple-inspired dark theme with glass effects
- ⚡ **Next.js 15** - Latest React framework with App Router
- 🎭 **Framer Motion** - Smooth animations and transitions
- 📱 **Responsive** - Works on all devices
- 🔄 **Real-time Processing** - Live resume analysis and job matching
- ✨ **Shimmer Loading** - Beautiful loading states
- 🎯 **Clean Architecture** - Organized, maintainable code structure

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── globals.css        # Global styles
├── components/
│   ├── features/          # Feature components
│   │   ├── FileUpload.tsx
│   │   ├── ResumeAnalysis.tsx
│   │   └── JobMatches.tsx
│   ├── ui/                # UI components
│   │   └── Shimmer.tsx
│   └── layout/            # Layout components
├── lib/
│   ├── api/               # API client
│   │   └── client.ts
│   ├── hooks/             # Custom hooks
│   │   └── useResumeProcessor.ts
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── utils/             # Utility functions
│   │   └── index.ts
│   └── constants/         # Constants
│       └── index.ts
└── public/                # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Usage

1. **Upload Resume** - Drag & drop or click to upload PDF resume
2. **View Analysis** - See AI-powered resume analysis with score and feedback
3. **Browse Matches** - View ranked job matches with explanations
4. **Apply** - Click "View on Telegram" to apply directly

## Design System

### Colors

- **Background**: Dark gradient (#0a0a0a to #1a1a2e)
- **Glass Cards**: White/5 with backdrop blur
- **Accents**: Blue (#3b82f6) and Purple (#8b5cf6)

### Components

- **Glass Card**: Glassmorphic card with blur effect
- **Glass Button**: Interactive button with glass effect
- **Score Badge**: Gradient badge for match scores
- **Shimmer**: Loading skeleton with shimmer animation

### Animations

- **Fade In**: Smooth opacity transitions
- **Slide Up**: Content slides up on mount
- **Scale**: Hover scale effects
- **Shimmer**: Loading shimmer animation
- **Float**: Floating background orbs

## API Integration

The frontend communicates with the backend API:

- `POST /process_resume` - Upload and analyze resume
- `POST /match_resume` - Match resume with jobs
- `GET /cache/info` - Get cache status
- `GET /health` - Check API health

## Performance

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Components load on demand
- **Caching**: Client-side caching for better UX

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Development

```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t jobmatch-frontend .

# Run container
docker run -p 3000:3000 jobmatch-frontend
```

## Troubleshooting

### API Connection Issues

- Ensure backend is running on http://localhost:8000
- Check CORS settings in backend
- Verify `.env.local` has correct API_URL

### Build Errors

- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

## Contributing

1. Follow the clean architecture pattern
2. Use TypeScript for type safety
3. Add proper error handling
4. Write meaningful component names
5. Keep components small and focused

## License

MIT

# SAHAYAK-AI Frontend

Next.js + React + TypeScript frontend for the SAHAYAK-AI disaster response platform.

## Setup

```bash
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

## Project Structure

```
src/
├── app/              # Next.js app directory
│   ├── page.tsx     # Main page
│   ├── layout.tsx   # Root layout
│   └── globals.css  # Global styles
├── components/      # React components
├── lib/            # Utility functions
│   ├── api.ts      # API client
│   └── store.ts    # Zustand stores
```

## Features

- ✅ Real-time emergency query processing
- ✅ Voice input support (future)
- ✅ Location-based POI search
- ✅ Route guidance to nearest shelter
- ✅ Safety verification with redline checks
- ✅ Responsive design with Tailwind CSS

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

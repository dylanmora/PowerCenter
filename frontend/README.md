# PowerCenter Frontend

A modern, professional React TypeScript application for powerlifting meet analysis and management.

## Features

- **Modern React Architecture**: Built with React 19, TypeScript, and functional components
- **Clean Component Structure**: Modular, reusable components with clear separation of concerns
- **Professional UI/UX**: Beautiful, responsive design using Tailwind CSS
- **Type Safety**: Full TypeScript implementation with proper interfaces and types
- **Error Handling**: Robust error handling and user feedback
- **Performance Optimized**: Efficient rendering and state management

## Architecture

```
src/
├── components/          # Reusable UI components
│   ├── Dashboard.tsx    # Main dashboard view
│   ├── Header.tsx       # Application header
│   ├── Sidebar.tsx      # Navigation sidebar
│   ├── MeetAnalyzer.tsx # Meet analysis form
│   ├── StatsCard.tsx    # Statistics display component
│   ├── TopPerformers.tsx # Top performers list
│   └── PlaceholderTab.tsx # Placeholder for future features
├── types/               # TypeScript type definitions
│   └── meet.ts         # Meet-related interfaces
├── utils/               # Utility functions
│   └── formatters.ts   # Data formatting utilities
├── config/              # Configuration files
│   └── api.ts          # API configuration
├── App.tsx              # Main application component
└── index.tsx            # Application entry point
```

## Technology Stack

- **React 19**: Latest React with hooks and functional components
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful, customizable icons
- **Modern Fetch API**: Native HTTP requests with proper error handling

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view the app

### Building for Production

```bash
npm run build
```

## Key Components

### App.tsx
The main application component that orchestrates the entire application. Features:
- Clean state management
- Tab-based navigation
- Component composition

### Dashboard.tsx
The primary dashboard view containing:
- Statistics overview cards
- Meet analysis form
- Results display
- Error handling

### MeetAnalyzer.tsx
Handles meet URL analysis with:
- Form validation
- API integration
- Loading states
- Error handling

## Design System

The application uses a consistent design system with:
- **Color Palette**: Red (#DC2626) as primary, gray scale for UI
- **Typography**: Clean, readable fonts with proper hierarchy
- **Spacing**: Consistent 6-unit grid system
- **Components**: Reusable, accessible components

## Configuration

API configuration is centralized in `src/config/api.ts`:
- Environment-based API URLs
- Request timeouts
- Retry logic

## Data Flow

1. User enters meet URL in MeetAnalyzer
2. Form validates input and makes API request
3. Results are processed and displayed in Dashboard
4. Error states are handled gracefully

## Code Quality

- **TypeScript**: Full type safety
- **ESLint**: Code linting and formatting
- **Component Structure**: Single responsibility principle
- **Error Boundaries**: Graceful error handling
- **Performance**: Optimized rendering and state updates

## Future Enhancements

- [ ] Advanced analytics and charts
- [ ] Meet management system
- [ ] Lifter database
- [ ] User authentication
- [ ] Real-time updates
- [ ] Mobile optimization




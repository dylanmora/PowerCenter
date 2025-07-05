# PowerCenter - Technical Architecture

## Overview

PowerCenter is a full-stack web application for powerlifting meet analysis and lifter database management. The application provides real-time analysis of powerlifting meets from LiftingCast, comprehensive lifter search capabilities, and performance analytics.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │ Tailwind│            │ Pandas  │            │LiftingCast│
    │   CSS   │            │  Data   │            │   Web    │
    └─────────┘            │ Manager │            └─────────┘
                           └─────────┘
                                  │
                           ┌────▼────┐
                           │OpenPower│
                           │Lifting  │
                           │  Data   │
                           └─────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **Icons**: Lucide React
- **HTTP Client**: Native Fetch API
- **Build Tool**: Create React App
- **State Management**: React Hooks (useState, useEffect)

### Backend
- **Framework**: FastAPI (Python)
- **Data Processing**: Pandas
- **Web Scraping**: Selenium WebDriver
- **Data Storage**: Parquet files with JSON metadata
- **HTTP Server**: Uvicorn
- **CORS**: Enabled for frontend integration

### External Dependencies
- **LiftingCast**: Meet data source
- **OpenPowerlifting**: Historical lifter database
- **ChromeDriver**: Web scraping automation

## Frontend Architecture

### Component Structure

```
src/
├── components/              # Reusable UI components
│   ├── Dashboard.tsx        # Main dashboard view
│   ├── Header.tsx           # Application header
│   ├── Sidebar.tsx          # Navigation sidebar
│   ├── MeetAnalyzer.tsx     # Meet analysis form
│   ├── StatsCard.tsx        # Statistics display
│   ├── TopPerformers.tsx    # Top performers list
│   ├── LifterSearch.tsx     # Lifter search form
│   ├── LifterCard.tsx       # Individual lifter display
│   ├── LiftersPage.tsx      # Main lifter page
│   └── PlaceholderTab.tsx   # Placeholder components
├── types/                   # TypeScript interfaces
│   ├── meet.ts             # Meet-related types
│   └── lifter.ts           # Lifter-related types
├── utils/                   # Utility functions
│   └── formatters.ts       # Data formatting utilities
├── config/                  # Configuration files
│   └── api.ts              # API configuration
├── App.tsx                  # Main application component
└── index.tsx                # Application entry point
```

### Key Components

#### App.tsx
- **Purpose**: Main application orchestrator
- **Responsibilities**:
  - State management for active tab
  - Component composition
  - Error handling coordination
  - Loading state management

#### Dashboard.tsx
- **Purpose**: Primary dashboard interface
- **Features**:
  - Statistics overview cards
  - Meet analysis form integration
  - Results display and error handling
  - Performance metrics calculation

#### LiftersPage.tsx
- **Purpose**: Lifter search and display
- **Features**:
  - Search form with validation
  - Results pagination
  - Statistics calculation
  - Error state management

### State Management

The application uses React's built-in state management with hooks:

```typescript
// Global state in App.tsx
const [result, setResult] = useState<MeetResult | null>(null);
const [error, setError] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);
const [activeTab, setActiveTab] = useState('dashboard');
```

### Data Flow

1. **User Input** → Component state update
2. **API Call** → Backend processing
3. **Response** → State update
4. **UI Re-render** → Display results

### Error Handling

- **Network Errors**: Graceful fallbacks with user-friendly messages
- **Validation Errors**: Form-level validation with real-time feedback
- **Loading States**: Visual indicators during API calls
- **Empty States**: Helpful messages when no data is available

## Backend Architecture

### Service Architecture

```
main.py (FastAPI App)
├── DataManager (OpenPowerliftingDataManager)
│   ├── Data Download & Caching
│   ├── Index Building
│   └── Search Optimization
├── LifterProcessor (LifterProcessor)
│   ├── Web Scraping
│   ├── Data Extraction
│   └── Profile Matching
└── API Endpoints
    ├── /meet/analyze
    ├── /lifter/search
    ├── /data/status
    └── /health
```

### Core Services

#### OpenPowerliftingDataManager
- **Purpose**: Manages OpenPowerlifting dataset
- **Features**:
  - Automatic data updates
  - Efficient indexing for fast searches
  - Parquet file storage for performance
  - Metadata management

#### LifterProcessor
- **Purpose**: Handles LiftingCast web scraping
- **Features**:
  - Selenium-based automation
  - Multi-threaded processing
  - Profile matching algorithms
  - Error recovery

### Data Processing Pipeline

```
1. Data Acquisition
   ├── OpenPowerlifting CSV download
   ├── LiftingCast web scraping
   └── Real-time meet data extraction

2. Data Processing
   ├── Pandas DataFrame operations
   ├── Name normalization
   ├── Index building
   └── Performance calculations

3. Data Storage
   ├── Parquet files for performance
   ├── JSON metadata
   ├── Pickle indexes
   └── Cache management

4. Data Retrieval
   ├── Indexed searches
   ├── Fuzzy matching
   ├── Performance scoring
   └── Pagination support
```

### API Endpoints

#### POST /meet/analyze
- **Purpose**: Analyze powerlifting meets
- **Input**: LiftingCast URL
- **Output**: Meet statistics and top performers
- **Processing**: Web scraping + data matching

#### GET /lifter/search
- **Purpose**: Search lifter database
- **Input**: Name, limit, offset
- **Output**: Matching lifters with performance data
- **Processing**: Indexed search with fuzzy matching

#### GET /data/status
- **Purpose**: System health and data status
- **Output**: Data loading status, record counts, cache info

#### GET /health
- **Purpose**: Service health check
- **Output**: Service availability and component status

## Data Architecture

### Data Sources

#### OpenPowerlifting Dataset
- **Format**: CSV files (converted to Parquet)
- **Size**: ~2GB+ of competition data
- **Update Frequency**: Daily automatic checks
- **Content**: Historical competition results

#### LiftingCast
- **Format**: Web scraping
- **Real-time**: Yes
- **Content**: Current meet rosters and results

### Data Models

#### MeetResult
```typescript
interface MeetResult {
  meet_name: string;
  date: string;
  total_lifters: number;
  successful_lookups: number;
  failed_lookups: number;
  average_squat: number;
  average_bench: number;
  average_deadlift: number;
  average_total: number;
  top_performers: TopPerformer[];
}
```

#### Lifter
```typescript
interface Lifter {
  name: string;
  total: number;
  squat_kg: number;
  bench_kg: number;
  deadlift_kg: number;
  dotscore: number;
  weight_class: string;
  age: number;
  division: string;
  meet_name?: string;
  date?: string;
}
```

### Data Storage Strategy

#### Caching Layer
- **Primary Storage**: Parquet files for performance
- **Index Storage**: Pickle files for fast loading
- **Metadata**: JSON files for configuration
- **Cache Directory**: `data_cache/`

#### Indexing Strategy
- **Name Index**: Normalized names for fast lookup
- **Performance**: O(log n) search complexity
- **Memory Usage**: Optimized for large datasets

## Performance Optimizations

### Frontend
- **Component Memoization**: React.memo for expensive components
- **Lazy Loading**: Code splitting for better initial load
- **Efficient Rendering**: Optimized re-render cycles
- **Bundle Optimization**: Tree shaking and minification

### Backend
- **Indexed Searches**: Pre-built indexes for fast lookups
- **Pandas Optimization**: Vectorized operations
- **Memory Management**: Efficient data structures
- **Caching**: Multi-level caching strategy

### Database
- **Parquet Format**: Columnar storage for analytics
- **Compression**: Efficient data compression
- **Indexing**: Custom indexes for search optimization

## Security Considerations

### Frontend Security
- **Input Validation**: Client-side validation
- **XSS Prevention**: React's built-in XSS protection
- **CORS**: Proper CORS configuration
- **Error Handling**: No sensitive data in error messages

### Backend Security
- **Input Sanitization**: All inputs validated
- **Rate Limiting**: API rate limiting (future enhancement)
- **Error Handling**: Secure error responses
- **Data Validation**: Pydantic models for type safety

## Scalability Considerations

### Current Architecture
- **Single Instance**: Monolithic design
- **In-Memory Data**: Fast but memory-intensive. ( Can switch to postgres or sql later on)
- **File-Based Storage**: Simple but not distributed

### Future Enhancements
- **Microservices**: Split into separate services
- **Database Migration**: Move to PostgreSQL/Redis
- **Load Balancing**: Multiple backend instances
- **CDN Integration**: Static asset optimization

## Deployment Architecture

### Development Environment
```
Frontend: localhost:3000 (React Dev Server)
Backend:  localhost:8000 (FastAPI + Uvicorn)
Database: Local Parquet files
```

### Production Considerations
- **Containerization**: Docker containers
- **Reverse Proxy**: Nginx for load balancing
- **Environment Variables**: Configuration management
- **Logging**: Structured logging with rotation

## Monitoring and Observability

### Current Monitoring
- **Application Logs**: Python logging
- **Error Tracking**: Exception handling
- **Performance Metrics**: Response times
- **Health Checks**: /health endpoint

## Development Workflow

### Code Organization
- **Frontend**: Component-based architecture
- **Backend**: Service-oriented design
- **Shared Types**: TypeScript interfaces
- **Configuration**: Environment-based configs

### Testing Strategy
- **Unit Tests**: Component and service testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full user journey testing
- **Performance Tests**: Load testing

### Code Quality
- **TypeScript**: Static type checking
- **ESLint**: Code linting and formatting
- **Pre-commit Hooks**: Automated quality checks
- **Code Review**: Peer review process

## Future Roadmap

### Phase 1: Core Features (Current)
-  Meet analysis
-  Lifter search
-  Basic statistics
-  Responsive UI

### Phase 2: Advanced Features
- [ ] Advanced analytics and charts
- [ ] Meet management system
- [ ] User authentication
- [ ] Real-time updates

### Phase 3: Enterprise Features
- [ ] Multi-tenant architecture
- [ ] Advanced reporting
- [ ] API rate limiting
- [ ] Performance optimization

### Phase 4: Scale and Performance
- [ ] Microservices migration
- [ ] Database optimization
- [ ] CDN integration
- [ ] Advanced caching

## Conclusion

PowerCenter demonstrates a modern, scalable architecture that balances performance, maintainability, and user experience. The application successfully handles complex data processing requirements while providing an intuitive interface for powerlifting meet analysis and lifter research.

The architecture is designed to be:
- **Maintainable**: Clear separation of concerns
- **Scalable**: Modular design for future growth
- **Performant**: Optimized for speed and efficiency
- **User-Friendly**: Intuitive interface and error handling

This foundation provides a solid base for future enhancements and enterprise-level features. 
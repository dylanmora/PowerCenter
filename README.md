# PowerCenter 

A modern, full-stack web application for powerlifting meet analysis and lifter database management. Built with React, TypeScript, FastAPI, and Python.

## Features

- **Meet Analysis**: Real-time analysis of powerlifting meets from LiftingCast
- **Lifter Search**: Comprehensive database search with performance metrics
- **Performance Analytics**: Advanced statistics and trend analysis
- **Modern UI**: Beautiful, responsive design with Tailwind CSS
- **Real-time Data**: Live scraping and data processing
- **Professional Architecture**: Clean, scalable codebase

## Technology Stack

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Modern Fetch API** for HTTP requests

### Backend
- **FastAPI** (Python) for REST API
- **Pandas** for data processing
- **Selenium** for web scraping
- **Parquet** for efficient data storage

### Data Sources
- **LiftingCast** for live meet data
- **OpenPowerlifting** for historical database

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Chrome/Chromium browser (for web scraping)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/powercenter.git
cd powercenter
```

2. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Setup Frontend**
```bash
cd frontend
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
PowerCenter/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── types/          # TypeScript interfaces
│   │   ├── utils/          # Utility functions
│   │   └── config/         # Configuration files
│   └── package.json
├── backend/                 # FastAPI Python backend
│   ├── main.py             # API endpoints
│   ├── data_manager.py     # Data processing
│   ├── lifter_processor.py # Web scraping
│   └── requirements.txt
├── data_cache/             # Cached data files
└── README.md
```

## Key Features

### Meet Analysis Dashboard
- Upload LiftingCast meet URLs
- Real-time data extraction and analysis
- Performance statistics and rankings
- Top performers identification

### Lifter Database
- Search by name with fuzzy matching
- Performance history and trends
- Competition records and statistics
- Advanced filtering options

### Professional UI/UX
- Clean, modern interface
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive navigation

## API Endpoints

- `POST /meet/analyze` - Analyze powerlifting meets
- `GET /lifter/search` - Search lifter database
- `GET /data/status` - System health and data status
- `GET /health` - Service health check

## Data Processing

- **Real-time Scraping**: Live data from LiftingCast
- **Historical Data**: OpenPowerlifting database integration
- **Performance Optimization**: Indexed searches and caching
- **Data Validation**: Robust error handling and validation

## Performance Features

- **Indexed Searches**: O(log n) search complexity
- **Caching Strategy**: Multi-level caching for speed
- **Optimized Rendering**: React performance optimizations
- **Efficient Data Storage**: Parquet format for analytics

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LiftingCast** for meet data
- **OpenPowerlifting** for historical database
- **React** and **FastAPI** communities
- **Tailwind CSS** for styling framework
---

⭐ **Star this repository if you find it helpful!** 
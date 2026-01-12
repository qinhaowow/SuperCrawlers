# SuperCrawler Web UI

This is the web interface for SuperCrawler, a multi-platform social media crawler management system.

## Project Setup

```bash
# Install dependencies
npm install

# Compile and Hot-Reload for Development
npm run dev

# Compile and Minify for Production
npm run build

# Preview Production Build
npm run preview
```

## Features

- Dashboard with system status
- Crawler management
- Task scheduling
- Data management
- System settings
- About page

## API Endpoints

The web UI communicates with the SuperCrawler API at the following endpoints:

- `/api/health` - Health check
- `/api/config/options` - Get configuration options
- `/api/config/current` - Get current configuration
- `/api/config/update` - Update configuration
- `/api/crawler/start` - Start crawler
- `/api/crawler/stop` - Stop crawler
- `/api/tasks` - Get tasks
- `/api/tasks/create` - Create task
- `/api/tasks/pause` - Pause task
- `/api/tasks/resume` - Resume task
- `/api/tasks/delete` - Delete task
- `/api/data` - Get data
- `/api/data/delete` - Delete data

## Deployment

1. Build the web UI:
   ```bash
   npm run build
   ```

2. The built files will be in the `dist` directory, which should be served by the SuperCrawler API server.
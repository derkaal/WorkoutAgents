# API Configuration Guide

This document explains how to use the API configuration and services in the React PWA frontend to connect with the FastAPI backend.

## Environment Configuration

The application uses environment variables to configure the API connection. These are set in the `.env` file in the root of the project.

### Available Environment Variables

- `VITE_API_BASE_URL`: The base URL of the API server (default: `http://localhost:8000`)

### Example `.env` File

```
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## Configuration Utility

The configuration utility is located at `src/config.ts`. It exports configuration objects that can be imported and used throughout the application.

### API Configuration

```typescript
import { API_CONFIG } from '../config';

// Use the API URL
console.log(API_CONFIG.API_URL); // http://localhost:8000/api/v1
```

### Environment Configuration

```typescript
import { ENV_CONFIG } from '../config';

// Check if running in development mode
if (ENV_CONFIG.IS_DEV) {
  console.log('Running in development mode');
}
```

## API Services

There are two API service utilities available:

### 1. Legacy API Service (`apiService.ts`)

This is the original API service that provides specific methods for workout-related API calls.

```typescript
import { apiService } from '../services/apiService';

// Generate a workout
const workout = await apiService.generateWorkout({ 
  difficulty: 'medium',
  duration: 30
});

// Analyze progress
const progress = await apiService.analyzeProgress();
```

### 2. Generic API Client (`apiClient.ts`)

This is a more flexible API client that can be used for any API endpoint.

```typescript
import { apiClient } from '../services/apiClient';

// GET request
const { data } = await apiClient.get('/users');

// POST request
const { data } = await apiClient.post('/users', {
  name: 'John',
  email: 'john@example.com'
});

// PUT request
const { data } = await apiClient.put('/users/123', {
  name: 'John Updated'
});

// DELETE request
const { status } = await apiClient.delete('/users/123');
```

### Creating a Custom API Client

You can create a custom API client with a different base URL:

```typescript
import { createApiClient } from '../services/apiClient';

const customApiClient = createApiClient('https://api.example.com/v2');
const { data } = await customApiClient.get('/users');
```

## Best Practices

1. **Use the configuration utility**: Always import configuration values from the config file rather than hardcoding them.

2. **Environment-specific behavior**: Use the `ENV_CONFIG` object to conditionally execute code based on the environment.

3. **Error handling**: The API client includes built-in error handling, but you should still wrap API calls in try/catch blocks:

```typescript
try {
  const { data } = await apiClient.get('/users');
  // Handle successful response
} catch (error) {
  if (error instanceof ApiError) {
    // Handle API error
    console.error(`API Error ${error.status}: ${error.message}`);
  } else {
    // Handle other errors
    console.error('Unknown error:', error);
  }
}
```

4. **TypeScript types**: Use TypeScript generics to specify the expected response type:

```typescript
interface User {
  id: string;
  name: string;
  email: string;
}

const { data } = await apiClient.get<User>('/users/123');
// data is typed as User
console.log(data.name);
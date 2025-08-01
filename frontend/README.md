# Re-Search Frontend

A React-based frontend for the Research Paper Discovery & Recommendation System.

## Overview

This frontend provides a modern, responsive UI for:
- User authentication and onboarding
- Paper search and discovery
- Personalized recommendations
- User profile management

## Tech Stack

- **Framework**: React 18.2
- **Styling**: Tailwind CSS 3.4
- **Routing**: React Router DOM 7
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: Sonner
- **UI Components**: Custom components inspired by shadcn/ui

## Project Structure

```
frontend/
├── public/
│   └── index.html        # HTML template
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── checkbox.jsx
│   │   │   ├── input.jsx
│   │   │   └── label.jsx
│   │   └── Header.jsx    # Navigation header
│   ├── hooks/
│   │   └── useAuth.js    # Authentication context
│   ├── lib/
│   │   ├── api.js        # API client configuration
│   │   └── utils.js      # Utility functions
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── OnboardingPage.jsx
│   │   ├── SearchPage.jsx
│   │   ├── PaperDetailPage.jsx
│   │   ├── RecommendationsPage.jsx
│   │   └── ProfilePage.jsx
│   ├── App.js            # Main app with routing
│   ├── App.css           # App-specific styles
│   ├── index.js          # Entry point
│   └── index.css         # Global styles & Tailwind
├── package.json          # Dependencies
├── tailwind.config.js    # Tailwind configuration
└── .env                  # Environment variables
```

## Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/login` | LoginPage | User login form |
| `/register` | RegisterPage | User registration |
| `/onboarding` | OnboardingPage | Interest selection (Pinterest-style) |
| `/search` | SearchPage | Paper search and browse |
| `/paper/:id` | PaperDetailPage | Paper details with actions |
| `/recommendations` | RecommendationsPage | Personalized recommendations |
| `/profile` | ProfilePage | User settings and history |

## Features

### Authentication
- JWT token-based authentication
- Persistent login state via localStorage
- Protected routes with automatic redirect

### Onboarding
- Pinterest-style masonry grid
- 16 research interest categories
- Minimum 3 selections required

### Search
- Search by paper title
- Filter by author name
- Filter by publication year
- Real-time results from Neo4j

### Paper Details
- Full paper metadata display
- Like/save functionality
- Share link (clipboard copy)
- Export citation
- View citing papers

### Recommendations
- Match percentage scores
- Explanation for each recommendation
- Multiple recommendation strategies

### Profile
- Edit profile information
- Change password
- View liked papers
- View recently viewed papers
- Display selected interests

## Quick Start

```bash
# Install dependencies
yarn install

# Set environment variables
cp .env.example .env

# Start development server
yarn start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | (empty for proxy) |
| `DANGEROUSLY_DISABLE_HOST_CHECK` | Allow external hosts | true |
| `HOST` | Server host binding | 0.0.0.0 |

## Design System

### Colors
- **Background**: Stone/Bone (`#FAFAF9`)
- **Primary**: Deep Indigo (`#0F172A`)
- **Accent**: Orange (`#EA580C`)
- **Success**: Emerald (`#10B981`)

### Typography
- **Headings**: Playfair Display (serif)
- **Body**: Inter (sans-serif)
- **Code**: JetBrains Mono (monospace)

### Components
All UI components follow the shadcn/ui pattern with Tailwind CSS and Radix UI primitives.

## Scripts

```bash
yarn start    # Start dev server
yarn build    # Production build
yarn test     # Run tests
```

## License

MIT

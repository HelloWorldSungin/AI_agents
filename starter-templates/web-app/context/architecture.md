# {{PROJECT_NAME}} - Architecture

## Overview

{{PROJECT_NAME}} is a modern web application built with a React frontend and Node.js backend.

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: [Choose: Redux Toolkit / Zustand / React Query]
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library

### Backend
- **Runtime**: Node.js 20+
- **Framework**: Express.js
- **Database**: [Choose: PostgreSQL / MongoDB / MySQL]
- **ORM**: [Choose: Prisma / TypeORM / Mongoose]
- **Authentication**: JWT
- **Testing**: Jest / Vitest

### Infrastructure
- **Deployment**: [Choose: AWS / Vercel / Docker / Kubernetes]
- **CI/CD**: [Choose: GitHub Actions / GitLab CI / CircleCI]
- **Monitoring**: [Choose: Sentry / Datadog / CloudWatch]

## Repository Structure

```
{{PROJECT_NAME}}/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── utils/        # Utility functions
│   │   ├── services/     # API service layer
│   │   └── App.tsx
│   ├── public/
│   └── package.json
│
├── backend/               # Node.js API server
│   ├── src/
│   │   ├── controllers/  # Request handlers
│   │   ├── services/     # Business logic
│   │   ├── models/       # Data models
│   │   ├── routes/       # API routes
│   │   ├── middleware/   # Custom middleware
│   │   └── server.ts
│   └── package.json
│
├── shared/                # Shared code between frontend/backend
│   └── types/            # TypeScript type definitions
│
└── .ai-agents/           # AI agents configuration
```

## Key Architecture Decisions

### Frontend Architecture
- **Component Structure**: Atomic design pattern (atoms, molecules, organisms, templates, pages)
- **Routing**: React Router v6
- **Data Fetching**: [Your choice: React Query, SWR, or custom hooks]
- **Form Handling**: [Your choice: React Hook Form, Formik]

### Backend Architecture
- **Design Pattern**: MVC (Model-View-Controller) pattern
- **API Style**: RESTful API
- **Layer Separation**: Controller → Service → Repository
- **Error Handling**: Centralized error handling middleware

### Database Schema
[Add your database design here]

Example:
```
users
- id (uuid, primary key)
- email (string, unique)
- password_hash (string)
- created_at (timestamp)

[Add your other tables]
```

## API Design

### Base URLs
- Development: `http://localhost:3000/api`
- Staging: `https://staging-api.{{PROJECT_NAME}}.com`
- Production: `https://api.{{PROJECT_NAME}}.com`

### Authentication
All protected endpoints require JWT token in Authorization header.

## Development Workflow

### Local Development
```bash
# Frontend
cd frontend && npm run dev    # Runs on http://localhost:5173

# Backend
cd backend && npm run dev      # Runs on http://localhost:3000
```

### Environment Variables
- Frontend: `.env.local`
- Backend: `.env`

## Deployment

### Frontend Deployment
[Describe your frontend deployment process]

### Backend Deployment
[Describe your backend deployment process]

## Performance Considerations

- Code splitting for frontend bundles
- Database query optimization with indexes
- Caching strategy: [Describe your caching approach]
- CDN for static assets

## Security Measures

- HTTPS everywhere
- CORS configuration
- Rate limiting on API endpoints
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS prevention through React's built-in escaping

---

**Last Updated**: [Date]
**Maintained By**: [Team/Person]

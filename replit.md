# The Solution Desk - Digital Marketplace

## Overview

The Solution Desk is a Flask-based digital marketplace web application that allows users to purchase and access digital tools. The platform features user authentication, content management through Markdown files, and integrated Stripe payment processing for secure transactions.

## User Preferences

Preferred communication style: Simple, everyday language.
Design preference: Executive cyberpunk aesthetic with dark theme and strategic neon accents.
Content strategy: Problem→solution framing for all tools and products.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL (via DATABASE_URL)
- **Authentication**: Flask-Login for session management with password hashing
- **Security**: Flask-Talisman for security headers and ProxyFix for reverse proxy handling
- **Content Management**: Flask-FlatPages for Markdown-based content rendering

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap with custom Executive Cyberpunk theme
- **Typography**: Montserrat geometric sans-serif font
- **Color Scheme**: Teal Pop variation (#1A1A28 background, #00BFA6 primary, #FFC857 CTAs)
- **Icons**: Feather Icons with subtle neon glow effects
- **JavaScript**: Vanilla JavaScript for interactive elements

### Database Schema
- **User**: Stores user accounts with email and hashed passwords
- **Tool**: Digital products with name, slug, and pricing information
- **Purchase**: Links users to purchased tools with Stripe session tracking

## Key Components

### Authentication System (`app/auth/`)
- Registration and login forms with validation
- Password hashing using Werkzeug security utilities
- Session management with Flask-Login
- Form validation using WTForms

### Main Application (`app/main/`)
- Homepage with tool listings and marketing content
- Individual tool detail pages combining database records with Markdown content
- User dashboard for viewing purchased tools
- Content routing for Markdown-based tool descriptions

### Shop/Payment System (`app/shop/`)
- Stripe integration for secure payment processing
- Checkout session creation with metadata tracking
- Purchase completion handling and database updates
- Duplicate purchase prevention

### Content Management
- Markdown files in `content/` directory for tool descriptions
- Dynamic content rendering with FlatPages
- Structured metadata in Markdown files (title, slug, price)

## Data Flow

1. **User Registration/Login**: Users create accounts or authenticate through forms
2. **Tool Browsing**: Homepage displays available tools from database
3. **Tool Details**: Individual pages combine database info with Markdown content
4. **Purchase Flow**: Authenticated users can initiate Stripe checkout sessions
5. **Payment Processing**: Stripe handles payment, returns success/failure status
6. **Purchase Recording**: Successful payments create database records linking users to tools
7. **Access Control**: Dashboard shows purchased tools, preventing duplicate purchases

## External Dependencies

### Payment Processing
- **Stripe**: Complete payment infrastructure with checkout sessions
- **Environment Variables**: STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY required

### Database
- **Default**: SQLite for development (file-based database)
- **Production**: PostgreSQL via DATABASE_URL environment variable
- **Migrations**: Flask-Migrate for database schema management

### Security
- **Session Management**: SESSION_SECRET environment variable for secure sessions
- **HTTPS**: Talisman security headers (disabled for development)
- **Password Security**: Werkzeug password hashing

### Content Delivery
- **CDN**: Bootstrap CSS and Feather Icons loaded from CDNs
- **Static Files**: Custom CSS/JS served from Flask static folder

## Deployment Strategy

### Development
- **Local Server**: Flask development server on port 5000
- **Debug Mode**: Enabled for development with detailed error pages
- **Database**: SQLite file-based database for simplicity

### Production Considerations
- **Environment Variables**: All sensitive configuration via environment variables
- **Database**: PostgreSQL recommended via DATABASE_URL
- **Security**: HTTPS enforcement and security headers via Talisman
- **Proxy**: ProxyFix middleware for reverse proxy deployment

### Configuration Management
- **Flexible Database**: Supports both SQLite (dev) and PostgreSQL (prod)
- **Security Toggles**: HTTPS and security headers configurable per environment
- **Session Security**: Configurable session secrets
- **Payment Integration**: Environment-based Stripe key configuration

The application follows Flask best practices with blueprint organization, proper separation of concerns, and environment-based configuration management. The architecture supports both development and production deployment scenarios with minimal configuration changes.
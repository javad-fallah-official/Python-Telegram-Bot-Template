# 📚 Documentation

Welcome to the Python Telegram Bot Template documentation! This directory contains comprehensive guides and references for using and extending the bot template.

## 📖 Quick Navigation

### Getting Started
- [**Quick Start Guide**](../QUICKSTART.md) - Get your bot running in minutes
- [**Installation & Setup**](setup/INSTALLATION.md) - Detailed installation instructions
- [**Configuration Guide**](setup/CONFIGURATION.md) - Environment variables and settings

### Core Features
- [**Database Guide**](features/DATABASE.md) - SQLite and PostgreSQL support
- [**Bot Handlers**](features/HANDLERS.md) - Commands, messages, and error handling
- [**Middleware**](features/MIDDLEWARE.md) - Rate limiting, admin controls, logging
- [**Services**](features/SERVICES.md) - Polling and webhook modes

### Migration Guides
- [**aiogram Migration**](migration/AIOGRAM_MIGRATION.md) - Framework migration details
- [**Test Migration**](migration/TEST_MIGRATION.md) - Test suite updates
- [**Database Migration**](migration/DATABASE_MIGRATION.md) - Database switching implementation

### Advanced Topics
- [**PostgreSQL Setup**](advanced/POSTGRESQL.md) - Production PostgreSQL configuration
- [**Deployment**](advanced/DEPLOYMENT.md) - Production deployment guide
- [**Performance**](advanced/PERFORMANCE.md) - Optimization tips and best practices
- [**Security**](advanced/SECURITY.md) - Security considerations and best practices

### Development
- [**Contributing**](development/CONTRIBUTING.md) - How to contribute to the project
- [**Testing**](development/TESTING.md) - Running and writing tests
- [**Architecture**](development/ARCHITECTURE.md) - Project structure and design patterns

### API Reference
- [**Core API**](api/CORE.md) - Core modules and classes
- [**Bot API**](api/BOT.md) - Bot factory and handlers
- [**Utils API**](api/UTILS.md) - Utility functions and helpers

## 🔍 Quick Search

Looking for something specific? Here are the most common topics:

| Topic | Documentation |
|-------|---------------|
| **First time setup** | [Quick Start Guide](../QUICKSTART.md) |
| **Environment variables** | [Configuration Guide](setup/CONFIGURATION.md) |
| **Database setup** | [Database Guide](features/DATABASE.md) |
| **Adding commands** | [Bot Handlers](features/HANDLERS.md) |
| **PostgreSQL** | [PostgreSQL Setup](advanced/POSTGRESQL.md) |
| **Deployment** | [Deployment Guide](advanced/DEPLOYMENT.md) |
| **Testing** | [Testing Guide](development/TESTING.md) |

## 📝 Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── setup/                       # Setup and configuration
│   ├── INSTALLATION.md         # Installation instructions
│   └── CONFIGURATION.md        # Configuration guide
├── features/                    # Core features documentation
│   ├── DATABASE.md             # Database functionality
│   ├── HANDLERS.md             # Bot handlers
│   ├── MIDDLEWARE.md           # Middleware and decorators
│   └── SERVICES.md             # Polling and webhook services
├── migration/                   # Migration guides
│   ├── AIOGRAM_MIGRATION.md    # aiogram framework migration
│   ├── TEST_MIGRATION.md       # Test suite migration
│   └── DATABASE_MIGRATION.md   # Database switching
├── advanced/                    # Advanced topics
│   ├── POSTGRESQL.md           # PostgreSQL setup
│   ├── DEPLOYMENT.md           # Production deployment
│   ├── PERFORMANCE.md          # Performance optimization
│   └── SECURITY.md             # Security best practices
├── development/                 # Development guides
│   ├── CONTRIBUTING.md         # Contributing guidelines
│   ├── TESTING.md              # Testing documentation
│   └── ARCHITECTURE.md         # Project architecture
└── api/                        # API reference
    ├── CORE.md                 # Core modules
    ├── BOT.md                  # Bot components
    └── UTILS.md                # Utility functions
```

## 🤝 Contributing to Documentation

Found an error or want to improve the documentation? See our [Contributing Guide](development/CONTRIBUTING.md) for details on how to help make the documentation better.

## 📞 Support

If you can't find what you're looking for in the documentation:

1. Check the [Quick Start Guide](../QUICKSTART.md) for common setup issues
2. Review the [Configuration Guide](setup/CONFIGURATION.md) for environment variable problems
3. Look at the [examples/](../examples/) directory for working code samples
4. Open an issue on GitHub with your question

---

*Last updated: January 2024*
![othor-ai-logo](https://github.com/user-attachments/assets/f4f6ab1c-699f-4f10-8d86-7b421e05a79c)

# Othor AI

An AI-native business intelligence platform that delivers insights in minutes. Othor AI is an open-source alternative to traditional BI tools, utilizing large language models to provide automated insights, interactive data analysis, and narrative-driven reporting.

## Features

- 🤖 **AI-Powered Analytics**: Get instant insights from your data using advanced language models
- 💬 **Chat with Data**: Natural language interactions with your business data
- 📊 **Smart Charts**: Auto-generated and updated visualizations
- 📝 **Business Narratives**: AI-generated executive summaries and reports
- 🔐 **Enterprise Security**: Role-based access control and secure data handling

## Repository Structure
```
.
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── docker-compose.yml
├── services/
│   ├── backend-organizations/     # Organization management service
│   ├── backend-metrics/          # Metrics dashboard service
│   ├── backend-metric-discovery/ # Metric discovery service
│   ├── backend-auth/            # Authentication service
│   ├── backend-narrative/       # Narrative generation service
│   ├── backend-chatbot/        # Data chat interface service
│   └── othor-frontend/         # Next.js frontend application
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── data-flow.md
│   │   └── security.md
│   ├── deployment/
│   │   ├── local-setup.md
│   │   └── production.md
│   └── development/
│       ├── contributing.md
│       └── coding-standards.md
├── scripts/
│   ├── setup.sh
│   ├── dev.sh
│   └── deploy.sh
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
        ├── ci.yml
        ├── release.yml
        └── deploy.yml
```

## Quick Start

1. Clone this repository with submodules:
```bash
git clone --recursive https://github.com/othorai/othor-platform.git
cd othor-platform
```

2. Initialize and update submodules:
```bash
git submodule init
git submodule update
```

3. Start the development environment:
```bash
./scripts/dev.sh
```

## Architecture

The platform consists of several microservices:

- **backend-organizations**: Manages organization data and user access
- **backend-metrics**: Handles metrics dashboard and data visualization
- **backend-metric-discovery**: Automatic metric detection and analysis
- **backend-auth**: Authentication and authorization service
- **backend-narrative**: AI-powered narrative generation
- **backend-chatbot**: Natural language data interaction
- **othor-frontend**: React/Next.js web application

## Development

1. Install dependencies:
```bash
# Frontend
cd services/othor-frontend
npm install

# Backend services
cd services/backend-*
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Start services:
```bash
docker-compose up
```

## Deployment

See [deployment documentation](docs/deployment/production.md) for production setup instructions.

## Team behind Othor 1.0 release

| [<img src="https://github.com/NairKoroth.png" width="80px;" alt="Nair Koroth"/><br /><sub><b>NairKoroth</b></sub>](https://github.com/NairKoroth) | [<img src="https://github.com/nekender.png" width="80px;" alt="User2"/><br /><sub><b>nekender</b></sub>](https://github.com/nekender) | [<img src="https://github.com/ritttwaj.png" width="80px;" alt="User3"/><br /><sub><b>ritttwaj</b></sub>](https://github.com/ritttwaj) |
| :---: | :---: | :---: |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT License](LICENSE)

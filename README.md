<img width="559" alt="Othor AI Logo" src="https://github.com/user-attachments/assets/7c3fa192-950b-46f8-bfa4-dd0661de7bc1" />

# Othor AI - 🚀 Data to Dashboards in Less than 30 seconds
[![stability-beta](https://img.shields.io/badge/stability-beta-33bbff.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta)
 ![Static Badge](https://img.shields.io/badge/v1.0_release_date-19_Dec_24-purple)

An AI-native fast, simple, and secure alternative to popular business intelligence solutions like Tableau, Power BI, and Looker. Othor utilizes large language models (LLMs) to deliver custom business intelligence solutions in seconds. Visit https://othor.ai/ to know more and book a demo.

Othor is built to be Fast, Simple & Secure.
1. **Fast & Modern**- Built with FastAPI for lightning-speed insights and real-time data updates.
2. **Simple & Intuitive** - Engineered with React for an intuitive, seamless, and simple user experience.
3. **Secure & Reliable** - Designed with care, ensuring robust security for your data and insights.

## Features

- 🤖 **AI-Powered Analytics**: Get instant insights from your data using advanced language models
- 💬 **Chat with Data**: Natural language interactions with your business data
- 📊 **Smart Charts**: Auto-generated and updated visualizations
- 📝 **Business Narratives**: AI-generated executive summaries and reports
- 🔐 **Enterprise Security**: Role-based access control and secure data handling



### Built with
- Python
- FastAPI
- React
- NextJS
- Tailwind CSS
- Shadcn/ui

### Code guidance by
- Anthropic Claude

## Video
<video width="800" alt="Othor Intro Video" src="https://github.com/user-attachments/assets/a5fb7c60-05f6-47b6-ad1c-3776e97d5466"></video>
 
## Screenshots
![Group 2(1)](https://github.com/user-attachments/assets/b5d720fb-4ca1-4c9d-b406-5c5276dda32e)

## Contact us
Meet our team for any commercial inquiries - https://cal.com/othor

## Stay up-to date
The first version (v1.0) of Othor, codenamed RuneWeaver, was officially launched on December 19, 2024. Release notes - Othor RuneWeaver (Getting ready to publish).

## Repository Structure
```
.
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── docker-compose.yml
├── .env                           #root .env file
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

## Architecture

The platform consists of several microservices:

- **backend-organizations**: Manages organization data and user access
- **backend-metrics**: Handles metrics dashboard and data visualization
- **backend-metric-discovery**: Automatic metric detection and analysis
- **backend-auth**: Authentication and authorization service
- **backend-narrative**: AI-powered narrative generation
- **backend-chatbot**: Natural language data interaction
- **othor-frontend**: React/Next.js web application

## Quick Start for Developers

Here is a recorded installation tutorial that explains the steps below - https://youtu.be/8NdjGs_Lwfw

1. Clone the git repository
   ```bash
   git clone --recursive https://github.com/othorai/othor.ai
   ````

2. Move to directory
   ```bash
   cd othor.ai/
   ````

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ````
   Edit .env with your configurations

4. Start services:
   Lets first create database image locally

   ```bash
   docker-compose build
   ```

   Now lets start the service, after intilization you can access the app at 'http://localhost:3000' and login using id - admin@example.com, password - admin123
   ```bash
   docker-compose up
   ```

   You can check the logs using command below
   ```bash
   docker-compose logs -f {microservice_name} #narrative,metrics,metric-discovery,chatbot,organization and auth
   ```

5. Stop services:
   To delete database volumes and start fresh
   ```bash
   docker-compose down -v
   ```

   To just stop services
   ```bash
   docker-compose down
   ```

## Product Demo
After installing the product successfully, watch the following video to learn how to connect to different datasources.

https://www.youtube.com/watch?v=TX_dUeZQK5g

## Team behind Othor 1.0(RuneWeaver) release

| [<img src="https://github.com/NairKoroth.png" width="80px;" alt="Nair Koroth"/><br /><sub><b>NairKoroth</b></sub>](https://github.com/NairKoroth) | [<img src="https://github.com/nekender.png" width="80px;" alt="User2"/><br /><sub><b>nekender</b></sub>](https://github.com/nekender) | [<img src="https://github.com/ritttwaj.png" width="80px;" alt="User3"/><br /><sub><b>ritttwaj</b></sub>](https://github.com/ritttwaj) |
| :---: | :---: | :---: |

## Upcoming Releases: What We're Working On
1. Single Sign-On (SSO) and integrations with popular applications
2. Additional data source connectors
3. LLM Switcher & LLM connectors
4. New layout options for narratives
5. Expanded chart types for dashboards
6. Mobile app (Enterprise License)
7. Email alerts
8. Themes

## Othor 2.0 - Bifrost 🌈
We’re here for the long haul. Expect a major release of Othor 2.0 in 2025! Take a look at our labs and research(https://othor.ai/labs/) to catch a glimpse of what we’re planning for Bifrost (Othor 2.0). Bifrost will be more collaborative, more enterprise-focused, and even more magical than RuneWeaver (Othor 1.0), while preserving its simplicity, speed, and security.

## Support Othor AI
If you like the product we’ve built and what we’re striving for in the long term, please help promote Othor within your network. We’re also raising funds. For a detailed pitch deck, contact us at uk@othor.ai.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT License](LICENSE)

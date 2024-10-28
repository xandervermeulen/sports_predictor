# Sports Predictor

The Sports Predictor project provides a complete application to predict outcomes for upcoming **tennis** and **UFC** matches. It integrates a Mendix front-end application with a Python backend service to deliver predictions and manage data flow.

## Project Overview

This project includes:

- A **Mendix Application** for users to view predictions and explore match data.
- **Custom Data Scrapers** to gather live and historical data for both UFC and tennis matches.
- A **Python Service** for AI-driven prediction models, including retraining capabilities for accuracy and options to make predictions on custom "fantasy" matches.

## Features

### Mendix Application
The Mendix application serves as the user interface, offering:
- Easy access to upcoming match predictions.
- An interactive display for exploring and visualizing prediction data.
- The ability to interact with other users on our own platform.
- Multiple Admin and users roles for a user friendly application.
  
### Data Collection
Two specialized data scrapers gather real-time and historical data:
- **UFC Scraper** – Collects data for upcoming and past UFC matches.
- **Tennis Scraper** – Collects data for upcoming and past tennis matches.

### AI Prediction Model
Our AI models allow for:
- **Automated Retraining** – Models are retrained with the latest data, ensuring improved prediction accuracy over time.
- **Live Predictions** – Users can create "fantasy" matchups, and the model will generate predictions for these custom inputs.
- **Initial Training** - The first version of our Neural Network is trained in the given notebooks in the project.

All AI logic and data processing run in a dedicated Python backend service.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/sports_predictor.git
   ```

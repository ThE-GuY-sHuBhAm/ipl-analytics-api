# IPL Performance Analytics API

[![Live App](https://img.shields.io/badge/Live%20App-the--ipl--dugout-brightgreen?style=for-the-badge)](https://the-ipl-dugout.onrender.com/)

A full-stack web application that provides detailed performance analytics for the Indian Premier League (IPL). This project processes raw ball-by-ball data to engineer a rich set of features and serves them through a robust Flask API to a dynamic, single-page frontend.

## Live Demo

You can access the live, deployed application here:
**[https://the-ipl-dugout.onrender.com](https://the-ipl-dugout.onrender.com)**

![Screenshot of the IPL Dugout application interface](https://i.imgur.com/8a6tJ2g.png)

---

## Features

* **Team vs. Team Analysis:** Get head-to-head match statistics between any two IPL teams.
* **Detailed Batsman Records:** View comprehensive career stats for any batsman, including runs, strike rate, average, 50s/100s, and more.
* **Detailed Bowler Records:** View complete career stats for any bowler, including wickets, economy, bowling average, and best figures.
* **Performance vs. Opponents:** See a player's detailed performance broken down against every individual opponent.
* **Single-Page Application:** A fast, modern UI that dynamically fetches and displays data without reloading the page.
* **RESTful API:** A well-structured backend API that serves all the calculated statistics as clean JSON.

---

## Tech Stack

* **Backend:** Python, Flask, Pandas, NumPy
* **Frontend:** HTML, JavaScript, Tailwind CSS
* **Server:** Gunicorn
* **Deployment:** Render

---

## API Endpoints

The application is powered by the following API endpoints:

| Method | Endpoint                    | Description                                         |
| :----- | :-------------------------- | :-------------------------------------------------- |
| `GET`  | `/api/list-all`             | Provides lists of all teams, batters, and bowlers.  |
| `GET`  | `/api/teamvteam`            | Returns head-to-head stats for two teams.           |
| `GET`  | `/api/batting-record`       | Returns the complete batting record for a player.   |
| `GET`  | `/api/bowling-record`       | Returns the complete bowling record for a player.   |

---

## How to Run Locally

To run this project on your own machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/ipl-analytics-api.git](https://github.com/your-username/ipl-analytics-api.git)
    cd ipl-analytics-api
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    flask run
    ```

5.  **Open your browser** and navigate to `http://127.0.0.1:5000`.


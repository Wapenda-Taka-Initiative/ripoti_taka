# Ripoti Taka: A Web Application to Mobilize Citizen Participation in Solid Waste Management in Nairobi

### Description
Solid waste management in Nairobi County faces challenges such as inadequate coverage, uncontrolled dumping, inefficient services, and lack of infrastructure, leading to health risks and environmental damage. Limited public participation has shown potential in improving the situation. This project aims to develop "Ripoti Taka," a web platform for citizens to monitor and report waste management issues using geotagged reports with descriptions and visual evidence. Utilizing ArchGIS, Leaflet JS, and Flask, the system creates interactive maps to identify problem areas, promoting sustainable waste management. This project could transform waste management in Nairobi and serve as a national model.

## Project Setup/Installation Instructions

### Dependencies
- Flask
- ArchGIS
- Leaflet JS
- Google Places

### Installation Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/barasamichael/ripoti_taka.git
    cd ripoti-taka
    ```
2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```
5. Run the development server:
    ```bash
    flask run
    ```

## Usage Instructions

### How to Run
1. Ensure the virtual environment is activated.
2. Run the Flask development server:
    ```bash
    flask run
    ```
3. Access the web application in your browser at `http://127.0.0.1:5000`.

### Examples
- **Report a waste issue**: Click on the map to add a new report, provide a description, and upload a photo.
- **View reported issues**: Browse the map to see all reported waste issues with details and images.

### Input/Output
- **Input**: Geotagged waste reports (location, description, photo).
- **Output**: Interactive map displaying reported waste issues, user points, and rewards.

## Project Structure

### Overview
```plaintext
.
├── README.md
├── app
│   ├── Dockerfile
│   ├── Procfile
│   ├── __init__.py
│   ├── administration
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── authentication
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── boot.sh
│   ├── docker-compose.yml
│   ├── main
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── comment.py
│   │   ├── permission.py
│   │   ├── report.py
│   │   ├── report_status.py
│   │   ├── reward.py
│   │   ├── role.py
│   │   ├── status.py
│   │   ├── user.py
│   │   └── user_reward.py
│   ├── profiles
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── registration
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── static
│   │   ├── assets
│   │   │   ├── css
│   │   │   │   ├── tailwind.css
│   │   │   │   └── tailwind.output.css
│   │   │   └── js
│   │   │       ├── charts-bars.js
│   │   │       ├── charts-lines.js
│   │   │       ├── charts-pie.js
│   │   │       ├── focus-trap.js
│   │   │       └── init-alpine.js
│   │   └── img
│   │       ├── community-engagement-home.jpg
│   │       ├── data-driven-home.avif
│   │       ├── efficient-reporting-home.gif
│   │       ├── images_not_submitted.png
│   │       ├── nairobi-home.jpg
│   │       ├── real-time-update-home.gif
│   │       ├── reward-home.gif
│   │       ├── savannah.jpg
│   │       ├── sustainable-home.png
│   │       └── trash.jpg
│   └── templates
│       ├── 401.html
│       ├── 403.html
│       ├── 404.html
│       ├── 500.html
│       ├── administration
│       │   ├── 403.html
│       │   ├── 404.html
│       │   └── 500.html
│       ├── authentication
│       │   ├── 403.html
│       │   ├── 404.html
│       │   ├── 500.html
│       │   ├── forgotten_password.html
│       │   ├── login.html
│       │   ├── password_reset.html
│       │   ├── reset_password.html
│       │   ├── unconfirmed.html
│       │   └── unlock_screen.html
│       ├── base.html
│       ├── email
│       │   ├── confirm_account.html
│       │   ├── confirm_account.txt
│       │   ├── password_reset.html
│       │   └── password_reset.txt
│       ├── main
│       │   ├── 403.html
│       │   ├── 404.html
│       │   ├── 500.html
│       │   ├── contact.html
│       │   ├── get_involved.html
│       │   ├── index.html
│       │   ├── privacy_policy.html
│       │   └── terms_and_conditions.html
│       ├── profiles
│       │   ├── 403.html
│       │   ├── 404.html
│       │   ├── 500.html
│       │   ├── analytics.html
│       │   ├── create_report.html
│       │   ├── dashboard.html
│       │   ├── distribution_of_categories.html
│       │   ├── edit_report.html
│       │   ├── explore.html
│       │   ├── latest_reports.html
│       │   ├── manage_categories.html
│       │   ├── manage_reports.html
│       │   ├── manage_rewards.html
│       │   ├── manage_users.html
│       │   ├── member_contributions.html
│       │   ├── personal_analytics.html
│       │   ├── report_details.html
│       │   ├── user_dashboard_base.html
│       │   └── user_profile.html
│       ├── registration
│       │   ├── 401.html
│       │   ├── 403.html
│       │   ├── 404.html
│       │   ├── 500.html
│       │   ├── edit_user_profile.html
│       │   └── register_user.html
│       └── utilities.html
├── backup.sql
├── config.py
├── data-dev-sqlite
├── decorators.py
├── flasky.py
└── utilities
    └── email.py

20 directories, 115 files
```

### Key Files
- **`app/models.py`**: Defines the database models for users, reports, and rewards.
- **`app/routes.py`**: Contains the main application routes and logic.
- **`app/templates/`**: HTML templates for rendering the web pages.
- **`app/static/`**: Static files such as CSS, JavaScript, and images.
- **`config.py`**: Configuration settings for the application.
- **`run.py`**: Entry point to start the Flask application.

## Additional Sections

### Project Status
Pending

### Known Issues
None at the moment.

### Acknowledgements
Thanks to the developers of ArchGIS, Leaflet JS, and Flask for their powerful tools.

## License
[MIT License](https://opensource.org/licenses/MIT)

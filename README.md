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
│   │   └── img
│   └── templates
│       ├── 401.html
│       ├── 403.html
│       ├── 404.html
│       ├── 500.html
│       ├── administration
│       ├── authentication
│       ├── base.html
│       ├── email
│       ├── main
│       ├── profiles
│       ├── registration
│       └── utilities.html
├── backup.sql
├── config.py
├── data-dev-sqlite
├── decorators.py
├── flasky.py
└── utilities
    └── email.py

18 directories, 49 files
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

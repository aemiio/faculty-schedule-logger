﻿# Faculty Schedule and Time Logging System (CLI)

A **console-based** Faculty Schedule and Time Logging System built with Python and MySQL. This command-line application provides an efficient way to manage faculty schedules and record time logs.

## 🚀 Features

### 🗓️ Schedule Management (CLI-Based)
- Add, update, and delete faculty schedules through guided text prompts
- View schedules in a formatted text-based table

### ⏳ Time Logging (Terminal-Based)
- Record faculty time-in and time-out via simple text input
- View detailed time logs for individual faculty members
- Export time logs to Excel for further processing
- Automated ETL (Extract, Transform, Load) for time log processing

### 📊 Data Visualization
- ASCII-based grid views for faculty schedules
- Text-formatted tabulated reports for time logs

## 📋 Prerequisites

- Python 3.x
- MySQL Server
- Terminal/Command Prompt
- Required Python packages:
  - mysql-connector-python
  - python-dotenv
  - pandas
  - tabulate
  - openpyxl

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/aemiio/faculty-schedule-logger.git
cd faculty-schedule-logger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database connection:
   - Create a `.env` file in the root directory:
```env
DB_HOST=your_host
DB_USER=your_username
DB_PASSWORD=your_password
```

4. Initialize the database:
```bash
python config/db_connection.py
python config/setup_db.py
```

## 📁 Project Structure

```
faculty-schedule-logger/
├── config/
│   ├── db_connection.py    # Database connection
│   └── setup_db.py         # Database initialization script
├── src/
│   ├── crud.py             # Main console application
│   └── etl.py              # ETL processing script
├── data/
│   └── data.json           # Sample faculty data
├── logs/
│   └── time_logs.xlsx      # Exported time logs
├── requirements.txt
└── README.md
```

## 🚦 Usage

1. Start the database connection:
```bash
python config/db_connection.py
```

2. Initialize the database:
```bash
python config/setup_db.py
```

3. Run the main application:
```bash
python src/crud.py
```

4. Navigate the menu using number keys:
   - `1` - Time-In/Out Management
   - `2` - Manage Faculty Schedules
   - `3` - Export Time Logs
   - `4` - Exit

5. Process time logs:
```bash
python src/etl.py
```

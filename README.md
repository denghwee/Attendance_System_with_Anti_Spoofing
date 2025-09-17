
<h1 align="center">
  <br>
  Attendance System with Silent Anti-spoofing
  <br>
</h1>

![Python Version](https://img.shields.io/badge/python-3.11.7%2B-blue)

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

* Check-In/Check-Out
  - Manual attendance marking (With button click)
  - Real-time entry/exit tracking with timestamps
* Attendance Tracking & Logs
  - Daily logs of attendance
  - Ability to track late arrivals, early leaves and absences
  - Preserve the possibily of each attendance is whether a fraud or not
* Reporting & Analytics
  - Generate reports include all days till now of all attendance
  - Exports to CSV
* Silent anti-spoofing involve
  - Can easily be installed without needed advanced equipments, such as: 3D Camera,...
  - Use the latest Mini-FasNET-v2 model of Minivision-AI
## How To Use

To clone and use this repository, you'll need [Git](https://git-scm.com) From your command line:

```bash
# Clone this repository
$ git clone https://github.com/denghwee/Attendance_System_with_Anti_Spoofing

# Go into the repository
$ cd Attendance_System_With_Anti_Spoofing

# Install dependencies
$ pip install requirements.txt
```

To run test repository

```bash
streamlit run main.py
```

## Credits

This repository uses the following open source package:

- [Silent-Anti-Spoofing](https://github.com/minivision-ai/Silent-Face-Anti-Spoofing)

## License

MIT

---


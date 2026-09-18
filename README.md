
# Keyanta – Typing Automation

**Keyanta** is a lightweight and customizable typing automation application for Windows, built with Python. It helps simplify typing practice and repetitive text-entry tasks through adjustable typing speed, pause and resume controls, floating mini mode, delay settings, and a modern interface.

Keyanta is designed to provide a simple and convenient typing experience with customizable controls and real-time progress tracking.

## Features

- **Adjustable Typing Speed:** Customize typing speed according to your requirements.
- **Pause and Resume:** Pause the typing process and resume whenever needed.
- **Floating Mini Mode:** Keep Keyanta accessible in a compact floating window while working on other applications.
- **Delay Control:** Configure delays before typing operations.
- **Opacity Control:** Adjust application window transparency.
- **Typing Progress:** Monitor typing progress and completed words.
- **Typing Speed Indicator:** View the configured typing speed in words per minute (WPM).
- **Local Mode:** Use the application in its local operating mode.
- **Modern Interface:** Clean, compact, and glassmorphism-inspired user interface.
- **Windows Executable:** Run the application using the prebuilt `Keyanta.exe` without manually launching the Python source code.

## Screenshots

### Main Interface

Keyanta provides a compact interface for managing typing speed, progress, opacity, delay, and typing controls.

<!-- Add your application screenshot here -->

## System Requirements

| Requirement | Details |
|---|---|
| Operating System | Microsoft Windows |
| Architecture | Compatible Windows architecture |
| Application | Keyanta.exe |
| Internet Connection | Not necessarily required for local functionality |
| Python | Required only when running from source |
| Additional Dependencies | Included or managed according to the application build |

## Download and Installation

### Option 1: Download Keyanta for Windows

1. Open the [Keyanta Releases](https://github.com/Vaibhav-Chaurasiya/typing-automation/releases) page.
2. Find the latest available release.
3. Download the Windows executable or ZIP package attached to the release.
4. If you downloaded a ZIP file, extract it.
5. Locate `Keyanta.exe`.
6. Double-click the executable to launch Keyanta.

**Note:** Download only the files published in the official repository's Releases section.

### Option 2: Run from Source Code

You can also run Keyanta directly from its Python source code.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Vaibhav-Chaurasiya/typing-automation.git
```

#### Step 2: Navigate to the Project Directory

```bash
cd typing-automation
```

#### Step 3: Install Dependencies

Make sure Python is installed on your Windows computer.

```bash
python -m pip install -r requirements.txt
```

#### Step 4: Launch the Application

```bash
python main.py
```

**Note:** Run these commands from the directory containing `main.py` and `requirements.txt`. If dependencies are missing, install the packages specified in the requirements file.

## How to Use

### 1. Launch Keyanta

Open `Keyanta.exe` or launch the application from its Python source code.

### 2. Configure Typing Speed

Adjust the typing speed using the available WPM control.

### 3. Set the Delay

Use the Delay control to configure the timing before typing operations.

### 4. Start Typing

Click the Start button to begin the typing process.

### 5. Pause or Resume

Use the available controls to pause and resume typing as needed.

### 6. Use Mini Mode

Enable Mini mode to keep Keyanta accessible in a compact floating window.

### 7. Adjust Opacity

Customize the application's transparency using the opacity control.

### 8. Monitor Progress

Track typing speed, completed words, and overall typing progress through the application interface.

## Project Structure

The project contains the Python application source code, build configuration, and Windows executable.

```text
typing-automation/
│
├── app/
│   ├── engine.py
│   └── ui.py
│
├── build/
│   └── Keyanta/
│
├── dist/
│   └── Keyanta.exe
│
├── web/
│   ├── .gitattributes
│   ├── Keyanta.spec
│   ├── LICENSE
│   ├── main.py
│   └── requirements.txt
│
├── .gitattributes
├── LICENSE
└── README.md
```

**Note:** The build directory contains generated build resources. The `dist` directory contains the packaged Windows executable.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| PyInstaller | Packaging Python application into a Windows executable |
| Tkinter / UI Libraries | Desktop interface, depending on the implementation |
| Windows | Target operating system |

The exact dependencies are listed in `requirements.txt`.

## Building the Executable

To create a Windows executable from the source code, install the required dependencies and PyInstaller.

```bash
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

Build the application using the provided PyInstaller specification:

```bash
python -m PyInstaller Keyanta.spec
```

Alternatively, if building directly from `main.py`:

```bash
python -m PyInstaller --onefile --windowed --name Keyanta main.py
```

The generated executable is typically placed in the `dist` directory.

**Important:** The specification file and build configuration should be used from their correct project directory.

## Use Cases

Keyanta can be useful for:

- Typing practice and speed testing.
- Repetitive text-entry tasks.
- Testing typing speed and timing configurations.
- Managing typing automation through a compact desktop interface.
- Desktop application workflow testing.

## Privacy and Responsible Use

Keyanta is intended to provide local typing automation functionality.

- Review the application behavior before using it with sensitive information.
- Avoid automating confidential information into third-party applications.
- Use typing automation only in applications where you have permission to do so.
- Check the source code to understand how the application handles data and input.

## Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork this repository.
2. Create a new branch.
3. Make your changes.
4. Test your changes.
5. Commit your changes with a descriptive message.
6. Open a Pull Request describing your contribution.

For major changes, consider opening an issue before starting development.

## Issues and Feature Requests

If you encounter a bug or have an idea for a new feature, please open an issue in the repository.

When reporting a bug, include:

- A clear description of the issue.
- Steps to reproduce the problem.
- Your Windows version.
- Relevant screenshots or error messages.
- Any additional information that may help reproduce the issue.

## Roadmap

Potential improvements for future versions:

- [ ] Improve typing statistics and progress tracking.
- [ ] Add additional customization options.
- [ ] Improve the user interface and accessibility.
- [ ] Expand documentation and usage examples.
- [ ] Continue improving Windows application packaging.
- [ ] Add new features based on user feedback.

## License

This project is distributed under the terms of the [Apache License 2.0](LICENSE).

Please review the license before using, modifying, or distributing the project.

## Author

**Vaibhav Chaurasiya**

GitHub: [@Vaibhav-Chaurasiya](https://github.com/Vaibhav-Chaurasiya)

## Repository

[Keyanta – Typing Automation](https://github.com/Vaibhav-Chaurasiya/typing-automation)

## Releases

Download available application versions from the [GitHub Releases](https://github.com/Vaibhav-Chaurasiya/typing-automation/releases) page.

---

**Keyanta – A lightweight and customizable typing automation tool for Windows.**

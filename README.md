# Respos File Organiser

## Description
Respos File Organiser is a Python application that helps you organize and manage your files efficiently. It is a user-friendly Python automation app with powerful features that allow you to create custom file types with their extensions and dynamically add directories/folders for sorting. This program will help you keep all your folders organised.

## Installation
1. Clone the repository and download it on your computer.
2. Make sure you have Python installed on your computer
3. Run the application using Python Launcher

Depencencies used for the program should automaticaly install on your first run. If a error occures due to dependencies not being installed, you can install the nessasary dependency by running this command in your terminal

`pip install customtkinter`

You can edit the different file types and there associated extenctions in the csv file. You can simply open it with any text editor, write the type of file and seperated by a comma, write the extenctions, seperating the extenctions with commas as well.

__Note:__ Please do not move any file out of the Respos File Organiser folder. Maintain the contents of Respos File Organiser folder for the program to work as intended. If not, you can lose some of the contents used in the program.

__Note:__ Backups are currently required just incase something goes wrong in moving the files somewhere or if you move it to somewhere you are not aware of. Backups are stored as zip files so it should take a smaller amount of space and old backups are deleted. In the program, you can specify how many saves you would want to keep. The program is in its very early stages and bugs and features maybe limited

## Features
- User-Friendly Interface
- Built in Error Checking
- Ability to produce backup of what you are sorting
- Lightweight and portable

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## How to Use

The program is composed of five main sections:

- The Menu Bar
- The Backup Box
- The Directory From Box
- The Directory To Box
- Status Box

<img width="800" alt="Screenshot 2024-01-31 at 2 04 34 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/0d071152-7efc-4fca-bebe-c705e4ed6119">

### Menu Bar

The Menu Bar provides buttons for saving, running on click, and auto running. Clicking the save button preserves the textbox contents for later use. Running on click sorts files immediately, while auto run continuously sorts files, delayed by the specified run time intervals in the Backup Box.
<img width="1317" alt="Screenshot 2024-01-31 at 2 45 26 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/10354501-868a-4218-bdde-15d07cf60c5c">


### Backup Box

The Backup Box is crucial for creating backups of files before sorting. At this program stage, creating a backup is mandatory.

- **Enter Backup Directory:** Type a directory into the textbox or use the directory button to select one using a dialog.
- **Backup History:** Choose the number of backups to keep in your backup folder.
- **Run Time Intervals:** Used during auto run to define sorting intervals.

__Backup Box and dialog when clicking directory button__

<img width="300" alt="Screenshot 2024-01-31 at 2 52 34 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/7b2abfaf-c1ff-43b8-9276-b71797773376">
<img width="500" alt="Screenshot 2024-01-31 at 2 54 29 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/4af40af5-525e-44b5-aa07-2aeb5315239a">

### Directory From Box

The Directory From Box allows users to specify the source directory for file sorting.
<img width="800" alt="Screenshot 2024-01-31 at 2 56 29 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/57c09d42-37b0-4cbe-8e09-2593b3adef92">

### Directory To Box

The Directory To Box enables users to define the destination directory for file sorting. The destination depends on the file type. You can choose the file type and its associated directory, and add or remove destinations using the close or plus button.
<img width="800" alt="Screenshot 2024-01-31 at 2 56 29 pm" src="https://github.com/leonfrancis37/Respos-File-Automator-And-Organiser/assets/158222407/2f194c65-c7c6-49cf-b921-6c55d6ac4d31">

## License
This project is licensed under BY-NC-SA 4.0 License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments
- Respos File Organiser relies on customtkinter for the GUI

## Contact
For questions or feedback, feel free to reach out at leonfrancis37@outlook.com.

## Changelog
- Keep

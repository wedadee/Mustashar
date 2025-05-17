# Mustashrik Django Project Installation

This guide provides simple terminal commands to install and run the Mustashrik Django project from a GitHub ZIP file in Microsoft Visual Studio on Windows.

## Prerequisites

- **Python**: Version 3.9 or higher installed (python.org).
- **Microsoft Visual Studio**: Community, Professional, or Enterprise (2022 recommended).
- **Git** (optional for cloning, not required for ZIP download).
- **A web browser** to download the ZIP file.

## Installation Commands

1. **Download and Extract the ZIP**

   - Go to the Mustashrik GitHub repository (e.g., `https://github.com/wedadee/Mustashar`).
   - Click the green **Code** button and select **Download ZIP**.
   - Save the ZIP file (e.g., `mustashrik-main.zip`) to a local directory (e.g., `C:\Projects`).
   - Extract the ZIP file to a folder (e.g., `C:\Projects\mustashrik-main`) using a tool like File Explorer, WinRAR, or 7-Zip.

2. **Open the Project in Microsoft Visual Studio**

   - Open Microsoft Visual Studio.
   - Go to **File > Open > Project/Solution**, navigate to `C:\Projects\mustashrik-main`, and open the project folder.
   - In the **Solution Explorer** (usually on the right), locate the solution name (e.g., `mustashrik-main`).
   - Right-click the solution name and select **Open Command Prompt Here** to open a terminal in the project directory.

3. **Install Dependencies from requirements.txt**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Django Development Server**

   ```bash
   python manage.py runserver
   ```

5. **Access the Application**

   - Open a browser and go to `http://localhost:8000`.

## Notes

- Replace `C:\Projects\mustashrik-main` with the actual path where you extracted the ZIP.
- If `requirements.txt` is missing, contact the repository maintainer or install Django manually with `pip install django`.
- If you encounter errors (e.g., port conflicts), try `python manage.py runserver 8001` to use a different port.
- To stop the server, press `Ctrl+C` in the terminal.

For further details, refer to the Mustashrik repository’s documentation or the Django documentation.

# 🧾 First Inspection Report Generator

A desktop app to **automatically generate First Inspection Reports** with embedded photos and insurance data using an Excel/CSV input.

---

## 🖥️ GUI Instructions (No Coding Needed)

### ▶️ How to Use

1. **Run the App**
   - **From source:**
     ```bash
     python main.py
     ```
   - Or double-click the `InspectionPro.exe` (if using the EXE version)

2. **Main Interface Overview**

   > **Window Title:** `Inspection Pro`

Select Input CSV/Excel File [Browse]

Select Images Folder [Browse]

Select Output Folder [Browse]

[ Generate ] (Button)

Status: Ready

markdown
Copy
Edit

3. **What to Do**
- 📄 Select your Excel/CSV file that has insured party details.
- 🖼️ Select a folder that contains:
  - Room folders (e.g., `bedroom1/`, `kitchen/`)
  - Optional `header.jpg` and `footer.jpg` images in the root
- 📂 Choose output folder for saving generated Word reports
- ✅ Click **“Generate Reports”**
- 🟢 Watch progress in the status bar.

**📁 Output Example:**
Output/
└── FIRST INSPECTION REPORT - CLAIM# AB12345 - SMITH - 123_MAIN_ST.docx

yaml
Copy
Edit

---

## 🛠️ Create an EXE (No Python Needed for Users)

### 🔧 Method 1: PyInstaller (Recommended)

1. **Install PyInstaller**
```bash
pip install pyinstaller
Build the Executable

Basic build:

bash
Copy
Edit
pyinstaller --onefile --windowed --add-data "app/templates;app/templates" --add-data "assets;assets" --hidden-import "jinja2.ext" --paths "app" --name InspectionReport main.py

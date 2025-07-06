import tkinter as tk
from app.views.main_window import ReportGeneratorUI
from app.core.report_engine import InspectionReportEngine
from config.settings import CONFIG

def main():
    root = tk.Tk()
    
    
    report_engine = InspectionReportEngine(CONFIG)
    app_ui = ReportGeneratorUI(root, report_engine)
    
    root.mainloop()

if __name__ == "__main__":
    main()
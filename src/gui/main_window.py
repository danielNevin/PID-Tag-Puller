"""Main application window using CustomTkinter."""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from pdf_processor.extractor import PDFExtractor
from tag_extractor.extractor import TagExtractor
from csv_exporter.exporter import CSVExporter


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        # Set theme BEFORE creating window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        super().__init__()

        # Configure window
        self.title("PID-Tag Puller")
        self.geometry("800x600")

        # Initialize variables
        self.pdf_path = None
        self.output_dir = None
        self.extracted_tags = []
        self.tag_summary = {}

        # Create UI
        self._create_widgets()

        # Force UI update to ensure widgets are rendered
        self.update_idletasks()

    def _create_widgets(self):
        """Create and layout all widgets."""
        # Main container with padding
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="PID-Tag Puller",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # File selection frame
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=10)

        # PDF selection
        pdf_label = ctk.CTkLabel(file_frame, text="PDF File:", font=ctk.CTkFont(size=14))
        pdf_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.pdf_entry = ctk.CTkEntry(file_frame, placeholder_text="No file selected")
        self.pdf_entry.pack(fill="x", padx=10, pady=5)

        pdf_button = ctk.CTkButton(
            file_frame,
            text="Select PDF",
            command=self._select_pdf
        )
        pdf_button.pack(padx=10, pady=5)

        # Output directory selection
        output_label = ctk.CTkLabel(file_frame, text="Output Directory:", font=ctk.CTkFont(size=14))
        output_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.output_entry = ctk.CTkEntry(file_frame, placeholder_text="No directory selected")
        self.output_entry.pack(fill="x", padx=10, pady=5)

        output_button = ctk.CTkButton(
            file_frame,
            text="Select Output Directory",
            command=self._select_output_dir
        )
        output_button.pack(padx=10, pady=(5, 10))

        # Extract button
        self.extract_button = ctk.CTkButton(
            main_frame,
            text="Extract Tags",
            command=self._extract_tags,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        self.extract_button.pack(pady=20)

        # Progress/status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

        # Results frame
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, pady=10)

        results_title = ctk.CTkLabel(
            results_frame,
            text="Extracted Tags Preview:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_title.pack(anchor="w", padx=10, pady=(10, 5))

        # Text box for results
        self.results_text = ctk.CTkTextbox(results_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Export button (initially disabled)
        self.export_button = ctk.CTkButton(
            main_frame,
            text="Export to CSV",
            command=self._export_csv,
            state="disabled"
        )
        self.export_button.pack(pady=10)

    def _select_pdf(self):
        """Open file dialog to select PDF."""
        filename = filedialog.askopenfilename(
            title="Select P&ID PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path = Path(filename)
            self.pdf_entry.delete(0, "end")
            self.pdf_entry.insert(0, str(self.pdf_path))

    def _select_output_dir(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = Path(directory)
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, str(self.output_dir))

    def _extract_tags(self):
        """Extract tags from the selected PDF."""
        if not self.pdf_path:
            messagebox.showerror("Error", "Please select a PDF file first")
            return

        # Run extraction in a separate thread to avoid freezing UI
        thread = threading.Thread(target=self._extraction_worker, daemon=True)
        thread.start()

    def _extraction_worker(self):
        """Worker function for tag extraction (runs in separate thread)."""
        try:
            # Update status
            self.status_label.configure(text="Extracting text from PDF...")

            # Extract text from PDF
            pdf_extractor = PDFExtractor(self.pdf_path)
            text = pdf_extractor.extract_text()

            # Extract tags
            self.status_label.configure(text="Identifying tags...")
            tag_extractor = TagExtractor(text)
            self.extracted_tags = tag_extractor.extract_all_tags(deduplicate=True)
            self.tag_summary = tag_extractor.get_summary()

            # Update UI with results
            self._display_results()

            # Enable export button
            self.export_button.configure(state="normal")

            # Update status
            self.status_label.configure(
                text=f"Extraction complete! Found {self.tag_summary['total_unique']} unique tags"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error during extraction:\n{str(e)}")
            self.status_label.configure(text="Error during extraction")

    def _display_results(self):
        """Display extraction results in the text box."""
        self.results_text.delete("1.0", "end")

        # Display summary
        summary_text = f"""Summary:
- Total unique tags: {self.tag_summary['total_unique']}
- Total instances: {self.tag_summary['total_instances']}
- Pumps: {self.tag_summary['pumps']}
- Valves: {self.tag_summary['valves']}
- Instruments: {self.tag_summary['instruments']}
- Equipment: {self.tag_summary['equipment']}
- Other: {self.tag_summary['other']}

Tags (showing first 50):
"""
        self.results_text.insert("1.0", summary_text)

        # Display first 50 tags
        preview_tags = self.extracted_tags[:50]
        for tag in preview_tags:
            self.results_text.insert("end", f"{tag}\n")

        if len(self.extracted_tags) > 50:
            self.results_text.insert("end", f"\n... and {len(self.extracted_tags) - 50} more tags")

    def _export_csv(self):
        """Export extracted tags to CSV."""
        if not self.extracted_tags:
            messagebox.showerror("Error", "No tags to export")
            return

        # Use selected output directory or ask for location
        if self.output_dir:
            default_filename = f"{self.pdf_path.stem}_tags.csv"
            output_path = self.output_dir / default_filename

            # Confirm overwrite if file exists
            if Path(output_path).exists():
                if not messagebox.askyesno("Confirm", f"File already exists:\n{output_path}\n\nOverwrite?"):
                    return
        else:
            output_path = filedialog.asksaveasfilename(
                title="Save CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"{self.pdf_path.stem}_tags.csv" if self.pdf_path else "tags.csv"
            )
            if not output_path:
                return

        try:
            # Export to CSV
            CSVExporter.export_tags(self.extracted_tags, output_path)

            # Update status
            self.status_label.configure(text=f"Exported to {Path(output_path).name}")

            messagebox.showinfo(
                "Success",
                f"Exported {len(self.extracted_tags)} tags to:\n{output_path}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting CSV:\n{str(e)}")
            import traceback
            traceback.print_exc()  # Print full error to console for debugging

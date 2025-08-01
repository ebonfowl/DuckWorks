"""
PyQt6 ComboBox Style Options - Test Different Styles
Copy any of these styles into your Canvas GUI to try them out!
"""

# Style Option 1: Modern Flat Design
modern_flat_style = """
QComboBox {
    border: 2px solid #3498db;
    border-radius: 8px;
    padding: 10px 15px;
    background-color: white;
    font-size: 11pt;
    font-weight: 500;
    min-width: 250px;
}
QComboBox:hover {
    border-color: #2980b9;
    background-color: #f8f9fa;
}
QComboBox:focus {
    border-color: #2980b9;
    background-color: #ffffff;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
    background-color: #3498db;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid white;
    margin: 0px 8px;
}
QComboBox QAbstractItemView {
    border: 2px solid #3498db;
    border-radius: 8px;
    background-color: white;
    selection-background-color: #3498db;
    selection-color: white;
    padding: 5px;
}
"""

# Style Option 2: Material Design
material_style = """
QComboBox {
    border: none;
    border-bottom: 2px solid #e0e0e0;
    border-radius: 0px;
    padding: 12px 40px 12px 15px;
    background-color: transparent;
    font-size: 11pt;
    min-width: 250px;
}
QComboBox:hover {
    border-bottom: 2px solid #2196f3;
    background-color: rgba(33, 150, 243, 0.04);
}
QComboBox:focus {
    border-bottom: 2px solid #2196f3;
    background-color: white;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
    background-color: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid #757575;
    margin-right: 10px;
}
QComboBox::down-arrow:hover {
    border-top-color: #2196f3;
}
QComboBox QAbstractItemView {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: white;
    selection-background-color: #2196f3;
    selection-color: white;
    padding: 2px;
}
"""

# Style Option 3: macOS-like
macos_style = """
QComboBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 30px 8px 12px;
    background-color: white;
    font-size: 11pt;
    min-width: 250px;
}
QComboBox:hover {
    border-color: #9ca3af;
    background-color: #f9fafb;
}
QComboBox:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
QComboBox::drop-down {
    border: none;
    width: 25px;
    background-color: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #6b7280;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background-color: white;
    selection-background-color: #3b82f6;
    selection-color: white;
    padding: 4px;
}
"""

# Style Option 4: Windows 11-like
windows11_style = """
QComboBox {
    border: 1px solid #8a8886;
    border-radius: 4px;
    padding: 9px 32px 9px 12px;
    background-color: #ffffff;
    font-size: 11pt;
    font-family: "Segoe UI Variable Display";
    min-width: 250px;
}
QComboBox:hover {
    border-color: #323130;
    background-color: #f3f2f1;
}
QComboBox:focus {
    border-color: #0078d4;
    border-width: 2px;
    background-color: white;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
    background-color: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #323130;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    border: 1px solid #8a8886;
    border-radius: 4px;
    background-color: white;
    selection-background-color: #0078d4;
    selection-color: white;
    outline: none;
}
"""

# Style Option 5: Dark Theme
dark_theme_style = """
QComboBox {
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 10px 35px 10px 15px;
    background-color: #2b2b2b;
    color: #ffffff;
    font-size: 11pt;
    min-width: 250px;
}
QComboBox:hover {
    border-color: #666666;
    background-color: #3c3c3c;
}
QComboBox:focus {
    border-color: #0078d4;
    background-color: #2b2b2b;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
    background-color: #444444;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid #ffffff;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    border: 1px solid #444444;
    border-radius: 6px;
    background-color: #2b2b2b;
    color: white;
    selection-background-color: #0078d4;
    selection-color: white;
}
"""

# Style Option 6: Gradient Style
gradient_style = """
QComboBox {
    border: 1px solid #bbb;
    border-radius: 8px;
    padding: 10px 35px 10px 15px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f0f0f0);
    font-size: 11pt;
    min-width: 250px;
}
QComboBox:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f8f8f8, stop: 1 #e8e8e8);
}
QComboBox:focus {
    border-color: #0078d4;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f5f5f5);
}
QComboBox::drop-down {
    border: none;
    width: 30px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #4a90e2, stop: 1 #357abd);
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid white;
    margin-right: 8px;
}
"""

print("Choose any of these styles to replace the current ComboBox styling!")
print("You can also mix and match properties from different styles.")
print("See the Qt documentation links above for more customization options!")

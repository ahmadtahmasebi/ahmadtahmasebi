# Product Manager Application

This is a product management application built with PyQt5 and SQLite.

## Installation

### Prerequisites

- Python 3.6 or higher

### Installing Dependencies

There are two ways to install the required dependencies:

#### Option 1: Using the installation script

Run the installation script:

```
python install_dependencies.py
```

#### Option 2: Manual installation

Install the required packages using pip:

```
pip install -r requirements.txt
```

## Running the Application

After installing the dependencies, you can run the application:

```
python product_manager_fixed.py
```

## Troubleshooting

If you encounter the error `ModuleNotFoundError: No module named 'pandas'` or similar errors for other packages, it means that the required dependencies are not installed. Please follow the installation instructions above.

## Features

### Core Features
- Product management (add, edit, delete)
- Inventory tracking
- Category management
- Barcode generation
- Reporting
- User activity logging

### New Features
- **Import Products**: Import product data from Excel or CSV files
- **Export Products**: Export product lists to Excel, CSV, or PDF formats
- **Advanced Image Management**:
  - Multiple images per product
  - Image gallery view
  - Primary image selection
  - Bulk image operations
- **External System Integration**:
  - Connect to external product management systems
  - Synchronize products, inventory, and prices
  - Scheduled automatic synchronization
  - Support for various system types (ERP, CRM, etc.)
- **Product Management Forms**:
  - Standard product management form
  - Customizable forms with field selection
  - Form designer with drag-and-drop interface
  - Form templates and saving options

## Import/Export Features

### Import
- Import products from Excel files (.xlsx, .xls)
- Import products from CSV files (.csv)
- Preview data before import
- Option to clear existing products before import
- Progress tracking during import

### Export
- Export to Excel with formatting
- Export to CSV for compatibility with other systems
- Export to PDF with product details and images
- Custom report generation

## Image Management

- Upload and manage multiple images per product
- Set primary product image
- View images in gallery mode
- Bulk image operations
- Image preview and zoom

## External System Integration

### Connection Features
- Connect to various external product management systems:
  - Retail systems
  - Inventory management systems
  - Accounting systems
  - CRM systems
  - ERP systems
- Flexible connection options:
  - API key authentication
  - Username/password authentication
  - Custom server and port configuration

### Synchronization Options
- Selective synchronization of:
  - Products
  - Inventory levels
  - Prices
  - Categories
  - Product images
- Synchronization scheduling:
  - Manual synchronization
  - Hourly updates
  - Daily updates
  - Weekly updates
- Real-time progress tracking during synchronization
- Detailed synchronization logs

## Product Management Forms

### Standard Form
- Complete product management interface
- Search functionality with advanced options
- Product information fields:
  - Basic details (name, category, price)
  - Inventory management (stock, minimum stock)
  - Image management
  - Description and additional information
- Operations:
  - Add new products
  - Edit existing products
  - Delete products
  - Print product information

### Customizable Form
- Field selection and visibility options
- Appearance customization:
  - Theme selection
  - Font customization
  - Size adjustments
- Real-time form preview
- Save custom configurations

### Form Designer
- Drag-and-drop interface for form creation
- Available components:
  - Text labels
  - Input fields (text, numeric)
  - Dropdown menus
  - Checkboxes and radio buttons
  - Buttons
  - Images
  - Tables
  - Grouping containers
- Property editor for component customization
- Save and load form designs

### Form Templates
- Save forms as reusable templates
- Load templates for quick form creation
- Share templates between users
- Default templates for common use cases

## Notes

- The application creates a SQLite database file named `products.db` in the same directory.
- Product images are stored in the `product_images` directory.
- Application settings are stored in the `settings` directory.
- Barcode images are automatically generated and stored in the `product_images` directory.
# automation-framework

A structured automation framework that provides a reliable foundation for building web and desktop automations using the **Page Object Model (POM)** architecture. This framework eliminates the complexity of direct Selenium/PyAutoGUI usage by offering pre-built, tested helper classes and utilities.

## Purpose

This project provides a standardized structure that allows developers to focus on automation logic rather than implementation details. Instead of worrying about driver instantiation, element locating strategies, or error handling, you simply use the provided helpers to build your automation workflows.

The framework implements the proven **Page Object Model (POM)** design pattern, organizing automation code into maintainable, scalable components that follow industry best practices.

## Architecture

### Platform Helpers
Located in the `platforms` directory, these provide the core automation capabilities:
- **Selenium Helper**: Advanced element locating, waiting strategies, and interaction methods
- **PyAutoGUI Helper**: Desktop automation utilities with debugging support

### Application Structure (Page Object Model)
Each automation project follows the **Page Object Model (POM)** pattern in the `app` folder:

```
app/
└── your_automation_project/
    ├── pages/
    │   ├── home_page.py      # Page Object Classes
    │   ├── login_page.py     # Represent individual pages
    │   └── feed_page.py      # Contain elements and page methods
    ├── workflow/
    │   ├── like_image.py     # Test Scripts / User Flows
    │   ├── upload_post.py    # Individual automation tasks
    │   └── search_items.py   # Combine page methods for complete actions
    └── data/
        └── test_data.json    # External data for tests
```

### Pages Folder (Page Objects)
Contains **Page Object Classes** where each web page becomes a dedicated class. Following POM principles, each class defines its elements as class attributes and provides methods that represent user actions on that page. This centralizes element definitions, allowing for easy maintenance when selectors change.

Example structure:
```python
class HomePage:
    def __init__(self):
        # Define page elements as attributes
        self.search_bar = (By.ID, "search-input")
        self.feed_section = (By.CLASS_NAME, "feed-container")
    
    def search(self, query):
        # Page methods encapsulate user actions
        pass
```

### Workflow Folder (Test Scripts/User Flows)
Contains **Test Script Files** that represent individual user scenarios or workflows. Each file implements a specific task by combining methods from different Page Objects, following the separation of concerns principle. This approach ensures clear, maintainable automation scripts.

## Benefits of Page Object Model Architecture

- **Maintainability**: Element selectors defined in one place across the entire project
- **Reusability**: Page methods can be combined in multiple workflows
- **Readability**: Clear separation between page structure and user actions
- **Scalability**: Easy to extend with new pages and workflows
- **Industry Standard**: Follows widely accepted test automation best practices

## Usage Pattern

1. Create a new folder in `app` for your automation project
2. Define **Page Object Classes** in the `pages` folder with their respective elements
3. Create individual **Workflow Scripts** in the `workflow` folder for each user scenario
4. Use the platform helpers to interact with elements and perform actions

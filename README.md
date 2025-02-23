
Sprinter - A Collaborative Sprint Management Tool
===================================================

Overview:
---------
Sprinter is a web-based application that helps teams manage sprints,
tasks, and user assignments in an agile workflow. Built using Django and
modern JavaScript (with drag-and-drop features), Sprinter is designed to
provide a visually engaging and intuitive interface for managing projects.

Features:
---------
- **User Authentication:**  
  Log in using Google and enjoy a personalized experience with user avatars.
  
- **Sprint Management:**  
  Create, view, and manage sprints. Each sprint displays its tasks,
  schedule, progress statistics, and guest participants.

- **Task Tracking:**  
  Organize tasks into columns ("todo", "in-progress", "done").  
  Drag and drop tasks between columns to update their status in real time.

- **Responsive UI:**  
  A clean, modern interface built with custom CSS styles and Google Fonts.
  The interface adapts to various screen sizes for desktop and mobile devices.

- **Custom Avatars & Icons:**  
  Uses external services like DiceBear and UI Avatars to generate
  unique user images, with CSS transforms (e.g., flipping images) for enhanced
  visual effects.

- **Dynamic Interactions:**  
  Interactive modals (popups) for sprint and task creation, as well as 
  guest invitation and sprint finalization.
  
- **Local Storage Persistence:**  
  Remembers the state of dropdowns (sprint boards) using localStorage,
  ensuring a personalized layout across sessions.

Project Structure:
------------------
- **Templates (HTML):**  
  The HTML templates use Django templating with static assets and inline CSS.
  They include sections for user cards, sprint information, task boards, and popups.

- **Static Assets:**  
  Custom CSS is provided directly within the template for simplicity.  
  External fonts are imported from Google Fonts.

- **JavaScript Interactions:**  
  - Drag and drop functionality for tasks.
  - Dropdown toggles for sprint boards.
  - Dynamic styling adjustments (e.g., flipping images using CSS transforms).
  - AJAX calls to update task status via Django views.

- **Backend (Django):**  
  - Views handle user authentication, sprint/task creation, and status updates.
  - Models include User, Sprint, and Task, with fields such as `storyPoints`
    and auto-updating timestamps (handled via a custom save method for Unix timestamps).

How to Run:
-----------
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/sprinter.git
   cd sprinter

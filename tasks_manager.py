import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# ---------------------------------------------------------
# Firestore configuration
# ---------------------------------------------------------

SERVICE_ACCOUNT_FILE = "tasksmanager-key.json"

PROJECTS_COLLECTION = "projects"
TASKS_COLLECTION = "tasks"


def initialize_firestore():
    """Initialize Firebase and return the Firestore client."""

    try:
        firebase_admin.get_app()
    except ValueError:
        credential = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(credential)

    return firestore.client()


db = initialize_firestore()


# ---------------------------------------------------------
# General utility functions
# ---------------------------------------------------------

def print_separator():
    print("\n" + "=" * 55)


def pause():
    input("\nPress Enter to continue...")


def read_non_empty(prompt):
    """Request a non-empty text value."""

    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This value cannot be empty.")


def confirm(prompt):
    """Request a yes/no confirmation."""

    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please enter 'y' or 'n'.")


def choose_document(documents, entity_name):
    """
    Allow the user to select a Firestore document
    by its displayed number.
    """

    if not documents:
        return None

    while True:
        try:
            choice = int(
                input(
                    f"\nSelect a {entity_name} number "
                    f"or enter 0 to cancel: "
                )
            )

            if choice == 0:
                return None

            if 1 <= choice <= len(documents):
                return documents[choice - 1]

            print("Invalid selection.")

        except ValueError:
            print("Please enter a valid number.")


# ---------------------------------------------------------
# Project functions
# ---------------------------------------------------------

def get_projects():
    """Return all projects ordered alphabetically."""

    documents = list(
        db.collection(PROJECTS_COLLECTION).stream()
    )

    documents.sort(
        key=lambda document:
        document.to_dict().get("name", "").lower()
    )

    return documents


def display_projects():
    """Display every project and return the documents."""

    print_separator()
    print("PROJECTS")
    print_separator()

    projects = get_projects()

    if not projects:
        print("No projects found.")
        return []

    for index, project in enumerate(projects, start=1):
        data = project.to_dict()

        name = data.get("name", "Unnamed project")
        status = data.get("status", "Unknown")

        print(f"{index}. {name}")
        print(f"   Status: {status}")
        print(f"   ID: {project.id}")

    return projects


def create_project():
    """Create a new project."""

    print_separator()
    print("CREATE PROJECT")
    print_separator()

    name = read_non_empty("Project name: ")

    project_data = {
        "name": name,
        "status": "In progress",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }

    project_reference = (
        db.collection(PROJECTS_COLLECTION).document()
    )

    project_reference.set(project_data)

    print("\nProject created successfully.")
    print(f"Project ID: {project_reference.id}")


def rename_project():
    """Change the name of an existing project."""

    projects = display_projects()

    project = choose_document(projects, "project")

    if project is None:
        return

    current_data = project.to_dict()
    current_name = current_data.get("name", "")

    print(f"\nCurrent name: {current_name}")

    new_name = read_non_empty("New project name: ")

    project.reference.update({
        "name": new_name,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    print("\nProject updated successfully.")


def get_tasks_by_project(project_id):
    """Return all tasks associated with a project."""

    query = (
        db.collection(TASKS_COLLECTION)
        .where(
            filter=FieldFilter(
                "project_id",
                "==",
                project_id
            )
        )
    )

    tasks = list(query.stream())

    tasks.sort(
        key=lambda document:
        document.to_dict().get("title", "").lower()
    )

    return tasks


def delete_project():
    """
    Delete a project and all tasks associated
    with that project.
    """

    projects = display_projects()

    project = choose_document(projects, "project")

    if project is None:
        return

    project_data = project.to_dict()
    project_name = project_data.get("name", "Unnamed project")

    tasks = get_tasks_by_project(project.id)

    print(f"\nProject: {project_name}")
    print(f"Related tasks: {len(tasks)}")

    if not confirm(
        "Delete this project and all of its related tasks?"
    ):
        print("Deletion cancelled.")
        return

    # Delete every task related to the project
    for task in tasks:
        task.reference.delete()

    # Delete the project
    project.reference.delete()

    print("\nProject and related tasks deleted successfully.")


# ---------------------------------------------------------
# Task functions
# ---------------------------------------------------------

def display_tasks(project_id):
    """Display tasks belonging to one project."""

    tasks = get_tasks_by_project(project_id)

    print_separator()
    print("PROJECT TASKS")
    print_separator()

    if not tasks:
        print("No tasks found for this project.")
        return []

    for index, task in enumerate(tasks, start=1):
        data = task.to_dict()

        title = data.get("title", "Untitled task")
        completed = data.get("completed", False)

        status = "Completed" if completed else "Pending"

        print(f"{index}. {title}")
        print(f"   Status: {status}")
        print(f"   ID: {task.id}")

    return tasks


def create_task(project_id):
    """Create a task associated with a project."""

    print_separator()
    print("CREATE TASK")
    print_separator()

    title = read_non_empty("Task title: ")

    task_data = {
        "title": title,
        "project_id": project_id,
        "completed": False,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }

    task_reference = (
        db.collection(TASKS_COLLECTION).document()
    )

    task_reference.set(task_data)

    print("\nTask created successfully.")
    print(f"Task ID: {task_reference.id}")


def edit_task(project_id):
    """Edit a task title and completion status."""

    tasks = display_tasks(project_id)

    task = choose_document(tasks, "task")

    if task is None:
        return

    data = task.to_dict()

    current_title = data.get("title", "")
    current_completed = data.get("completed", False)

    current_status = (
        "Completed"
        if current_completed
        else "Pending"
    )

    print_separator()
    print("EDIT TASK")
    print_separator()

    print(f"Current title: {current_title}")
    print(f"Current status: {current_status}")

    new_title = input(
        "\nNew title "
        "(press Enter to keep the current title): "
    ).strip()

    updates = {}

    if new_title:
        updates["title"] = new_title

    if confirm("Change the task completion status?"):
        updates["completed"] = not current_completed

    if not updates:
        print("\nNo changes were made.")
        return

    updates["updated_at"] = firestore.SERVER_TIMESTAMP

    task.reference.update(updates)

    print("\nTask updated successfully.")


def delete_task(project_id):
    """Delete one task from a project."""

    tasks = display_tasks(project_id)

    task = choose_document(tasks, "task")

    if task is None:
        return

    task_data = task.to_dict()
    task_title = task_data.get("title", "Untitled task")

    print(f"\nSelected task: {task_title}")

    if not confirm("Delete this task?"):
        print("Deletion cancelled.")
        return

    task.reference.delete()

    print("\nTask deleted successfully.")


# ---------------------------------------------------------
# Project task menu
# ---------------------------------------------------------

def manage_project_tasks():
    """Open the task menu for a selected project."""

    projects = display_projects()

    project = choose_document(projects, "project")

    if project is None:
        return

    project_id = project.id

    while True:

        # Read the project again in case its data changed
        project_snapshot = (
            db.collection(PROJECTS_COLLECTION)
            .document(project_id)
            .get()
        )

        if not project_snapshot.exists:
            print("\nThe project no longer exists.")
            return

        project_data = project_snapshot.to_dict()
        project_name = project_data.get(
            "name",
            "Unnamed project"
        )

        print_separator()
        print(f"PROJECT: {project_name}")
        print_separator()

        print("1. View tasks")
        print("2. Create task")
        print("3. Edit task")
        print("4. Delete task")
        print("0. Back to main menu")

        option = input("\nSelect an option: ").strip()

        if option == "1":
            display_tasks(project_id)
            pause()

        elif option == "2":
            create_task(project_id)
            pause()

        elif option == "3":
            edit_task(project_id)
            pause()

        elif option == "4":
            delete_task(project_id)
            pause()

        elif option == "0":
            break

        else:
            print("\nInvalid option.")
            pause()


# ---------------------------------------------------------
# Main application menu
# ---------------------------------------------------------

def main():
    """Run the terminal application."""

    while True:

        print_separator()
        print("PROJECT MANAGEMENT SYSTEM")
        print_separator()

        print("1. View projects")
        print("2. Create project")
        print("3. Rename project")
        print("4. Delete project")
        print("5. Manage project tasks")
        print("0. Exit")

        option = input("\nSelect an option: ").strip()

        if option == "1":
            display_projects()
            pause()

        elif option == "2":
            create_project()
            pause()

        elif option == "3":
            rename_project()
            pause()

        elif option == "4":
            delete_project()
            pause()

        elif option == "5":
            manage_project_tasks()

        elif option == "0":
            print("\nApplication closed.")
            break

        else:
            print("\nInvalid option.")
            pause()


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nApplication closed.")

    except Exception as error:
        print(f"\nUnexpected error: {error}")
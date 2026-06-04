# Dataset of 10 real product prompts and 10 edge case prompts
EVALUATION_DATASET = {
    "standard_prompts": [
        {
            "id": "std_1",
            "name": "CRM",
            "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
        },
        {
            "id": "std_2",
            "name": "ERP",
            "prompt": "Create an ERP system with login, inventory tracking, purchase orders, vendor management, and financial reporting. Accountant and Manager roles."
        },
        {
            "id": "std_3",
            "name": "HRMS",
            "prompt": "Build an HRMS with employee profiles, leave request approval workflow, attendance tracking, and admin settings page."
        },
        {
            "id": "std_4",
            "name": "E-Commerce",
            "prompt": "Build an e-commerce platform with customer login, product catalog list page, shopping cart, checkout, payments, and admin product management."
        },
        {
            "id": "std_5",
            "name": "LMS",
            "prompt": "Build a learning management system with teacher and student roles. Students can view courses. Teachers can upload courses and grade quizzes."
        },
        {
            "id": "std_6",
            "name": "Hospital",
            "prompt": "Build a clinic management system with Patient, Doctor, and Receptionist roles. Book appointments, edit medical history, and pay bills."
        },
        {
            "id": "std_7",
            "name": "Inventory",
            "prompt": "Build an inventory manager with warehouses, stock adjustments, stock levels alert, and supplier orders dashboard."
        },
        {
            "id": "std_8",
            "name": "Banking",
            "prompt": "Build a digital banking portal where customers can login, view accounts, transfer money between accounts, and download transaction statements."
        },
        {
            "id": "std_9",
            "name": "SaaS",
            "prompt": "Build a subscription SaaS analytics dashboard that connects to client APIs, displays performance metrics, and gates premium metrics for paid tiers."
        },
        {
            "id": "std_10",
            "name": "Marketplace",
            "prompt": "Build a multi-vendor marketplace where buyers can purchase, and sellers can list items, manage inventory, and withdraw earnings. Admins verify sellers."
        }
    ],
    "edge_cases": [
        {
            "id": "edge_1",
            "name": "Vague Requirements",
            "prompt": "Build a business app."
        },
        {
            "id": "edge_2",
            "name": "Missing Roles",
            "prompt": "Build a contact list where contacts can be created, updated, and deleted, and see audit log metrics. Do not define roles."
        },
        {
            "id": "edge_3",
            "name": "Missing Entities",
            "prompt": "Create a blog application but don't specify where posts, comments, or categories are stored or structured."
        },
        {
            "id": "edge_4",
            "name": "Contradictions",
            "prompt": "Build a CRM where only admins can edit contacts. Users can edit contacts. Manager has no access to contacts but must delete contacts."
        },
        {
            "id": "edge_5",
            "name": "Invalid Feature Requests",
            "prompt": "Build an app that teleports physical items from one office to another using quantum blockchain technology."
        },
        {
            "id": "edge_6",
            "name": "Duplicate Modules",
            "prompt": "Build a system with a contact service, customer details service, user details service, contact service 2, and auth module."
        },
        {
            "id": "edge_7",
            "name": "Partial Requirements",
            "prompt": "Build a system that handles subscription payments."
        },
        {
            "id": "edge_8",
            "name": "Ambiguous Permissions",
            "prompt": "Create a task manager where users can see tasks. Maybe managers can edit them, but not sure, it depends if they are busy."
        },
        {
            "id": "edge_9",
            "name": "Circular Workflows",
            "prompt": "Order requires Manager approval, which triggers Admin validation, which requires Customer signoff, which sends it back to Manager approval."
        },
        {
            "id": "edge_10",
            "name": "Missing Business Rules",
            "prompt": "Build a subscription-based video sharing app where users pay for views. No payment system or price rules specified."
        }
    ]
}

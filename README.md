# Customer Loan Management System

## Project Overview
The **Loan Management System** is a backend application designed to process and manage loans for customers. It allows the creation, viewing, and eligibility checking of loans, as well as viewing loan details by customer and managing loan applications. The system uses **Django**, **PostgreSQL**, and is deployed via **Docker**.

This project features multiple APIs to interact with customer and loan data. It uses a **PostgreSQL** database and exposes the application on port **80**.

## Project Setup and Installation
Follow the steps below to set up and run the project.

### 1. **Clone the Repository**
- Clone the repository to your local machine:
```bash
git clone https://github.com/dhimanparas20/Customer-Loan-Management-System
cd Customer-Loan-Management-System
```

### 2. **Build and Run the Docker Containers**
- Run the following command to build and start the containers:
```bash
sudo docker compose up --build
```

### 3. **Access the Container**
- Once the containers are up, access the shell of the web container:
```bash
sudo docker exec -it <container_id> sh
```

### 4. **Run Migrations**
- Inside the container shell, run the Django migrations to set up the database:
```bash
python3 manage.py migrate
```

### 5. **Create a Superuser**
- Create a superuser to access the Django admin panel:
```bash
python3 manage.py createsuperuser --username admin
```

### 6. **Load Initial Data (Optional)**
- If you need to load some initial data (e.g., from a file like load_data.py), run:
```bash
    python3 load_data.py
```
- Further you need to update alter customer_id sequence 
```bash
    # Outside docker container
    # Step 1: Find the container ID
    sudo docker ps

    # Step 2: Access the container
    sudo docker exec -it <postgress container_id> bash

    # Step 3: Access PostgreSQL CLI
    psql -U <db name>

    # Step 4: Run the ALTER SEQUENCE command
    ALTER SEQUENCE loans_customer_customer_id_seq RESTART WITH 301;

    # Step 5: Exit PostgreSQL CLI
    \q

    # Step 6: Exit the container
    exit

```


### 7. **Exit the Container**
- Exit the container shell:
```bash
exit
```

## Access the Application
Once the setup is complete, the project will be available at:

- Frontend and Admin Panel: http://localhost:80/admin/
- API Endpoints: Accessible via http://localhost:80/api/*

All the API endpoints are accessible, and debug is currently set to True for development purposes.


## API Endpoints

### 1. **/api/register** (POST)
Add a new customer to the customer table with approved limit

#### Request Body:
```json
{
  "first_name": "Paras",
  "last_name": "Dhiman",
  "age": 30,
  "monthly_salary": 24000,
  "phone_number": "9418178848"
}
```
#### Response Body:
```json
{
    "customer_id": 301,
    "name": "Paras Dhiman",
    "age": 30,
    "monthly_income": 24000.0,
    "approved_limit": 900000.0,
    "phone_number": "9418178848"
}
```

### 2. **/api/check-eligibility/** (POST)
This endpoint checks whether a customer is eligible for a loan based on certain conditions.

#### Request Body:
```json
{
  "customer_id": 301,
  "loan_amount": 500000,
  "interest_rate": 8.5,
  "tenure": 24
}
```
#### Response Body:
```json
{
    "customer_id": 300,
    "approval": false,
    "interest_rate": 8.5,
    "corrected_interest_rate": 12.0,
    "tenure": 24,
    "monthly_installment": 0.0
}
```

### 3. **/api/create-loan** (POST)
This endpoint creates a new loan based on eligibility.

#### Request Body:
```json
{
  "customer_id": 255,
  "loan_amount": 500000,
  "interest_rate": 8.5,
  "tenure": 24
}
```
#### Response Body:
```json
{
    "loan_id": 754,
    "customer_id": 255,
    "loan_approved": true,
    "message": "Loan approved successfully.",
    "monthly_installment": 20833.333333333332
}
```

### 4. **/api/view-loan/{loan_id}** (POST)
This endpoint retrieves details of a specific loan.

#### Response Body:
```json
{
    "loan_id": "9997",
    "loan_amount": "500000.00",
    "interest_rate": "8.50",
    "monthly_payment": "20833.33",
    "tenure": 24,
    "customer": {
        "customer_id": 255,
        "first_name": "Annemarie",
        "last_name": "Polo",
        "age": 27,
        "monthly_salary": "250000.00",
        "phone_number": "9166250716",
        "approved_limit": "9000000.00"
    }
}
```

### 5. **/api/view-loans/{customer_id}/** (POST)
This endpoint retrieves all loan details of a specific customer.

#### Response Body:
```json
[
    {
        "loan_id": "9268",
        "loan_amount": "600000.00",
        "interest_rate": "14.34",
        "monthly_payment": "21145.00",
        "tenure": 162,
        "repayments_left": 151
    },
    {
        "loan_id": "6414",
        "loan_amount": "800000.00",
        "interest_rate": "11.51",
        "monthly_payment": "20418.00",
        "tenure": 84,
        "repayments_left": 73
    },
    {
        "loan_id": "4873",
        "loan_amount": "700000.00",
        "interest_rate": "13.75",
        "monthly_payment": "22895.00",
        "tenure": 45,
        "repayments_left": 34
    }
]
```
## Conclusion
You have successfully set up and started the Loan Management System. Feel free to explore the API endpoints and interact with the data as needed!

For any issues or enhancements, feel free to contribute to the repository or raise an issue.
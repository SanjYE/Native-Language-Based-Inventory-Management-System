CREATE DATABASE RestaurantInventoryManagement;
USE RestaurantInventoryManagement;

CREATE TABLE Inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Supplier (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    email VARCHAR(255),
    contact_number VARCHAR(20)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL,
    employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

CREATE TABLE Order_Items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    inventory_id INT,
    quantity_ordered INT NOT NULL,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2) AS (quantity_ordered * unit_price) STORED,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id) ON DELETE SET NULL
);

CREATE TABLE Employee (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_name VARCHAR(255) NOT NULL,
    position VARCHAR(100),
    contact_number VARCHAR(20),
    email VARCHAR(255),
    address VARCHAR(255)
);

CREATE TABLE Customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    contact_number VARCHAR(20),
    email VARCHAR(255),
    -- address VARCHAR(255)
);

CREATE TABLE Sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATE NOT NULL,
    total_amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    customer_id INT,
    employee_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE Reservations (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    reservation_date DATE NOT NULL,
    table_number INT NOT NULL,
    customer_id INT,
    employee_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE Menu (
    menu_item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    availability BOOLEAN DEFAULT TRUE
);

CREATE TABLE Menu_Inventory (
    menu_item_id INT,
    inventory_id INT,
    PRIMARY KEY (menu_item_id, inventory_id),
    FOREIGN KEY (menu_item_id) REFERENCES Menu(menu_item_id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id) ON DELETE CASCADE
);

ALTER TABLE Inventory
ADD COLUMN supplier_id INT,
ADD FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id) ON DELETE SET NULL;

ALTER TABLE Reservations
ADD FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE SET NULL;

ALTER TABLE Orders
ADD FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE SET NULL;

ALTER TABLE Sales
ADD FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE SET NULL;

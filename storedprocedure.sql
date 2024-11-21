use restaurantinventorymanagement;

DROP PROCEDURE IF EXISTS GetHighestSaleEmployee;

DELIMITER //


CREATE PROCEDURE GetHighestSaleEmployee(
    IN start_date DATE, 
    IN end_date DATE
)
BEGIN
    -- Declare variables to store results
    DECLARE max_sale DECIMAL(10, 2);
    DECLARE emp_id INT;
    DECLARE emp_name VARCHAR(255);
    DECLARE emp_position VARCHAR(100);

    -- Find the maximum sale amount and corresponding employee ID
    SELECT 
        employee_id, 
        total_amount
    INTO 
        emp_id, max_sale
    FROM 
        Sales
    WHERE 
        sale_date BETWEEN start_date AND end_date
    ORDER BY 
        total_amount DESC
    LIMIT 1;

    -- Fetch employee details for the highest sale
    SELECT 
        employee_name, 
        position
    INTO 
        emp_name, emp_position
    FROM 
        Employee
    WHERE 
        employee_id = emp_id;

    -- Return the results as a table
    SELECT 
        emp_id AS Employee_ID, 
        emp_name AS Employee_Name, 
        emp_position AS Employee_Position, 
        max_sale AS Highest_Sale_Amount;
END //

DELIMITER ;

use restaurantinventorymanagement;


DELIMITER //

CREATE PROCEDURE GetEmployeeSalesSummary(
    IN emp_id INT, 
    IN start_date DATE, 
    IN end_date DATE
)
BEGIN
    DECLARE total_sales DECIMAL(10,2);
    DECLARE number_of_sales INT;

    -- Calculate total sales for the employee in the given date range
    SELECT SUM(total_amount), COUNT(*)
    INTO total_sales, number_of_sales
    FROM Sales
    WHERE employee_id = emp_id
      AND sale_date BETWEEN start_date AND end_date;

    -- Output the results
    SELECT 
        emp_id AS Employee_ID,
        total_sales AS Total_Sales,
        number_of_sales AS Number_of_Sales;
END //

DELIMITER ;


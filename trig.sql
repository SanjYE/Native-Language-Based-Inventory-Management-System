DELIMITER //

CREATE TRIGGER after_employee_update
AFTER UPDATE ON Employee
FOR EACH ROW
BEGIN
    IF OLD.position <> NEW.position OR OLD.contact_number <> NEW.contact_number THEN
        INSERT INTO Employee_Log (
            employee_id, 
            old_position, 
            new_position, 
            old_contact, 
            new_contact
        )
        VALUES (
            OLD.employee_id, 
            OLD.position, 
            NEW.position, 
            OLD.contact_number, 
            NEW.contact_number
        );
    END IF;
END //

DELIMITER ;

DELIMITER $$

CREATE TRIGGER update_employee_sales
AFTER INSERT ON Sales
FOR EACH ROW
BEGIN
    DECLARE employee_sales DECIMAL(10, 2);
    
    -- Get the current total sales for the employee
    SELECT total_sales INTO employee_sales
    FROM Employee
    WHERE employee_id = NEW.employee_id;
    
    -- Update the total sales for the employee by adding the new sale's total amount
    UPDATE Employee
    SET total_sales = employee_sales + NEW.total_amount
    WHERE employee_id = NEW.employee_id;
END $$

DELIMITER ;

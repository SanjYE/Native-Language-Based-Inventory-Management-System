DELIMITER //

CREATE FUNCTION GetTotalSalesForDay(date_of_sale DATE)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_sales DECIMAL(10,2);

    SELECT SUM(total_amount)
    INTO total_sales
    FROM sales
    WHERE sale_date = date_of_sale;

    RETURN IFNULL(total_sales, 0);
END; //

DELIMITER ;

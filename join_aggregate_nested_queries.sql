SELECT 
    o.order_id, 
    o.order_date, 
    o.total_amount, 
    e.employee_name AS processed_by
FROM 
    Orders o
JOIN 
    Employee e
ON 
    o.employee_id = e.employee_id;


SELECT 
    payment_method, 
    COUNT(*) AS number_of_sales, 
    SUM(total_amount) AS total_sales, 
    AVG(total_amount) AS average_sale
FROM 
    Sales
GROUP BY 
    payment_method;


SELECT 
    c.customer_name, 
    c.contact_number
FROM 
    Customers c
JOIN 
    Sales s
ON 
    c.customer_id = s.customer_id
WHERE 
    s.total_amount > (SELECT AVG(total_amount) FROM Sales);

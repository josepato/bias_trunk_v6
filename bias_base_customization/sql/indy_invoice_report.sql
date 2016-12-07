DROP TYPE IF EXISTS invoice_report_type CASCADE;
CREATE TYPE invoice_report_type AS (
	number 		varchar,
	code 		varchar,
	partner 	varchar,
	date 		varchar,
	sale_order 	varchar,
	payment_term 	varchar,
	box 		numeric,
	free_box 	numeric,
	total_box 	numeric,
	discount 	numeric,
	tax 		numeric,
	total_amount 	numeric
	);
--DROP FUNCTION IF EXISTS getChildren(integer);
CREATE OR REPLACE FUNCTION invoice_report(
	date_start 	date, 
	date_stop 	date,
	group_by	varchar	
	) RETURNS SETOF invoice_report_type AS $$
DECLARE
r1 invoice_report_type%ROWTYPE;
r2 record ;
partner record;
box record;
free_box record;
discount record;
tax record;
subtotal record;
s_group record;
no_user boolean:= False;

BEGIN
    FOR s_group IN SELECT p.user_id, u.name
    FROM account_invoice i LEFT JOIN res_partner p ON (i.partner_id = p.id) LEFT JOIN res_users u ON (p.user_id = u.id)
    WHERE date_invoice BETWEEN date_start AND date_stop AND i.state NOT IN ('draft','cancel') GROUP BY p.user_id, u.name
    LOOP
	IF s_group.user_id IS NULL THEN 
	    no_user := False;
	ELSE
	    no_user := True;
	END IF;
RAISE NOTICE 'Saleman : %,%', s_group, no_user;

	    RETURN QUERY SELECT
		''::varchar,
		''::varchar,
		''::varchar,
		''::varchar,
		''::varchar,
		''::varchar,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric
		;
	    RETURN QUERY SELECT
		''::varchar,
		'VENDEDOR: '::varchar,
		s_group.name,
		''::varchar,
		''::varchar,
		''::varchar,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric,
		NULL::numeric
		;
	
	FOR r2 IN SELECT p.id as partner_id, i.id, i.number, p.ref, p.name, p.user_id, i.date_invoice, i.origin
	FROM account_invoice i LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND date_invoice BETWEEN date_start AND date_stop AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	ORDER BY i.number
	LOOP
	    SELECT name  INTO partner FROM account_payment_term WHERE id = (
	    SELECT trim('account.payment.term,' FROM value) AS term_id
	    FROM ir_property WHERE name = 'property_payment_term'
	    AND trim('res.partner,' FROM res_id) = r2.partner_id::varchar)::integer
	    ;
	    SELECT sum(l.quantity) INTO box FROM account_invoice_line l
	    LEFT JOIN account_invoice i ON (l.invoice_id = i.id)
	    WHERE i.type = 'out_invoice' AND l.price_subtotal <> 0 AND l.uos_id = 12 AND i.id = r2.id
	    ;
	    SELECT sum(l.quantity) INTO free_box FROM account_invoice_line l
	    LEFT JOIN account_invoice i ON (l.invoice_id = i.id)
	    WHERE i.type = 'out_invoice' AND l.price_subtotal = 0 AND l.uos_id = 12 AND i.id = r2.id
	    ;
	    SELECT l.price_subtotal INTO discount FROM account_invoice_line l
	    LEFT JOIN account_invoice i ON (l.invoice_id = i.id)
	    WHERE i.type = 'out_invoice' AND l.uos_id = 25 AND i.id = r2.id
	    ;
	    SELECT SUM(amount) INTO tax FROM account_invoice_tax t
	    LEFT JOIN account_invoice i ON (t.invoice_id = i.id)
	    WHERE i.type = 'out_invoice' AND i.id = r2.id
	    ;
	    SELECT sum(l.price_subtotal) INTO subtotal FROM account_invoice_line l
	    LEFT JOIN account_invoice i ON (l.invoice_id = i.id)
	    WHERE i.type = 'out_invoice' AND i.id = r2.id
	    ;
	    
	    RETURN QUERY SELECT
	    r2.number,
	    r2.ref,
	    r2.name,
	    r2.date_invoice::varchar,
	    r2.origin,
	    partner.name,
	    box.sum::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN 0 ELSE free_box.sum END)::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN box.sum ELSE box.sum + free_box.sum END)::numeric,
	    (SELECT CASE WHEN discount.price_subtotal IS NULL THEN 0 ELSE discount.price_subtotal END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN 0 ELSE tax.sum END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN subtotal.sum ELSE tax.sum + subtotal.sum END)::numeric
	    ;
        END LOOP;
	SELECT sum(l.quantity) INTO box FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.price_subtotal <> 0 AND l.uos_id = 12 AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	;
	SELECT sum(l.quantity) INTO free_box FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.price_subtotal = 0 AND l.uos_id = 12 AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	;
	SELECT SUM(l.price_subtotal) INTO discount FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.uos_id = 25 AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	;
	SELECT SUM(amount) INTO tax FROM account_invoice_tax t
	LEFT JOIN account_invoice i ON (t.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	;
	SELECT sum(l.price_subtotal) INTO subtotal FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND i.state NOT IN ('draft','cancel')
	AND (p.user_id = s_group.user_id OR (no_user = False AND p.user_id IS NULL ))
	;
	RETURN QUERY SELECT
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    'S U M A'::varchar,
	    box.sum::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN 0 ELSE free_box.sum END)::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN box.sum ELSE box.sum + free_box.sum END)::numeric,
	    (SELECT CASE WHEN discount.sum IS NULL THEN 0 ELSE discount.sum END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN 0 ELSE tax.sum END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN subtotal.sum ELSE tax.sum + subtotal.sum END)::numeric
	    ;
    END LOOP;
	SELECT sum(l.quantity) INTO box FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.price_subtotal <> 0 AND l.uos_id = 12 AND i.state NOT IN ('draft','cancel')
	;
	SELECT sum(l.quantity) INTO free_box FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.price_subtotal = 0 AND l.uos_id = 12 AND i.state NOT IN ('draft','cancel')
	;
	SELECT SUM(l.price_subtotal) INTO discount FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND l.uos_id = 25 AND i.state NOT IN ('draft','cancel')
	;
	SELECT SUM(amount) INTO tax FROM account_invoice_tax t
	LEFT JOIN account_invoice i ON (t.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND i.state NOT IN ('draft','cancel')
	;
	SELECT sum(l.price_subtotal) INTO subtotal FROM account_invoice_line l
	LEFT JOIN account_invoice i ON (l.invoice_id = i.id) LEFT JOIN res_partner p ON (i.partner_id = p.id)
	WHERE i.type = 'out_invoice' AND i.state NOT IN ('draft','cancel')
	;
        RETURN QUERY SELECT
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    NULL::numeric,
	    NULL::numeric,
	    NULL::numeric,
	    NULL::numeric,
	    NULL::numeric,
	    NULL::numeric
		;
	RETURN QUERY SELECT
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    ''::varchar,
	    'T O T A L'::varchar,
	    box.sum::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN 0 ELSE free_box.sum END)::numeric,
	    (SELECT CASE WHEN free_box.sum IS NULL THEN box.sum ELSE box.sum + free_box.sum END)::numeric,
	    (SELECT CASE WHEN discount.sum IS NULL THEN 0 ELSE discount.sum END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN 0 ELSE tax.sum END)::numeric,
	    (SELECT CASE WHEN tax.sum IS NULL THEN subtotal.sum ELSE tax.sum + subtotal.sum END)::numeric
	    ;

END
$$ language 'plpgsql';
SELECT * FROM invoice_report('2010-01-01', '2011-01-31','partner');

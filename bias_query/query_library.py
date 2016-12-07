# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import time

#******************************************************************************************
#   Querys Library 
#******************************************************************************************
class query_tool(osv.osv):
    _inherit = 'query.tool'

    _columns = {
    }

    def init(self, cr):
    # MOVE ALL ACCOUNT MOVE LINE FROM ONE PARTNER ID TO OTHER
        cr.execute("""
DROP type IF EXISTS unify_account_partner_type CASCADE;
CREATE TYPE unify_account_partner_type AS (
	lid 	 		integer,
	pid 	 		integer,
	partner			varchar,
	ref 			varchar,
	entry   		varchar	
	); 
        """)

        cr.execute("""
CREATE OR REPLACE FUNCTION unify_account_partner(
	partner_from integer,
	partner_to integer
	) RETURNS SETOF unify_account_partner_type AS $$
DECLARE
 r record ; pay record ;  i integer := 0 ;
BEGIN
    FOR r IN 
	SELECT l.id AS lid, l.move_id AS pid, p.name AS partner, l.ref, m.name AS entry
	FROM account_move_line l
	LEFT JOIN account_move m ON (l.move_id = m.id)
	LEFT JOIN res_partner p ON (l.partner_id = p.id)
	WHERE l.partner_id = partner_from
	LOOP
	    i := i + 1;
		RAISE NOTICE 'count : %,%,%,%,%', i, r.lid, r.partner, r.ref, r.entry;
		UPDATE account_move_line SET partner_id = partner_to WHERE id = r.lid;
		RETURN NEXT r;
	END LOOP;

END
$$ LANGUAGE plpgsql;
        """)

        # CASH FLOW TAX REPORT 

        cr.execute("""
CREATE OR REPLACE FUNCTION get_tax_from_payments6(
    report_type varchar,
    date_start date,
    date_stop date,
    tax varchar,
    order_by varchar) RETURNS SETOF varchar AS $$
DECLARE
    all_accounts integer[] ; 
    all_moves integer[] ; 
    all_total numeric[] := ARRAY[0,0,0,0] ; 
    lid integer := 0 ;
    i integer := 0 ;
    indx integer := 1 ;
    indx_m integer := 1 ;
    doc_count integer := 0 ;
    pay_count integer := 0 ;
    reconcile integer := 0 ;
    r record ;
    r1 record ;
    r2 record ;
    r3 record ;
    r4 record ;
    r5 record ;
    debit numeric ;
    credit numeric ;
    tax_amount numeric ;
    query_type varchar := '' ;
    date_inv varchar := '' ;
    result varchar := '';
    acc_code varchar ;
    entry varchar := '' ;
BEGIN
    IF report_type = 'debit' THEN 
	query_type := ' AND l.debit > 0 ' ;
    ELSIF report_type = 'credit' THEN 
	query_type := ' AND l.credit > 0 ' ;
    END IF;

    FOR r IN EXECUTE 'SELECT id FROM account_account WHERE id IN '||tax
    LOOP
        all_accounts := array_append(all_accounts, r.id) ;
    END LOOP;
    
    indx := 1;
    WHILE all_accounts[indx] > 0
	LOOP
        SELECT code INTO acc_code FROM account_account WHERE id = all_accounts[indx];
        IF result = '' THEN 
	    result := result||'"'||acc_code||'"';
	    all_total[4+indx] := 0 ;
	ELSE
	    result := result||',"'||acc_code||'"';
	    all_total[4+indx] := 0 ;
	END IF;
	indx := indx + 1;
	END LOOP;

    RETURN NEXT '('
		||'"no.",'
		||'"doc_count",'
		||'"date",'
		||'"entry",'
		||'"journal",'
		||'"partner",'
		||'"vat",'
		||'"document",'
		||'"number",'
		||'"reference",'
		||'"date_invoice",'
		||'"account",'
		||'"debit",'
		||'"credit",'
		||'"balance",'
		||'"amount",'
		||result
		||')';

    FOR r IN EXECUTE 'SELECT 
    m.id, 
    SUM(l.debit) AS debit,
    SUM(l.credit) AS credit,
    MIN(l.date) AS date, 
    MIN(a.code) AS account,
    MIN(m.name) AS entry, 
    MIN(j.code) AS journal, 
    CASE WHEN MIN(partner.name) IS NULL THEN '||quote_literal('')||' 
    ELSE replace(MIN(partner.name), '||quote_literal('"')||', '||quote_literal('')||') END AS partner, 
    CASE WHEN MIN(partner.vat) IS NULL THEN '||quote_literal('')||' ELSE
    replace(replace(replace(MIN(partner.vat), '||quote_literal('-')||','||quote_literal('')||'), '
    ||quote_literal(' ')||','||quote_literal('')||'), chr(10),'||quote_literal('')||') END AS vat
    FROM account_move m 
    LEFT JOIN account_journal j ON (m.journal_id = j.id)
    LEFT JOIN account_move_line l ON (l.move_id = m.id)
    LEFT JOIN res_partner partner ON (l.partner_id = partner.id) 
    LEFT JOIN account_account a ON (l.account_id = a.id) 
    LEFT JOIN account_account_type t ON (a.user_type = t.id) 
    WHERE t.code = '||quote_literal('cash')
    ||' AND l.date BETWEEN '||quote_literal(date_start)||' AND '||quote_literal(date_stop)
    --||' and m.id = 990 '
    ||query_type
    ||' GROUP BY m.id'
    ||' ORDER BY '
    ||order_by
    LOOP
	i := i + 1;
	indx_m := 1;
	result := '';
        all_total[1] := all_total[1] + r.debit;
        all_total[2] := all_total[2] + r.credit;
        all_total[3] := all_total[3] + (r.debit - r.credit);

	-- 	Search how much document reconciled whit payment
        all_moves := NULL ;
	FOR r1 IN SELECT distinct(l.move_id) AS move_id 
	    FROM account_move_line l LEFT JOIN account_journal j ON (l.journal_id = j.id)
	    WHERE l.reconcile_id IN (SELECT DISTINCT(reconcile_id) FROM account_move_line WHERE move_id = r.id)
	    AND j.type != 'cash'
	    LOOP
	        all_moves := array_append(all_moves, r1.move_id) ;
	    END LOOP;

	doc_count := array_upper(all_moves,1);

	IF doc_count IS NULL THEN
 	    indx := 1 ;
   	    WHILE all_accounts[indx] > 0
	    LOOP
		SELECT CASE WHEN SUM(l.debit) - SUM(l.credit) IS NULL THEN 0
		ELSE SUM(l.debit) - SUM(l.credit) END INTO tax_amount
		FROM account_move_line l WHERE move_id = r.id AND account_id = all_accounts[indx];
		IF result = '' THEN result := result||tax_amount; ELSE result := result||','||tax_amount; END IF;
		all_total[4+indx] := all_total[4+indx] + tax_amount;
		indx := indx + 1;
	    END LOOP;
		
	    RETURN NEXT '('
		||i||','
		||'0'||','
		||'"'||r.date||'",'
		||'"'||r.entry||'",'
		||'"'||r.journal||'",'
		||'"'||r.partner||'",'
		||'"'||r.vat||'",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"'||r.account||'",'
		||r.debit||','
		||r.credit||','
		||r.debit-r.credit||','
		||'"",'
		||result
		||')';

	ELSE	
	    indx_m := 1;
	    WHILE all_moves[indx_m] > 0
	    LOOP
		SELECT number, reference INTO r3 FROM account_invoice WHERE move_id = all_moves[indx_m];

		SELECT m.name, MIN(m.date) AS date,
		CASE WHEN SUM(l.debit)-SUM(l.credit) IS NULL THEN 0 ELSE SUM(l.debit)-SUM(l.credit) END AS amount
		INTO r5 FROM account_move_line l LEFT JOIN account_account a ON (l.account_id = a.id)
		LEFT JOIN account_move m ON (l.move_id = m.id)
		WHERE move_id = all_moves[indx_m] AND a.type in ('payable','receivable') GROUP BY m.name;

		indx := 1;
		WHILE all_accounts[indx] > 0
		LOOP
		    SELECT CASE WHEN SUM(l.debit) - SUM(l.credit) IS NULL THEN 0
		    ELSE SUM(l.debit) - SUM(l.credit) END INTO tax_amount
		    FROM account_move_line l WHERE move_id = all_moves[indx_m] AND account_id = all_accounts[indx];

		    IF result = '' THEN result := result||tax_amount; ELSE result := result||','||tax_amount; END IF;
		    all_total[4+indx] := all_total[4+indx] + tax_amount;
		    indx := indx + 1;
		END LOOP;    

		all_total[4] := all_total[4] + r5.amount;

	        indx := 1;
		IF indx_m = 1 THEN
		    RETURN NEXT '('
		||i||','
		||doc_count||','
		||'"'||r.date||'",'
		||'"'||r.entry||'",'
		||'"'||r.journal||'",'
		||'"'||r.partner||'",'
		||'"'||r.vat||'",'
		||'"'||r5.name||'",'
		||'"'||r3.number||'",'
		||'"'||r3.reference||'",'
		||'"'||r5.date||'",'
		||'"'||r.account||'",'
		||r.debit||','
		||r.credit||','
		||r.debit-r.credit||','
		||r5.amount||','
		||result
		||')';
		ELSE
		    RETURN NEXT '('
		||i||','
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"'||r5.name||'",'
		||'"",'
		||'"",'
		||'"'||r5.date||'",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||r5.amount||','
		||result
		||')';
		END IF;
		result := '';
		indx_m := indx_m + 1;
		
	    END LOOP;    
	END IF;
    END LOOP;
        result := '';
        indx := 1;
        WHILE all_accounts[indx] > 0
	LOOP
        IF result = '' THEN 
	    result := result||''||all_total[4+indx]||'';
	ELSE
	    result := result||','||all_total[4+indx]||'';
	END IF;
	indx := indx + 1;
	END LOOP;

--RAISE NOTICE 'result : %,%', all_total,result ;

	RETURN NEXT '('
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"",'
		||'"TOTAL",'
		||all_total[1]||','
		||all_total[2]||','
		||all_total[3]||','
		||all_total[4]||',' 
		||result
		||')';
   
END
$$ LANGUAGE plpgsql;
        """)

query_tool()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


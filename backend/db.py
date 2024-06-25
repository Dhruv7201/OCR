import psycopg2



conn = psycopg2.connect(database = "zota",
                        user = "tableau",
                        host= '27.109.26.202',
                        password = "ta372mogt9",
                        port = 5432)


if conn:
    query = """
SELECT 
    tmpl.name AS product_name,
    tmpl.default_code AS product_code,
    lot.name AS lot_name,
    lot.mrp AS mrp,
    lot.mfg_date AS mfg_date,
    lot.exp_date AS exp_date
FROM 
    stock_production_lot AS lot
LEFT JOIN 
    product_product AS prod ON prod.id = lot.product_id
LEFT JOIN
	product_template AS tmpl ON tmpl.id = prod.product_tmpl_id;
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    print(len(rows))
    # for row in rows:
    #     print(row)
    conn.close()
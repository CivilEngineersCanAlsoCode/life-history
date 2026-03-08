--liquibase formatted sql


--changeset author:rdube26:insert_ira_sect
INSERT INTO ira_sect (gate_type_cd, ira_sect_cd,sect_ord_no, sect_nm)
VALUES
    ('ACR', 'AD', 1, 'Default'),
    ('GR', 'GD', 1, 'Default'),
    ('IR', 'ID', 1, 'Default'),
    ('OCCP', 'OCCP', 1, 'Default'),
    ('SR', 'SD', 1, 'Default'),
    ('PRR', 'ANYM', 2, 'Anonymity'),
    ('PRR', 'CBTV', 5, 'Cross-border Transfer of Value'),
    ('PRR', 'COCE', 1, 'Cash or cash equivalent'),
    ('PRR', 'DQ', 7, 'Data quality (the quality of customer and transaction data available)'),
    ('PRR', 'LTOV', 4, 'Large transfer of value'),
    ('PRR', 'RTOV', 3, 'Rapid Transfer of Value'),
    ('PRR', 'UBTP', 6, 'Use by third parties');
